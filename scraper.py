import configparser
import supabase
import helpers
import logging
import asyncio
import os

logging.basicConfig(
level=logging.DEBUG,  # Capture all levels of logs
format='%(asctime)s - %(levelname)s - %(message)s',  # Log format with timestamp
handlers=[
    logging.FileHandler("logfile.log"),  # Log to a file
    logging.StreamHandler()              # Log to console
    ]
)
ini_file_path = os.path.join(os.path.dirname(__file__), "secrets.ini")
config = configparser.ConfigParser()
config.read(ini_file_path)
API_KEY = config["CREDENTIALS"]["API_KEY"]
SUPABASE_URL = config["CREDENTIALS"]["URL"]
SUPABASE_KEY =  API_KEY
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    logging.info("Retrieving supabase information.")
    all_trackers = helpers.load_tracker_db()
    concerts = set([row["concert_id"] for row in all_trackers])
except Exception as e:
    logging.error(f"An error occured in retrieving the information from supabase: {e}")
new_concert_info = {}
for concert in concerts:
    response = helpers.request_api(concert)
    try:
        new, new_tickets_prices = helpers.check_new(response)
        if new:
            new_concert_info[concert] = new_tickets_prices
        else:
            logging.info(f"No new tickets found for concert {concert}")
    except Exception as e:
        logging.error(f"An error occured: {e}")
        logging.info(f"Skipping concert {concert}")
        continue
asyncio.run(helpers.process_notifications(new_concert_info, all_trackers))