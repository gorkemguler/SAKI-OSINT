import asyncio
import aiohttp
import json
import re
import configparser

async def check_email_registration(session, site, email):
    url = site["url"].format(email=email)
    method = site.get("method", "GET")
    headers = site.get("headers", {})
    data = site.get("data")
    success_regex = site.get("success_regex")
    fail_regex = site.get("fail_regex")

    # Add a default User-Agent header if not present
    if "User-Agent" not in headers:
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"

    try:
        if method == "POST":
            if data:
                # Check if data is meant to be JSON
                if "application/json" in headers.get("Content-Type", ""):
                    payload = json.loads(data.format(email=email))
                    async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                        text = await response.text()
                else:
                    payload = data.format(email=email)
                    async with session.post(url, headers=headers, data=payload, timeout=10) as response:
                        text = await response.text()
            else:
                async with session.post(url, headers=headers, timeout=10) as response:
                    text = await response.text()
        else: # GET
            params = site.get("params", {})
            for key, value in params.items():
                params[key] = value.format(email=email)
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                text = await response.text()

        if success_regex and re.search(success_regex, text):
            return site["name"], url, True
        elif fail_regex and re.search(fail_regex, text):
            return site["name"], url, False
        else:
            # If no specific regex matches, try to infer from status code or general content
            if response.status == 200 and ("account" in text.lower() or "user" in text.lower()) and ("found" in text.lower() or "exists" in text.lower()):
                return site["name"], url, True
            elif response.status == 404 or "not found" in text.lower() or "does not exist" in text.lower():
                return site["name"], url, False
            return site["name"], url, "Unknown"

    except asyncio.TimeoutError:
        return site["name"], url, "Timeout"
    except aiohttp.ClientError:
        return site["name"], url, "Error"
    except Exception as e:
        return site["name"], url, f"Exception: {e}"

async def search_email_registrations(email):
    config = configparser.ConfigParser()
    config.read('config.ini')

    proxy = None
    if config.has_section('PROXY'):
        http_proxy = config['PROXY'].get('HTTP_PROXY')
        https_proxy = config['PROXY'].get('HTTPS_PROXY')
        if https_proxy:
            proxy = https_proxy
        elif http_proxy:
            proxy = http_proxy

    with open("email_recon_sites.json") as f:
        sites = json.load(f)["sites"]

    results = []
    async with aiohttp.ClientSession(proxy=proxy) as session:
        tasks = [check_email_registration(session, site, email) for site in sites]
        responses = await asyncio.gather(*tasks)
        for result in responses:
            results.append(result)
    return results
