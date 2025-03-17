from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"OK": "app running."}), 200

@app.route("/api/weight", methods=["GET","POST"])
def weight():
    if request.method == "GET":

        # Get parameters from the URL
        paramFrom = request.args.get("from")
        paramTo = request.args.get("to")
        paramFilter = request.args.get("filter","in,out,none")

        return jsonify([{"from":paramFrom},{"to":paramTo},{"filter":paramFilter}])

        #return jsonify([{"id": "example"},{"id": "example2"}]), 200

    elif request.method == "POST":
        return jsonify({"not implemented"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0", port="5001")
