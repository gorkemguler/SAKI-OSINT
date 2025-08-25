import asyncio
import aiohttp
import json
import configparser

async def check_username(session, site, username):
    url = site["url"].format(username)
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                return site["name"], url, True
            else:
                return site["name"], url, False
    except asyncio.TimeoutError:
        return site["name"], url, "Timeout"
    except aiohttp.ClientError:
        return site["name"], url, "Error"

async def search_usernames(username):
    config = configparser.ConfigParser()
    config.read('config.ini')

    proxy = None
    if config.has_section('PROXY'):
        http_proxy = config['PROXY'].get('HTTP_PROXY')
        if http_proxy: # aiohttp uses a single proxy setting
            proxy = http_proxy

    with open("sites_data.json") as f:
        sites = json.load(f)["sites"]

    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [check_username(session, site, username) for site in sites]
        responses = await asyncio.gather(*tasks)
        for result in responses:
            if result:
                results.append(result)
    return results
