from flask import Flask
from mysqlbilling import connect

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
        try:
            connect()
            return 'OK', 200
        except:
            return 'Failure', 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
