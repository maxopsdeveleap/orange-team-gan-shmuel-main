from flask import Flask, render_template, request, jsonify
import datetime
# import mysql.connector
# import os

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

# http://localhost:5000/weight?from=20230301000000&to=20230302235959&filter=in,out


@app.route("/weight", methods=["GET"])
def get_weight():
    from_param = request.args.get('from', default="20230301000000")
    to_param = request.args.get('to', default=str(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    filter_param = request.args.get('filter', default="in,out,none")

    try:
        t1 = datetime.datetime.strptime(from_param, '%Y%m%d%H%M%S')
        t2 = datetime.datetime.strptime(to_param, '%Y%m%d%H%M%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected format: yyyymmddhhmmss"}), 400

    filter_directions = filter_param.split(',')

    filtered_data = []
    for item in sessions_data:
        item_time = datetime.datetime.fromtimestamp(
            float(item['id'].split('.')[0]))

        if t1 <= item_time <= t2 and item['direction'] in filter_directions:
            filtered_data.append(item)

    return jsonify(filtered_data), 200


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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0", port="5001")
