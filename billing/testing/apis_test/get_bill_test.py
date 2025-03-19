import requests

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'

class Formats:
    BOLD = '\033[1m'
    RESET = '\033[0m'

def run_get_bill_check():
    bill_get_url = "http://localhost:5000/bill/{id}"
    try:
        bill_get_url = bill_get_url.format(id="10006")
        response = requests.get(bill_get_url)
        if response.status_code == 200:
            get_bill = ("Bill GET Test :" + Formats.BOLD + Colors.GREEN + " Passed OK!" + Colors.END + Formats.RESET)
            print(get_bill)
        else:
            get_bill = ("Bill GET Test :" + Formats.BOLD + Colors.RED + " FAILED!" + Colors.END + Formats.RESET)
            print(get_bill)
            print(response)
    except requests.RequestException as e:
        get_bill = ("Bill GET Test :" + Formats.BOLD + Colors.RED + " FAILED!" + Colors.END + Formats.RESET)
        print(get_bill)
        print(get_bill, e)
    print(get_bill)