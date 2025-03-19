from flask import Flask, request, jsonify, send_file, render_template
from mysqlbilling import connect
import requests
from datetime import datetime
import logging
import os
import pandas as pd


app = Flask(__name__)


RATES_FOLDER= os.path.abspath(os.path.join(os.path.dirname(__file__), "..","in"))
app.config["RATES_FOLDER_PATH"] = RATES_FOLDER


@app.route('/health', methods=['GET'])
def health_check():
        try:
            connect()
            return 'OK', 200
        except:
            return 'Failure', 500

@app.route('/provider', methods=['POST'])
def create_provider():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Provider name is required"}), 400
    
    provider_name = data['name']

    connection = connect()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id FROM Provider WHERE name = %s", (provider_name,))
        existing_provider = cursor.fetchone()
        
        if existing_provider:
             return jsonify({"error": "Provider name must be unique"}), 409

        cursor.execute("INSERT INTO Provider (name) VALUES (%s)", (provider_name,))
        connection.commit()

        provider_id = cursor.lastrowid
        return jsonify({"id": str(provider_id)}), 201
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
         cursor.close()
         connection.close()


@app.route('/provider/<string:provider_id>', methods=['PUT'])
def update_provider(provider_id):   
    try:
        provider_id = int(provider_id)  # Ensure it's an integer
    except ValueError:
        return jsonify({"error": "Invalid provider ID - ID requires numbers only"}), 400  # Return a 400 Bad Request if it's not a valid integer

    data = request.get_json()

    # Input validation
    if not data or 'name' not in data:
        return jsonify({"error": "Provider name is required"}), 400

    new_name = data['name']

    connection = connect()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id FROM Provider WHERE id = %s", (provider_id,))
        existing_provider = cursor.fetchone()
        
        if not existing_provider:
            return jsonify({"error": "Provider not found"}), 404

        # Check if the new name is unique (excluding the current provider)
        cursor.execute("SELECT id FROM Provider WHERE name = %s AND id != %s", (new_name, provider_id))
        duplicate_provider = cursor.fetchone()
        
        if duplicate_provider:
            return jsonify({"error": "Provider name must be unique"}), 409

        # Update the provider's name
        cursor.execute("UPDATE Provider SET name = %s WHERE id = %s", (new_name, provider_id))
        connection.commit()

        return jsonify({"message": "Provider updated successfully"}), 200

    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error updating provider: {e}")
        return jsonify({"error": "Failed to update provider"}), 500

    finally:
        cursor.close()
        connection.close()


@app.route('/truck/<id>', methods=['PUT'])
def update_truck(id):
   data = request.get_json()
   if not data or "provider_id" not in data:
       return jsonify({"error": "Provider ID is required"}), 400
   new_provider_id = data["provider_id"]
   
   connection = connect()
   cursor = connection.cursor()

   try:
       cursor.execute("SELECT id FROM Trucks WHERE id = %s", (id,))
       if not cursor.fetchone():
           return jsonify({"error": "No matching truck found"}),404
       cursor.execute("SELECT id FROM Provider WHERE id = %s", (new_provider_id,))
       if not cursor.fetchone():
           return jsonify({"error": "Invalid provider ID"}), 400
       
       cursor.execute("UPDATE Trucks SET provider_id = %s WHERE id = %s", (new_provider_id, id))
       connection.commit()

       return jsonify({"message": "Truck updated successfully"}), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500
   finally:
       cursor.close()
       connection.close()


@app.route('/rates', methods=['GET'])
def get_rates():
    try:
        RATES_DIRECTORY = "/in"
        # Define the path to the rates file
        rates_file_path = os.path.join(RATES_DIRECTORY, "rates.xlsx")

        # Check if the file exists
        if not os.path.exists(rates_file_path):
            return jsonify({"error": "Rates file not found"}), 404

        # Send file
        return send_file(rates_file_path, as_attachment=True, download_name="rates.xlsx")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rates', methods=['POST'])
def add_rates():
    if "file" not in request.files:
        return jsonify({"error": "Invalid request, file required"}), 400
    
    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Filename is required, currently empty"}), 400
    
    if not file.filename.endswith("xlsx"):
        return jsonify({"error": "File must be excel. '.xlsx'"}), 400

    file_path = os.path.join(app.config["RATES_FOLDER_PATH"], file.filename)
    file.save(file_path)

    dataframe = pd.read_excel(file_path)

    required_columns = {"Product", "Rate", "Scope"}

    if not required_columns.issubset(dataframe.columns):
        return jsonify({"error": "Missing required names"}), 400

    if dataframe.empty:
        return jsonify({"error": "Excel file is empty of rows"}), 400

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Rates")

    try:
        for i, row in dataframe.iterrows():
            product = row["Product"]
            rate = row["Rate"]
            scope = row["Scope"]

            if scope == "All":
                provider_id = ""
            else:
                provider_id = scope
            
            if provider_id:
                cursor.execute("SELECT id FROM Provider WHERE id = %s", (provider_id,))
                if not cursor.fetchone():
                     continue
                else:
                    cursor.execute("""
                    INSERT INTO Rates (product_id, rate, scope)
                    VALUES (%s, %s, %s)
                    """, (product, rate, provider_id))
            else:
                cursor.execute("""
                INSERT INTO Rates (product_id, rate, scope)
                VALUES (%s, %s, %s)
                """, (product, rate, scope))
        connection.commit()
        return jsonify({"message": "Row added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# POST /truck - Register a truck
@app.route('/truck', methods=['POST'])
def register_truck():
    # Get JSON data from the request
    data = request.get_json()

    # Validate input
    if not data or 'provider_id' not in data or 'id' not in data:
        return jsonify({"error": "Missing required fields: 'provider_id' and 'id'"}), 400

    provider_id = data['provider_id']  # Provider's ID
    license_number = data['id']  # Truck's license plate (id)

    connection = None
    cursor = None

    try:
        # Establish a database connection
        connection = connect()
        cursor = connection.cursor()

        # Check if the provider exists
        cursor.execute("SELECT id FROM Provider WHERE id = %s", (provider_id,))
        provider = cursor.fetchone()

        if not provider:
            return jsonify({"error": "Provider not found"}), 404

        # Check if the truck already exists
        cursor.execute("SELECT * FROM Trucks WHERE id = %s", (license_number,))
        existing_truck = cursor.fetchone()

        if existing_truck:
            return jsonify({"error": "Truck already exists"}), 409

        # Insert the truck into the database
        cursor.execute("INSERT INTO Trucks (id, provider_id) VALUES (%s, %s)", (license_number, provider_id))
        connection.commit()

        # Return success response
        return jsonify({"message": "Truck registered successfully", "id": license_number}), 201

    except Exception as e:
        print(f"Error updating provider: {e}")
        return jsonify({"error": f"Failed to update provider: {str(e)}"}), 500

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/truck/<id>', methods=['GET'])
def get_truck_info(id):

    logger.info(f"Getting information for truck: {id}")

    # Get query parameters with defaults
    from_date = request.args.get('from', None)
    to_date = request.args.get('to', None)

    # Set default values if not provided
    now = datetime.now()
    if not from_date:
        # Default is 1st of current month at 000000
        from_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H%M%S")
        logger.info(f"Using default from_date: {from_date}")

    if not to_date:
        # Default is now
        to_date = now.strftime("%Y%m%d%H%M%S")
        logger.info(f"Using default to_date: {to_date}")

    try:
        # Validate the date format
        datetime.strptime(from_date, "%Y%m%d%H%M%S")
        datetime.strptime(to_date, "%Y%m%d%H%M%S")
    except ValueError:
        logger.error(f"Invalid date format: from_date={from_date}, to_date={to_date}")
        return jsonify({"error": "Invalid date format. Use yyyymmddhhmmss"}), 400

    try:
        # Production API URL (configurable via environment variable)
        production_api_url = os.getenv("PRODUCTION_API_URL", "http://weight_app:5001/truck")
        logger.info(f"Calling production API for truck {id} from {from_date} to {to_date}")

        # Make a request to the production API
        response = requests.get(
            f"{production_api_url}/{id}",
            params={"from": from_date, "to": to_date},
            timeout=int(os.getenv("REQUEST_TIMEOUT", "10"))  # Configurable timeout
        )

        # Handle response from production API
        if response.status_code == 404:
            logger.warning(f"Truck {id} not found in production database")
            return jsonify({"error": "Truck not found"}), 404

        if response.status_code != 200:
            logger.error(f"Production API error: {response.status_code} - {response.text}")
            return jsonify({"error": "Error retrieving truck information from production"}), 502

        # Validate the response from the production API
        truck_data = response.json()
        if not all(key in truck_data for key in ["id", "tara", "sessions"]):
            logger.error(f"Invalid response from production API: {truck_data}")
            return jsonify({"error": "Invalid data received from production API"}), 502

        logger.info(f"Successfully retrieved data for truck {id}")
        return jsonify(truck_data), 200

    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to connect to production API"}), 503

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to process truck information request"}), 500

@app.route('/truck-info-test', methods=['GET'])
def truck_info_test_page():
    """Serve the truck information test page HTML"""
    return render_template('truck_info_test.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("FLASK_PORT", 5000))
