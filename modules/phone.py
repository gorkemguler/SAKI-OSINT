import phonenumbers
import requests
from googlesearch import search
import configparser
import os

def check_phone_number(phone_number):
    results = {
        "valid": False,
        "country_code": None,
        "national_number": None,
        "carrier": None,
        "location": None,
        "online_mentions": []
    }

    config = configparser.ConfigParser()
    config.read('config.ini')

    if config.has_section('PROXY'):
        http_proxy = config['PROXY'].get('HTTP_PROXY')
        https_proxy = config['PROXY'].get('HTTPS_PROXY')
        if http_proxy: os.environ['HTTP_PROXY'] = http_proxy
        if https_proxy: os.environ['HTTPS_PROXY'] = https_proxy

    try:
        parsed_number = phonenumbers.parse(phone_number)
        if phonenumbers.is_valid_number(parsed_number):
            results["valid"] = True
            results["country_code"] = parsed_number.country_code
            results["national_number"] = parsed_number.national_number
            
            # Get carrier and location info (may not always be available)
            from phonenumbers import carrier, geocoder
            results["carrier"] = carrier.name_for_number(parsed_number, "en")
            results["location"] = geocoder.description_for_number(parsed_number, "en")

            # Search for online mentions (basic Google search)
            query = f'\"{phone_number}\" site:.com OR site:.org OR site:.net OR site:.io'
            print(f"[*] Searching Google for mentions of {phone_number}...")
            try:
                for url in search(query, num=5, stop=5, pause=2):
                    results["online_mentions"].append(url)
            except Exception as e:
                results["online_mentions"].append(f"Error during Google search: {e}")

    except Exception as e:
        results["error"] = str(e)

    return results

