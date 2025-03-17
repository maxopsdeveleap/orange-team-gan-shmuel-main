from flask import Flask, render_template, request, jsonify
from mysqlweight import connect
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"OK": "app running."}), 200


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
