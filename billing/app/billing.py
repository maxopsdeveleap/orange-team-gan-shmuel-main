from flask import Flask
from mysqlbilling import connect

app = Flask(__name__)


# @app.route('/', methods=[''])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
