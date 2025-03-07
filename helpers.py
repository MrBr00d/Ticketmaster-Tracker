import requests
import configparser
import pickle
import time
import random
import logging
import os
import asyncio
import aiohttp

ini_file_path = os.path.join(os.path.dirname(__file__), "secrets.ini")
pickle_dir = os.path.join(os.path.dirname(__file__), "data.pickle")
print(pickle_dir)
logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read(ini_file_path)
print(config.sections())
DB_KEY = config["CREDENTIALS"]["DB_KEY"]


def load_tracker_db() -> list:

    url = config["CREDENTIALS"]["URL"] + "/rest/v1/trackers?select=*"

    payload = {}
    headers = {
    'apikey': f'{DB_KEY}',
    'Authorization': f'Bearer {DB_KEY}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        logger.info("Tracker load OK")
        return response.json()
    else:
        logger.error(f"Non-OK response from supabase")
    
def request_api(concert_number):
    url = f"https://availability.ticketmaster.nl/api/v2/TM_NL/resale/{concert_number}"
    headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'nl,en-US;q=0.7,en;q=0.3',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'cross-site',
  'Sec-Fetch-User': '?1',
  'Priority': 'u=0, i',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'TE': 'trailers'
}
    time.sleep(random.randint(1,10))
    logger.info(f"Start API call for concert {concert_number}")
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        return response.json()["offers"]
    else:
        logger.error(f"Non-OK statuscode for Ticketmaster API request for concert_id {concert_number}")

def check_new(ticket_ids: list) -> tuple[bool,list]:
    """Usage should be the list of tickt id's from a single concert."""
    new = False
    new_tickets = []
    try:
        with open(pickle_dir, 'rb') as f:
            hist_tickets = pickle.load(f)
    except:
        hist_tickets = {}

    for res in ticket_ids:
        if res["id"] in hist_tickets:
            continue
        else:
            hist_tickets[res["id"]] = res["price"]['total']/100
            new_tickets.append(res["price"]['total']/100)
            new = True

    with open(pickle_dir, 'wb') as f:
        pickle.dump(hist_tickets, f, pickle.HIGHEST_PROTOCOL)
    return new, new_tickets

async def push_notification(session, user_id, concert_name, prices):
    url = f"https://ntfy.sh/{user_id}"
    message = f"caa05286-99fb-4738-bcb8-053c04ca0c85 There are new tickets available for concert: {concert_name}. The price(s) are: {prices}"
    async with session.post(url, data=message.encode(encoding='utf-8'), headers={"Priority": "high"}) as response:
        logger.info(f"Pushed concert info to user: {user_id}")
        return await response.text()

async def process_notifications(results, all_trackers):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for result, prices in results.items():
            for row in all_trackers:
                if result == row["concert_id"]:
                    tasks.append(push_notification(session, row["user_id"], row["concert_name"], prices))
        await asyncio.gather(*tasks)
