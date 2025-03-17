from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import mysqlweight  # database connection module
import time  # Add this for the sleep function in retry logic
import mysql.connector
import os

app = Flask(__name__)

sessions_data = [
    {
        "id": "1619874477.123456",
        "direction": "in",
        "bruto": 1000,
        "neto": "na",
        "produce": "orange",
        "containers": ["str1", "str2"]
    },
    {
        "id": "1619874487.234567",
        "direction": "out",
        "bruto": 1500,
        "neto": 1000,
        "produce": "tomato",
        "containers": ["str3"]
    },
    {
        "id": "1619874497.345678",
        "direction": "none",
        "bruto": 800,
        "neto": "na",
        "produce": "na",
        "containers": []
    }
]

items_data = {
    "truck1": {
        "tara": 800,
        "sessions": ["1619874477.123456", "1619874487.234567"]
    },
    "container1": {
        "tara": "na",
        "sessions": ["1619874497.345678"]
    }
}


# @app.route("/", methods=["GET"])
# def home():
#     return render_template("index.html")

# http://localhost:5000/health
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"OK": "app running."}), 200

# New weight transaction endpoint
@app.route("/weight", methods=["POST"])
def record_weight_transaction():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['direction', 'truck']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create database connection using your existing module
        connection = create_connection_with_retry()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Handle different directions
        if data['direction'].lower() == 'in':
            # Truck is entering - create new transaction
            return handle_truck_entry(cursor, connection, data)
        elif data['direction'].lower() == 'out':
            # Truck is leaving - update or create transaction
            return handle_truck_exit(cursor, connection, data)
        else:
            return jsonify({"error": "Invalid direction. Must be 'in' or 'out'"}), 400
            
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

def handle_truck_entry(cursor, connection, data):
    try:
        # Prepare data for new transaction
        now = datetime.now()
        
        # Convert containers list to JSON string if present
        containers_json = json.dumps(data.get('containers', [])) if 'containers' in data else None
        
        # Insert new transaction
        query = """
        INSERT INTO transactions 
        (datetime, direction, truck, containers, bruto, produce) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        values = (
            now,
            data['direction'],
            data['truck'],
            containers_json,
            data.get('bruto'),
            data.get('produce')
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        # Get the ID of the newly created transaction
        transaction_id = cursor.lastrowid
        
        # Prepare and return response
        response = {
            "id": transaction_id,
            "truck": data['truck'],
            "bruto": data.get('bruto'),
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

def handle_truck_exit(cursor, connection, data):
    try:
        # Find the most recent entry for this truck
        find_entry_query = """
        SELECT id, containers, bruto 
        FROM transactions 
        WHERE truck = %s AND direction = 'in' 
        ORDER BY datetime DESC 
        LIMIT 1
        """
        
        cursor.execute(find_entry_query, (data['truck'],))
        entry_record = cursor.fetchone()
        
        if not entry_record:
            return jsonify({"error": f"No entry record found for truck {data['truck']}"}), 404
        
        # Get truck tara weight
        truck_tara = data.get('truckTara')
        if not truck_tara:
            return jsonify({"error": "Missing truckTara weight for exit transaction"}), 400
        
        # Calculate neto weight based on containers
        neto = None
        containers_json = data.get('containers')
        
        if containers_json:
            containers = json.loads(containers_json) if isinstance(containers_json, str) else containers_json
            
            # Check if we have weights for all containers
            all_containers_known = True
            containers_weight = 0
            
            for container_id in containers:
                # Get container weight from database
                container_query = "SELECT weight FROM containers_registered WHERE container_id = %s"
                cursor.execute(container_query, (container_id,))
                container = cursor.fetchone()
                
                if not container:
                    all_containers_known = False
                    break
                
                containers_weight += container['weight']
            
            # Calculate neto if all containers are known
            if all_containers_known:
                neto = data.get('bruto') - truck_tara - containers_weight
            else:
                neto = "na"  # As specified in your schema comment
        else:
            # If no containers specified, just use bruto minus truckTara
            neto = data.get('bruto') - truck_tara
        
        # Create a new record for the exit transaction
        now = datetime.now()
        
        # Convert containers list to JSON string if present
        containers_json = json.dumps(data.get('containers', [])) if 'containers' in data else None
        
        # Insert the exit record
        query = """
        INSERT INTO transactions 
        (datetime, direction, truck, containers, bruto, truckTara, neto) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            now,
            data['direction'],
            data['truck'],
            containers_json,
            data.get('bruto'),
            truck_tara,
            neto if neto != "na" else None  # Store as NULL in database if "na"
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        # Get the ID of the exit transaction
        transaction_id = cursor.lastrowid
        
        # Prepare and return response
        response = {
            "id": transaction_id,
            "truck": data['truck'],
            "bruto": data.get('bruto'),
            "truckTara": truck_tara,
            "neto": neto,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


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

# http://localhost:5000/item/truck1?from=20230301000000&to=20230302235959
@app.route("/item/<id>", methods=["GET"])
def get_item(id):
    from_param = request.args.get('from', default="20230301000000")
    to_param = request.args.get('to', default=str(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S')))

    try:
        t1 = datetime.datetime.strptime(from_param, '%Y%m%d%H%M%S')
        t2 = datetime.datetime.strptime(to_param, '%Y%m%d%H%M%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected format: yyyymmddhhmmss"}), 400

    if id not in items_data:
        return jsonify({"error": "Item not found"}), 404

    item_data = items_data[id]
    return jsonify({
        "id": id,
        "tara": item_data["tara"],
        "sessions": item_data["sessions"]
    }), 200

# http://localhost:5000/session/1619874477.123456


@app.route("/session/<id>", methods=["GET"])
def get_session(id):
    session = next((item for item in sessions_data if item['id'] == id), None)

    if not session:
        return jsonify({"error": "Session not found"}), 404

    response = {
        "id": session["id"],
        "direction": session["direction"],
        "bruto": session["bruto"],
    }

    if session["direction"] == "out":
        response["truckTara"] = 1000
        response["neto"] = session["neto"] if session["neto"] != "na" else "na"

    return jsonify(response), 200


@app.route("/api/weight", methods=["GET","POST"])
def weight():

    # Get:/api/weight?from=t1&to=t2&filter=in,out,none
    if request.method == "GET":

        # Get the current date and time
        now = datetime.now()

        # Get parameters from the URL
        paramFrom = request.args.get("from", now.strftime("%Y%m%d000000"))
        paramTo = request.args.get("to", now.strftime("%Y%m%d%H%M%S"))

        # Convert paramFrom and paramTo to MySQL DATETIME format
        paramFromFormatted = datetime.strptime(paramFrom, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        paramToFormatted = datetime.strptime(paramTo, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

        paramFilter = request.args.get("filter","in,out,none")

        return jsonify({
            "from":paramFromFormatted,
            "to":paramToFormatted,
            "filter":paramFilter}), 200

        filterList = tuple(paramFilter.split(","))

        try:
            connection = connect()
            cursor = connection.cursor(dictionary=True)  # Enables fetching rows as dictionaries
            
            query = """
                SELECT id, truck, bruto, truckTara, neto
                FROM transactions
                WHERE direction IN ({})
                AND datetime BETWEEN %s AND %s
            """.format(",".join(["%s"] * len(filterList)))
            

            # SQL Query to fetch required columns
            cursor.execute(query, (*filterList, paramFromFormatted, paramToFormatted))
            transactions = cursor.fetchall()

            cursor.close()
            connection.close()

            return jsonify(transactions), 200

        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500
            

    elif request.method == "POST":
        return jsonify({"not implemented"}), 201

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0", port="5001")
