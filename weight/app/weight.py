from flask import Flask, render_template, request, jsonify
from mysqlweight import connect
from datetime import datetime
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
