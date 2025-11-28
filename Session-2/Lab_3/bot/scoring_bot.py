import requests
import time

TARGET = "http://127.0.0.1:5004/admin"
COOKIE = {"session_user": "admin"}  # simulate admin session

INITIAL_PRICE = 199

def get_price():
    r = requests.get(TARGET, cookies=COOKIE)
    print(r.text)
    import re

    match = re.search(r"Current Price:\s*([0-9]+)", r.text)
    if not match:
        print("[!] Cannot extract price, check target.")
        return None

    price = match.group(1)
    print("[+] Extracted price:", price)
    return price


    # crude price extraction
    try:
        start = r.text.index("Current Price:") + len("Current Price:")
        snippet = r.text[start:start+20]
        price = int(''.join([c for c in snippet if c.isdigit()]))
        return price
    except:
        return None

print("[*] Scoring bot started. Waiting for exploitation...")

while True:
    price = get_price()

    if price is None:
        print("[!] Cannot extract price, check target.")
    elif price != INITIAL_PRICE:
        print(f"[+] SUCCESS! Student exploited CSRF. New price = {price}")
        break

    time.sleep(2)
