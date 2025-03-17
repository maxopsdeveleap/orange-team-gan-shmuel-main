from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"OK": "app running."}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0", port="5001")
