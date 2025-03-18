from flask import Flask, request, jsonify
from mysqlbilling import connect
import os

app = Flask(__name__)


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
    except:
         return jsonify({"error": "Failed to insert new entry"}), 500
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


# POST /truck - Register a truck
@app.route('/truck', methods=['POST'])
def register_truck():
    # Get JSON data from the request
    data = request.get_json()

    # Validate input
    if not data or 'provider_id' not in data or 'truck_id' not in data:
        return jsonify({"error": "Missing required fields: 'provider_id' and 'truck_id'"}), 400

    provider_id = data['provider_id']  # Provider's ID
    license_number = data['truck_id']  # Truck's license plate (truck_id)

    conn = None
    cursor = None

    try:
        # Establish a database connection
        connection = connect()
        cursor = conn.cursor(dictionary=True)

        # Check if the provider exists
        cursor.execute("SELECT id FROM Provider WHERE id = %s", (provider_id,))
        provider = cursor.fetchone()

        if not provider:
            return jsonify({"error": "Provider not found"}), 404

        # Check if the truck already exists
        cursor.execute("SELECT * FROM trucks WHERE truck_id = %s", (license_number,))
        existing_truck = cursor.fetchone()

        if existing_truck:
            return jsonify({"error": "Truck already exists"}), 409

        # Insert the truck into the database
        cursor.execute("INSERT INTO trucks (truck_id, provider_id) VALUES (%s, %s)", (license_number, provider_id))
        conn.commit()

        # Return success response
        return jsonify({"message": "Truck registered successfully", "truck_id": license_number}), 201

    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error registering truck: {e}")
        return jsonify({"error": "Failed to register truck"}), 500

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("FLASK_PORT", 5000))
