from datetime import datetime
import argparse
from forex_python.converter import CurrencyCodes
import sys
import json
import os
import requests
import requests_cache
# ratelimit_requests_cache.install_cache('example_cache')
# requests_cache.install_cache('demo_cache')


def is_date_valid(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date <= datetime.today():
            return date
        return False
    except ValueError:
        return False


def is_amount_valid(amount):
    amount_str = str(amount)
    parts = amount_str.split(".")

    return len(parts) == 2 and len(parts[1]) == 2 and parts[0].isdecimal() and parts[1].isdecimal()


def is_currency_code_valid(code):
    currency_codes = CurrencyCodes()
    return currency_codes.get_currency_name(code.upper()) is not None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('date', type=is_date_valid)

    args = parser.parse_args()

    date = args.date.strftime('%Y-%m-%d')

    flag = True
    while flag:
        input_amount = input()
        while flag:
            if input_amount.upper() == "END":
                sys.exit()
            if (
                    is_amount_valid(input_amount) != 0):
                amount = input_amount
                break
            input_amount = input("Please enter a valid amount ")

        base_currency_input = input()
        while flag:
            if base_currency_input.upper() == "END":
                sys.exit()
            if is_currency_code_valid(base_currency_input) != 0:
                base_currency = base_currency_input.upper()
                break
            base_currency_input = input("Please enter a valid currency code ")

        target_currency_input = input()
        while flag:
            if target_currency_input.upper() == "END":
                sys.exit()
            if is_currency_code_valid(target_currency_input) != 0:
                target_currency = target_currency_input.upper()
                break
            target_currency_input = input("Please enter a valid currency code ")

        script_dir_config = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir_config, 'config.json')

        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as json_file:
            config = json.load(json_file)
            api_key = config['api_key']

        url = 'https://api.fastforex.io/historical'

        params = {
            'api_key': api_key,
            'date': str(date),
            'from': base_currency,
            'to': target_currency
        }

        response = requests.get(url, params=params)

        exchange_rate = response.json()['results'][target_currency]
        target_amount = round(float(exchange_rate) * float(amount), 2)
        output = amount + " " + str(base_currency) + " is " + str(target_amount) + " " + str(target_currency)

        print(output)

        script_dir_output = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir_output, 'output.json')

        with open(output_path, 'r') as json_file:
            existing_data = json.load(json_file)

        existing_data[date + " " + amount + " " + str(base_currency)] = str(target_amount) + " " + str(target_currency)

        with open(output_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)


if __name__ == "__main__":
    main()
