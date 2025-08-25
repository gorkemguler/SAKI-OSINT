import configparser
import requests

HIBP_API_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/{account}"
HIBP_UNIFIED_URL = "https://haveibeenpwned.com/unifiedsearch/{account}"

def check_email_breach(email):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['API_KEYS'].get('HIBP_API_KEY')

    proxies = {}
    if config.has_section('PROXY'):
        http_proxy = config['PROXY'].get('HTTP_PROXY')
        https_proxy = config['PROXY'].get('HTTPS_PROXY')
        if http_proxy: proxies['http'] = http_proxy
        if https_proxy: proxies['https'] = https_proxy

    if api_key:
        print("INFO: Using HIBP API key.")
        headers = {"hibp-api-key": api_key}
        try:
            response = requests.get(HIBP_API_URL.format(account=email), headers=headers, proxies=proxies)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return [] # No breaches found
            else:
                return {"error": f"API returned status code {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"An error occurred during API request: {e}"}
    else:
        print("WARNING: No HIBP API key found. Trying experimental method with Selenium.")
        print("INFO: This requires Selenium and a compatible browser (like Chrome) to be installed.")
        print("INFO: The first run might be slow as it downloads the necessary browser driver.")

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import json

            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

            if https_proxy: # Assuming HTTPS_PROXY is used for Selenium
                options.add_argument(f'--proxy-server={https_proxy}')

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

            print(f"INFO: Navigating to HIBP for {email}...")
            driver.get(HIBP_UNIFIED_URL.format(account=email))

            wait = WebDriverWait(driver, 15)
            pre_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
            
            breaches_json = pre_element.text
            data = json.loads(breaches_json)
            
            driver.quit()

            return {"breaches": data.get("Breaches", [])}

        except Exception as e:
            if 'driver' in locals() and driver:
                driver.quit()
            return {"error": f"An error occurred with Selenium: {e}"}
