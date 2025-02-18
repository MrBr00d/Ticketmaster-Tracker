import requests
import pickle
import time
import random
# In order to start tracking you need to create a "concerts.txt" file.
# In this file you enter the ID of the ticketmaster concert (last number in url) followed by a comma and then the concert name. Each concert you want to track will be on a new line. e.g.
# 1234,AC/DC
# 5678,Sabaton
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
    return requests.request("GET", url, headers=headers)

def check_offers(response):
    results = response.json()["offers"]
    new = False

    try:
        with open('data.pickle', 'rb') as f:
            hist_tickets = pickle.load(f)
    except:
        hist_tickets = {}

    for res in results:
        if res["listingId"] in hist_tickets:
            continue
        else:
            hist_tickets[res["listingId"]] = res["price"]['total']/100
            new = True

    with open('data.pickle', 'wb') as f:
        pickle.dump(hist_tickets, f, pickle.HIGHEST_PROTOCOL)
    return new

def push_notification(names:list):
    requests.post("https://ntfy.sh/HhXk7fxzeHHst78I",
                  data = ("Er zijn nieuwe tickets beschikbaar voor de concerten: " + " en ".join(names)).encode(encoding='utf-8'),
                  headers={"Priority": "high"})

if __name__ == "__main__":
    new_concerts = []
    with open("concerts.txt", "r") as f:
        concerts = f.read().split("\n")
    for concert in concerts:
        concert_num, name = concert.split(",")
        api_response = request_api(concert_num)
        new_tickets = check_offers(api_response)
        if new_tickets:
            new_concerts.append(name)
    if new_concerts:
        push_notification(new_concerts)