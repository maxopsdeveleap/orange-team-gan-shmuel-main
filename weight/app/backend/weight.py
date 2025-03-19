from flask import Flask, render_template, request, jsonify
from datetime import datetime
import mysqlweight
import time
import mysql.connector
import os
import csv
import json
import time

app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return render_template("index.html")


def handle_weight_in(cursor, connection, data, direction, truck, containers):
    # Check for existing recent transaction for this truck/direction
    existing_in_query = """
        SELECT t1.id, t1.session
        FROM transactions t1
        LEFT JOIN (
            SELECT truck, MAX(datetime) as latest_out_time
            FROM transactions
            WHERE truck = %s AND direction = 'out'
            GROUP BY truck
        ) t2 ON t1.truck = t2.truck
        WHERE t1.truck = %s AND t1.direction = 'in'
            AND (t2.latest_out_time IS NULL OR t1.datetime > t2.latest_out_time)
        ORDER BY t1.datetime DESC
        LIMIT 1
    """
    cursor.execute(existing_in_query, (truck, truck))
    existing_entry = cursor.fetchone()

    # Handle force flag for repeated transactions
    force = data.get('force', False)
    if existing_entry and not force:
        return jsonify({"error": "Transaction already exists. Use force=true to overwrite."}), 400

    # Prepare transaction data
    now = datetime.now()
    weight = data['weight']
    unit = data['unit']
    produce = data.get('produce', 'na')

    # set up the last session id to maintaine continues
    if existing_entry and force:
        # If overriding an existing entry, use its session ID
        session_id = existing_entry['session']
        # Delete the existing entry if force=true
        delete_query = "DELETE FROM transactions WHERE id = %s"
        cursor.execute(delete_query, (existing_entry['id'],))
    else:
        # Get a new session ID
        cursor.execute("SELECT MAX(session) as max_session FROM transactions")
        session_result = cursor.fetchone()
        if session_result is None or session_result['max_session'] is None:
            session_id = 1
        else:
            session_id = session_result['max_session'] + 1

    # Handle different scenarios
    # Insert truck transaction
    if truck != 'na':
        query = """
            INSERT INTO transactions
            (datetime, direction, truck, containers, bruto, produce, session)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (now, direction, truck,
                  json.dumps(containers.split(',')) if containers else None,
                  weight, produce, session_id)
        cursor.execute(query, values)
        transaction_id = cursor.lastrowid

    # Handle container registration logic for 'none' direction
    elif direction == 'none':
        if not containers:
            return jsonify({"error": "No containers specified for 'none' direction"}), 400

        containers_list = containers.split(',')
        for container in containers_list:
            container_query = """
                INSERT INTO containers_registered
                (container_id, weight, unit)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE weight = %s, unit = %s
            """
            cursor.execute(container_query, (container,
                           weight, unit, weight, unit))
        transaction_id = None  # No truck transaction

    connection.commit()

    # Prepare response
    response = {
        "id": transaction_id,
        "truck": truck,
        "bruto": weight,
        "session": session_id
    }

    return jsonify(response), 201


def handle_weight_out(cursor, connection, data, truck):
    # Validate truck and containers
    if truck == 'na':
        return jsonify({"error": "Must specify either truck "}), 400

    # Find the most recent entry for this truck
    find_entry_query = """
    SELECT id, truck, bruto, session, containers, produce
    FROM transactions
    WHERE truck = %s AND direction = 'in'
    ORDER BY datetime DESC
    LIMIT 1
    """
    cursor.execute(find_entry_query, (truck,))
    entry_record = cursor.fetchone()
    containers = json.loads(entry_record['containers'])

    # Validate entry record exists
    if truck != 'na' and not entry_record:
        return jsonify({"error": f"No entry record found for truck {truck}"}), 404

    # Calculate container weights
    total_container_tara = 0
    if containers:
        for container in containers:
            # Fetch container weight from registered containers
            container_query = "SELECT weight FROM containers_registered WHERE container_id = %s"
            cursor.execute(container_query, (container,))
            container_record = cursor.fetchone()

            if not container_record:
                total_container_tara = None
                break
            total_container_tara += container_record['weight']

    # Prepare out transaction
    now = datetime.now()
    out_weight = data['weight']

    # Calculate neto
    if truck != 'na':
        # Use current out_weight as truck tara
        truck_tara = out_weight

        # Use previous entry's bruto as the entry weight
        entry_bruto = entry_record['bruto']

        # Calculate neto
        neto = "na"
        if total_container_tara is not None:
            neto = entry_bruto - truck_tara - total_container_tara

        # Insert out transaction
        query = """
        INSERT INTO transactions
        (datetime, direction, truck, bruto,
         truckTara, neto, containers, produce, session)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            now,
            'out',
            truck,
            entry_bruto,
            truck_tara,  # truck tara from current out weight
            neto if neto != "na" else None,
            json.dumps(containers) if containers else None,
            # include produce, defaulting to 'na'
            entry_record.get('produce', 'na'),
            entry_record['session']
        )
        cursor.execute(query, values)
        transaction_id = cursor.lastrowid

        # Prepare response
        response = {
            "id": transaction_id,
            "truck": truck,
            "bruto": entry_bruto,
            "truckTara": truck_tara,
            "neto": neto
        }
    else:
        # Handle standalone container out transaction
        response = {
            "truck": "na",
            "bruto": out_weight
        }

    connection.commit()
    return jsonify(response), 201


def create_connection_with_retry(max_retries=3, retry_delay=2):
    """Attempt to connect to the database with retries"""
    retries = 0
    last_error = None

    while retries < max_retries:
        try:
            connection = mysqlweight.connect()
            if connection:
                return connection
        except Exception as e:
            last_error = e
            print(f"Connection attempt {retries + 1} failed: {e}")
            retries += 1
            time.sleep(retry_delay)

    # If we get here, all retries failed
    print(f"All {max_retries} connection attempts failed. Last error: {last_error}")
    return None


def convert_to_kg(weight, unit="lbs"):
    if unit.lower() == "lbs":
        return weight * 0.453592
    return weight


@app.route("/health", methods=["GET"])
def health():
    try:
        mysqlweight.connect()
        return 'OK', 200
    except:
        return 'Failure', 500


@app.route("/weight", methods=["GET"])
def weight():
    # Get the current date and time
    now = datetime.now()

    # Get parameters from the URL
    paramFrom = request.args.get("from", now.strftime("%Y%m%d000000"))
    paramTo = request.args.get("to", now.strftime("%Y%m%d%H%M%S"))

    # Convert paramFrom and paramTo to MySQL DATETIME format
    paramFromFormatted = datetime.strptime(
        paramFrom, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    paramToFormatted = datetime.strptime(
        paramTo, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

    paramFilter = request.args.get("filter", "in,out,none")

    filterList = tuple(paramFilter.split(","))

    try:
        connection = mysqlweight.connect()
        # Enables fetching rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        query = """
                SELECT id, direction, bruto, neto, produce, containers
                FROM transactions
                WHERE direction IN ({})
                AND datetime BETWEEN %s AND %s
            """.format(",".join(["%s"] * len(filterList)))

        # SQL Query to fetch required columns
        cursor.execute(
            query, (*filterList, paramFromFormatted, paramToFormatted))
        transactions = cursor.fetchall()

        # Convert `containers` column from string to list
        for transaction in transactions:
            if transaction["containers"]:  # Ensure it's not None
                transaction["containers"] = json.loads(
                    transaction["containers"])

        cursor.close()
        connection.close()

        return jsonify(transactions), 200

    except mysql.connector.Error as err:
        return jsonify({"error xx": str(err)}), 500


@app.route("/item/<id>", methods=["GET"])
def get_item(id):

    # Get the current date and time
    now = datetime.now()

    paramFrom = request.args.get("from", now.strftime("%Y%m01000000"))
    paramTo = request.args.get('to', now.strftime('%Y%m%d%H%M%S'))

    # Convert paramFrom and paramTo to MySQL DATETIME format
    try:
        paramFromFormatted = datetime.strptime(
            paramFrom, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        paramToFormatted = datetime.strptime(
            paramTo, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected format: yyyymmddhhmmss"}), 400

    connection = mysqlweight.connect()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT * FROM transactions 
        WHERE truck = %s 
        OR JSON_CONTAINS(containers, JSON_QUOTE(%s))
    """

    cursor.execute(query, (id, id))
    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    if not transactions:
        return jsonify({"error": "No transactions found"}), 404

    sessions = set()
    tara = "na"

    for record in transactions:
        sessions.add(record["session"])
        if record["truckTara"]:
            tara = record["truckTara"]

    return jsonify({
        "id": id,
        "tara": tara,
        "sessions": list(sessions)
    }), 200


@app.route("/session/<id>", methods=["GET"])
def get_session(id):
    try:
        # Connect to database
        connection = create_connection_with_retry()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        # Query to get session data
        session_query = """
            SELECT id, truck, direction, bruto, truckTara, neto
            FROM transactions
            WHERE session = %s
            ORDER BY datetime
        """

        cursor.execute(session_query, (id,))
        session_records = cursor.fetchall()

        # Check if session exists
        if not session_records:
            return jsonify({"error": "Session not found"}), 404

        # Process the results
        # For simplicity, we'll use the first record for general info
        first_record = session_records[0]

        # Prepare the base response
        response = {
            "id": id,
            "truck": first_record["truck"] if first_record["truck"] else "na",
            "bruto": first_record["bruto"]
        }

        # Add OUT-specific fields if applicable
        out_record = next(
            (record for record in session_records if record["direction"] == "out"), None)
        if out_record:
            response["truckTara"] = out_record["truckTara"]
            response["neto"] = out_record["neto"] if out_record["neto"] is not None else "na"

        cursor.close()
        connection.close()

        return jsonify(response), 200

    except Exception as e:
        print(f"Error retrieving session: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/unknown", methods=["GET"])
def unknown():
    try:
        connection = mysqlweight.connect()
        # Enables fetching rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT direction, neto, containers
            FROM transactions
            WHERE direction = %s AND neto IS %s 
        """

        # SQL Query to fetch required columns

        cursor.execute(query, ("out", None))
        transactions = cursor.fetchall()

        container_ids = set()

        for transaction in transactions:
            for container in json.loads(transaction["containers"]):
                container_ids.add(container)

        # return jsonify({"len": len(container_ids)}), 200

        query = f"""
            SELECT container_id 
            FROM ({" UNION ALL ".join(["SELECT %s AS container_id"] * len(container_ids))}) AS input_list
            WHERE container_id NOT IN (SELECT container_id FROM containers_registered);
        """

        cursor.execute(query, list(container_ids))

        missing_ids = [row["container_id"] for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        return jsonify(missing_ids), 200

    except mysql.connector.Error as err:
        return jsonify({"error xx": str(err)}), 500


@app.route("/weight", methods=["POST"])
def record_weight_transaction():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Validate required fields
        required_fields = ['direction', 'weight', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Normalize inputs
        direction = data['direction'].lower()
        truck = data.get('truck', 'na')
        # containers = data.get('containers', '').split(
        #     ',') if data.get('containers') else []
        containers = data.get('containers', None)

        # Validate direction
        valid_directions = ['in', 'out', 'none']
        if direction not in valid_directions:
            return jsonify({"error": "Invalid direction. Must be 'in', 'out', or 'none'"}), 400

        # Create database connection
        connection = create_connection_with_retry()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        try:
            # Handle different scenarios based on direction
            if direction in ['in', 'none']:
                return handle_weight_in(cursor, connection, data, direction, truck, containers)
            elif direction == 'out':
                return handle_weight_out(cursor, connection, data, truck)

        except Exception as e:
            connection.rollback()
            print(f"Error processing transaction: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/batch-weight", methods=["POST"])
def batch_weight():
    upload_folder = "./in"

    file_name = request.get_json().get("file")
    file_path = os.path.join(upload_folder, file_name)

    containers = []

    if os.path.isfile(file_path):
        if file_name.endswith('.csv'):
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                unit = "kg" if "kg" in header[1].lower() else "lbs"
                for row in reader:
                    if len(row) == 2:
                        container_id, weight = row
                        containers.append(
                            (container_id, weight, unit))

        elif file_name.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                for entry in data:
                    containers.append(
                        (entry["id"], int(entry["weight"]), entry["unit"]))

        else:
            return jsonify({"error": f"Unsupported file format: {file_name}"}), 400

    if not containers:
        return jsonify({"error": "No valid files found"}), 400

    connection = create_connection_with_retry()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    query = "INSERT INTO containers_registered (container_id, weight, unit) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE weight=VALUES(weight), unit=VALUES(unit)"
    cursor.executemany(query, containers)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Batch weight uploaded successfully", "count": len(containers)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0", port="5001")
