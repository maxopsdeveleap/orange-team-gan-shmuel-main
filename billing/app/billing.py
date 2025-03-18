from flask import Flask, request, jsonify
from mysqlbilling import connect
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

    ## Be sure to pip freeze into root folder requirements.txt before committing







if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("FLASK_PORT", 5000))
