import asyncio
import base64
from numpy import double
from telegram import Bot
from telegram.constants import ParseMode
import os
import json
from datetime import datetime
import pytz
 
print("Current Working Directory:", os.getcwd())
 
import requests
from requests.structures import CaseInsensitiveDict
import random
import string
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
 
from urllib.parse import quote
 
ADMIN = ["SECRETKEY:c2ltcGxpMTAw|NjU4OTM3ODU4NA=="]
TOKEN = '7019260893:AAEV8w6fJzvj4HHeOLtnCOywk-StGd20zr4'
filename = 'accounts.txt'
bot = Bot(token=TOKEN)
requests.adapters.DEFAULT_POOLSIZE = 100
 
a = ""
b = ""
chat_id = ''
 
def load_accounts(filename):
    try:
        with open(filename, 'r') as file:
            accounts = [line.strip() for line in file.readlines()]
            return accounts
 
    except FileNotFoundError:
        print(f"File '{filename}' not found.") 
        return []
 
def write_accounts_to_file(filename, accounts):
    with open(filename, 'w') as file:
        for account in accounts:
            file.write(str(account) + '\n')
 
def delete_account(account_to_delete, accounts, filename):
    if account_to_delete in accounts:
        accounts.remove(account_to_delete)
        write_accounts_to_file(filename, accounts)
        return (f"*ACCOUNT DELETED*\n\nAccount:\n`{account_to_delete}`")
    else:
        return (f"Account `{account_to_delete}` not found.")
 
async def sendMessage(chat_id, text):
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
 
def timestamp():
    now_utc = datetime.now(pytz.utc)
    philippines_timezone = pytz.timezone('Asia/Manila')
    now_philippines = now_utc.astimezone(philippines_timezone)
    timestamp_str = now_philippines.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp_str
 
async def editMessage(chatid, messageid, txt):
    await bot.edit_message_text(
        chat_id=chatid,
        message_id=messageid,
        text=txt,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
 
user_state = {}
 
def GetAuthorizationKey(telegramUsername, telegramId):
    username_bytes = str(telegramUsername).encode()
    id_bytes = str(telegramId).encode()
    AuthorizationKey: bytes = base64.b64encode(username_bytes) + b'|' + base64.b64encode(id_bytes)
    return AuthorizationKey.decode() 
 
def generate_random_password():
    letters_count = random.randint(5, 10)
    digits_count = 3
    random_letters = ''.join(random.choice(string.ascii_letters) for _ in range(letters_count))
    random_digits = ''.join(random.choice(string.digits) for _ in range(digits_count))
    password = random_letters + random_digits
    return password
 
def clean_response_text(response_text):
    cleaned_text = re.sub(r'[^ -~]+', '', response_text)
    return cleaned_text
 
def fetch_ip(proxy):
    try:
        response = requests.get('http://httpbin.org/ip', proxies=proxy)
        return response.json()['origin']
    except requests.RequestException as e:
        return f"Error fetching IP: {e}"
 
def auto_registercb(inv_code, proxy):
    url = "https://api.711bet2.com/gw/login/register"
    headers = CaseInsensitiveDict({
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": "https://711bet2.com/",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "U-Devicetype": "pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })
 
    num1 = random.randint(9111111111, 9999999999)
    random_password = generate_random_password()
 
    payload = {
        "invite_code": inv_code,
        "agreeOnPromos": True,
        "account_value": f"+63|{num1}",
        "account_type": 1,
        "password": random_password,
        "agreeOnState": True,
        "extra": {"from": "act_raffle"},
        "flow_id": ""
    }
 
    current_ip = fetch_ip(proxy)
 
    response = requests.post(url, headers=headers, json=payload, proxies=proxy, timeout=50)
    cleaned_text = clean_response_text(response.text)
 
    if '{"code":6,"msg":"already exists"}' in cleaned_text:
        print("Invitation code already exists. Skipping registration.")
        return None
 
    data = response.json().get('data', {})
    user_id = data.get('user_id', 'N/A')
    token = data.get('token', 'N/A')
 
    if user_id == 'N/A' or token == 'N/A':
        raise ValueError("Failed to extract user_id or token from the registration response.")
 
    return (current_ip, random_password, user_id, token, num1)
 
def auto_recharge(user_id, token, amount, currency, typ, pay_method, proxy):
    recharge_url = "https://api.711bet2.com/user/recharge"
    headers = CaseInsensitiveDict({
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"{token};{user_id}",
        "Content-Type": "application/json",
        "Referer": "https://711bet2.com/",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "U-Devicetype": "pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })
 
    recharge_payload = {
        "amount": "100",
        "currency": "PHP",
        "data": {"typ": "GCASHORIGIN", "pay_method": "electronic_wallet"},
        "pay_method": "electronic_wallet",
        "typ": "GCASHORIGIN",
        "device": "pc",
        "task_id": "-1",
        "token": token,
        "user_id": user_id
    }
 
    try:
        response = requests.post(recharge_url, json=recharge_payload, proxies=proxy)
        response_json = response.json()
 
        if '{"code":200,"message' in response.text:
            responseData = response.json()
            paymentLink = responseData['data']['pay_method']['cashier']
            return True, paymentLink
        else:
            return False, response.text
 
    except requests.RequestException as e:
        return f"Error during auto-recharge: {e}"
 
async def perform_withdrawal(user_id, token, amount, withdrawal_id):
    url = "https://api.711bet2.com/user/withdraw"
    url2 = "https://api.711bet.com.ph/user/get_all_asset"
 
    payload = {
        "amount": amount,
        "currency": "PHP",
        "data": {
            "method": "electronic_wallet",
            "pay_method": "id",
            "pay_method_id": withdrawal_id
        },
        "method": "electronic_Wallet",
        "pay_method": "id",
        "pay_method_id": "",
        "token": str(token),
        "user_id": str(user_id)
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(f'{user_id};{token}'),
        'Origin': 'https://711bet2.com',
        'Referer': 'https://711bet2.com',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    payload2 = {
        "user_id": user_id,
        "token": token,
    }
 
    headers2 = {
        'Content-Type': 'application/json',
        'Authorization': f'{user_id};{token}',
        'Origin': 'https://711bet.com.ph',
        'Referer': 'https://711bet.com.ph/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        # First request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = json.loads(response.text)
        print("Response from url:", response.text)
        print(payload)
 
        # Second request
        response2 = requests.post(url2, json=payload2, headers=headers2)
        response2.raise_for_status()
        print("Response from url2:", response2.text)
        print(payload2)
 
        # Process response data
        site_response = response_data.get('message')
        gamewallet = response2.json().get('data', {}).get('PHP', {})
        
        if response_data.get('code') == 200:
            return (f"*Message: Success*\n🆔 WithdrawID:`{withdrawal_id}`\n💸 Amount: `PHP {amount}`\n\nℹ️ SITE DETAILS\n👝 Game Wallet:\t`PHP {gamewallet.get('amount')}`\n💰 Withdrawable:\t`PHP {gamewallet.get('withdrawable_amount')}`\n⌛️ Bet Progress:\t`PHP {gamewallet.get('bet_progress')}`\n🎯 Bet Target:\t`PHP {gamewallet.get('bet_target')}`")
        else:
            return (f"*Message: {site_response}*\n🆔 WithdrawID:`{withdrawal_id}`\n💸 Amount: `PHP {amount}`\n\nℹ️ SITE DETAILS\n👝 Game Wallet:\t`PHP {gamewallet.get('amount')}`\n💰 Withdrawable:\t`PHP {gamewallet.get('withdrawable_amount')}`\n⌛️ Bet Progress:\t`PHP {gamewallet.get('bet_progress')}`\n🎯 Bet Target:\t`PHP {gamewallet.get('bet_target')}`")
 
    except requests.exceptions.RequestException as e:
        return (f"Error during withdrawal request: {e}")
 
def ewallet_info(token, user_id):
    url = "https://api.711bet2.com/user/withdraw_pays"
    fprint:str = ''
 
    payload = {
        "user_id": user_id,
        "token": token,
        "currency": "PHP"
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{user_id};{token}',
        'Origin': 'https://711bet2.com',
        'Referer': 'https://711bet2.com',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    url2 = "https://api.711bet.com.ph/user/get_all_asset"
    payload2 = {
        "user_id": user_id,
        "token": token,
    }
    headers2 = {
        'Content-Type': 'application/json',
        'Authorization': f'{user_id};{token}',
        'Origin': 'https://711bet.com.ph',
        'Referer': 'https://711bet.com.ph/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response2 = requests.post(url2, json=payload2, headers=headers2)
        response2.raise_for_status()
 
        ewallet_data = response.json()
        gamewallet = response2.json().get('data', {}).get('PHP', {})
 
        if "data" in ewallet_data and isinstance(ewallet_data["data"], list):
            ewallet_data = ewallet_data["data"]
            if not ewallet_data:
                return(f"ℹ️ No eWallet information available. \n\nGame Wallet:\t`PHP {gamewallet.get('amount')}`\nWithdrawable:\t`PHP {gamewallet.get('withdrawable_amount')}`\nBet Progress:\t`PHP {gamewallet.get('bet_progress')}`\nBet Target:\t`PHP {gamewallet.get('bet_target')}`")
            else:
                fprint:str = fprint + "*ℹ️ eWallet information:*"+"\n"
                for wallet_info in ewallet_data:
                    fprint = fprint + "🆔 Wallet ID: *" + str(wallet_info.get("id")) +"*\n"
                    fprint = fprint + "💳 Payment Method: *" + str(wallet_info.get("payment_method"))+"*\n"
                    fprint = fprint + "👤 Account Name: *" + str(wallet_info.get("account_name"))+"*\n"
                    fprint = fprint + "📱 Account Number: *" + str(wallet_info.get("account_no"))+"*\n"
                    fprint = fprint + "📱 Phone: *" + str(wallet_info.get("phone"))+"*\n\n🎮GAME WALLET:\n"
                    fprint = fprint + "💸 Amount: *" + str(gamewallet.get('amount'))+"*\n"
                    fprint = fprint + "💰 Withdrawable: *" + str(gamewallet.get('withdrawable_amount'))+"*\n"
                    fprint = fprint + "⏳ Bet Progress: *" + str(gamewallet.get('bet_progress'))+"*\n"
                    fprint = fprint + "🎯 Bet Target: *" + str(gamewallet.get('bet_target'))+"*\n\n"
                return fprint
        elif "code" in ewallet_data and ewallet_data["code"] == 401:
            return ("Invalid credentials. Please check your login information.")
        else:
            return ("Invalid eWallet information response.")
 
    except requests.exceptions.RequestException as e:
        return (f"Error during eWallet information request: {e}")
 
def getwalletid(token, user_id):
    url = "https://api.711bet2.com/user/withdraw_pays"
 
    payload = {
        "user_id": user_id,
        "token": token,
        "currency": "PHP"
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{user_id};{token}',
        'Origin': 'https://711bet2.com',
        'Referer': 'https://711bet2.com',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
 
        ewallet_data = response.json()
 
        if "data" in ewallet_data and isinstance(ewallet_data["data"], list):
            data_list = ewallet_data["data"]
            if data_list:
                for item in data_list:
                    if "id" in item:
                        return item["id"]
            else:
                return "No eWallet information available."
        elif "code" in ewallet_data and ewallet_data["code"] == 401:
            return "Invalid credentials. Please check your login information."
        else:
            return "Invalid eWallet information response."
 
    except requests.exceptions.RequestException as e:
        return f"Error during eWallet information request: {e}"
 
def bindM(user_id, token, accountname, accountnumber):
    url = "https://api.711bet.io/api/v1/platform/asset_order/withdraw_info/add"
 
    payload = {
        "data": {
            "phone": accountnumber,
            "email": f"{accountnumber}@gmail.com",
            "payment_method": "PAYMAYA",
            "account_name": accountname,
            "account_no": f"0{accountnumber}"
        },
        "withdraw_type": "electronic_wallet",
        "token": quote(token),
        "user_id": quote(user_id)
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{user_id};{token}',
        'Origin': 'https://711bet.io',
        'Referer': 'https://711bet.io/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
 
        response_data = response.json()
        code = response_data.get("code")
        message = response_data.get("message")
 
        if code == 200:
            account_data = response_data.get("data", {})
            name = account_data.get("account_name")
            account_no = account_data.get("account_no")
            phone = account_data.get("phone")
            email = account_data.get("email")
            return f"*BINDED SUCCESSFULLY*\n\nℹ️ Details:\n👤 Name: {name}\n#️⃣ Account Number: {account_no}\n📱 Phone: {phone}\n📧 Email: {email}\n✍️ Message: {str(message)}\n🏧 Method: Paymaya"
        else:
            return f"Error Code: {code}\nMessage: {message}"
 
    except requests.exceptions.RequestException as e:
        return f"Error Code: 500\nMessage: Error during bind request: {e}"
 
def bind(user_id, token, accountname, accountnumber):
    url = "https://api.711bet.io/api/v1/platform/asset_order/withdraw_info/add"
 
    payload = {
        "data": {
            "phone": accountnumber,
            "email": f"{accountnumber}@gmail.com",
            "payment_method": "GCASH",
            "account_name": accountname,
            "account_no": f"0{accountnumber}"
        },
        "withdraw_type": "electronic_wallet",
        "token": quote(token),
        "user_id": quote(user_id)
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{user_id};{token}',
        'Origin': 'https://711bet.io',
        'Referer': 'https://711bet.io/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
 
        response_data = response.json()
        code = response_data.get("code")
        message = response_data.get("message")
 
        if code == 200:
            account_data = response_data.get("data", {})
            name = account_data.get("account_name")
            account_no = account_data.get("account_no")
            phone = account_data.get("phone")
            email = account_data.get("email")
            return f"*BINDED SUCCESSFULLY*\n\nℹ️ Details:\n👤 Name: {name}\n#️⃣ Account Number: {account_no}\n📱 Phone: {phone}\n📧 Email: {email}\n✍️ Message: {str(message)}\n🏧 Method: Gcash"
        else:
            return f"Error Code: {code}\nMessage: {message}"
 
    except requests.exceptions.RequestException as e:
        return f"Error Code: 500\nMessage: Error during bind request: {e}"
 
def get_current_datetime():
    current_datetime = datetime.now()
    formatted_current_datetime = current_datetime.isoformat() + 'Z'
 
    return formatted_current_datetime
 
def check_status(user_id, token, withdrawal_id):
    url = "https://api.711bet.com.ph/user/list_withdraw"
 
    payload = {
        "from_time": "2024-03-23T16:00:00.000Z",
        "to_time": quote(get_current_datetime()),
        "pos": 0,
        "size": 10,
        "user_id": user_id,
        "token": token
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{str(user_id)};{str(token)}',
        'Origin': 'https://711bet.com.ph',
        'Referer': 'https://711bet.com.ph/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
 
        response_data = response.json()
        code = response_data["code"]
 
        if code == 200:
            withdrawals_info = ""
            for withdrawal in response_data["data"]:
                amount = withdrawal["amount"]
                actual = withdrawal["actual_amount"]
                state = withdrawal["state"]
 
                if state == "accepted_and_done":
                    withdrawals_info += f"💰 Amount: `{amount}`\n💸 Actual: `{actual}`\n💡 State: `{state}`\n\n"
                else:
                    withdrawals_info += f"💰 Amount: `{amount}`\n💸 Actual: `{actual}`\n💡 State: `{state}`\n\n"
 
            return withdrawals_info
        else:
            return f"Response code: {code}"
 
    except requests.exceptions.RequestException as e:
        return f"Error during request: {e}"

 
 
def login(phone, password):
    url = "https://api.711bet2.com/gw/login/login"
 
    payload = {
        "account_value": f"+63|{quote(phone)}",
        "password": quote(password),
        "account_type": 1,
        "redirect_uri": "https://711bet2.com"
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://711bet2.com',
        'Referer': 'https://711bet2.com',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
 
        responsedata = response.json()
 
        if responsedata["code"] == 0:
            print("✅ Login successful!")
            token, user_id = responsedata["data"]["token"], responsedata["data"]["user_id"]
            return token, user_id
 
        elif responsedata["code"] == 20:
            raise Exception(f"❌ *Login Failed*\n\nReason: \n[{responsedata['code']}] - {responsedata['msg']}")
 
        else:
            raise Exception(f"❌ Login failed with code {responsedata['code']}: {responsedata['msg']}")
 
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error during login request: {e}\n\n{responsedata}")
 
 
 
def boostwheel(inv_code:str, num_invites:int):
    proxy_host = "rp.proxyscrape.com"
    proxy_port = 6060
    proxy_username = "z9duk1c4p6h0267"
    proxy_password = "2z2894dte2x3upo"
 
    proxy = {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
    }
 
    results = []
    finalres = "BOOSTED ACCOUNTS\n\n"
    with ThreadPoolExecutor(max_workers=200) as executor:
        future_to_register = {executor.submit(auto_registercb, inv_code, proxy): _ for _ in range(num_invites)}
        for future in as_completed(future_to_register):
            result = future.result()
            if result is not None:  # Skip None results
                results.append(result)
    print("\nAll registrations completed. Summary of created accounts and IPs with recharge info:\n")
    global chat_id
    for result in results:
        ip, password, user_id, token, num1 = result  # Added num1
        # Print formatted output
        finalres += f'👤 Username: `{num1}`\n🔑 Password: `{password}`\n📍 IP Registered: {ip}\n'
        # Perform auto-recharge after registration
        success, recharge_link = auto_recharge(user_id, token, "100", "PHP", "GCASHORIGIN", "electronic_wallet", proxy)
        if success:
            finalres = finalres + f"📎 [Recharge Link]({recharge_link})\n"
 
        else:
            finalres = finalres + f'Failed to get Recharge Link\n'
        finalres = finalres + f'\n'
    return finalres
 
def spin(token, userid):
    url = "https://api.www-711bet.com/api/v1/act-raffle/draw"
 
    payload = {
        "token": token,
        "user_id": userid
    }
 
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://711bet.com',
        'Referer': 'https://711bet.com',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'U-Devicetype': 'pc',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
 
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
 
        responsedata = response.json()
        message = ""
 
        if responsedata.get("code") == 200:
            currreward = responsedata["data"]["current_reward"]
            remreward = responsedata["data"]["remain_reward"]
            message = responsedata["message"]
        else:
            message = responsedata["message"]
 
        return responsedata.get("code", None), currreward, remreward, message
 
    except requests.exceptions.RequestException as e:
        print(f"`ERROR SPINNING: {e}`")
        return None, None, None, str(e)
 
async def readchat(text, message_id, user, chat_id):
    accounts = load_accounts(filename)
    skey = "SECRETKEY:"+GetAuthorizationKey(user.username, user.id)
    print("\n"+timestamp() + " : "+ f"{user.first_name} [{user.id}] : {text}")
 
    ms = ""
    ms += "`/help`\nshow all cmd\n\n"
    ms += "`/auth`\nshows secret key\n\n"
    ms += "`/boost invCode`\nboost to wheel 711BET with 2 referrals\n\n"
    ms += "`/bindG 9123456789 PASS GCNum GCName`\nGcash num must start at 9\n\n"
    ms += "`/bindM 9123456789 PASS MAYANum MAYAName`\nMaya num must start at 9\n\n"
    ms += "`/list 9123456789 PASS`\nWithdrawal List\n\n"
    ms += "`/viewE 9123456789 PASS`\nview walletEwallet details\n\n"
    ms += "`/withdraw 9123456789 PASS AMOUNT WITHDRAWID`\nwithdraw on 711 account\n\n"
 
    token, user_id = "Error", "error"
 
    if skey in accounts:
        if '/start' in text:
            param = text.split(' ')
            await sendMessage(chat_id, f"👋 Welcome to Simplicity Bot! 🤖\n\nPlease use /help for understanding the bot easily. Thanks!\n\nJoin my channel for updates: [SimpNoob Channel](https://t.me/simpNoob)\n\nOwner: [Simplicity](https://t.me/simpli100)")
 
        elif '/help' in text:            
            await sendMessage(chat_id, ms)
 
        elif '/auth' in text:
            reply = f"SECRETKEY:{GetAuthorizationKey(user.username, user.id)}"
            await sendMessage(chat_id, reply)
            print(timestamp() + " : "+reply)
 
        elif '/bindG' in text:
            command = text.split(' ')
            phone: str = command[1]
            password: str = command[2]
            gcnum: int = command[3]
            gcname: str = command[4]
            token, user_id = login(phone, password)
            reply = bind(user_id, token, gcname, gcnum)
            await sendMessage(chat_id, reply)
            print(timestamp() + " : "+reply)
 
        elif '/bindM' in text:
            command = text.split(' ')
            phone: str = command[1]
            password: str = command[2]
            gcnum: int = command[3]
            gcname: str = command[4]
            token, user_id = login(phone, password)
            reply = bindM(user_id, token, gcname, gcnum)
            await sendMessage(chat_id, reply)
            print(timestamp() + " : "+reply)
 
 
        elif '/boost' in text:
            param = text.split(' ')
            baccount :str = param[1]
            nboost = 2
            await sendMessage(chat_id, f"*🚀 NOW BOOSTING*\n\n👤 Account:\n`{baccount}`\n\n⌛️ _Please wait for 1-5mins_")
            reply = boostwheel(baccount, nboost)
            await sendMessage(chat_id, reply)
            print(timestamp() + " : "+reply)
 
        elif '/withdraw' in text:
            command = text.split(' ')
            phone = command[1]
            password = command[2]
            amount = command[3]
            withdrawal_id = command[4]
            token, user_id = login(phone, password)
            reply = await perform_withdrawal(user_id, token, amount, withdrawal_id)
            await sendMessage(chat_id,  reply)
            print(timestamp() + " : " + reply)
 
        elif '/list' in text:
            command = text.split(' ')
            phone:str = command[1]
            password:str = command[2]
            token, user_id = login(phone, password)
            withdrawal_id:int = getwalletid(token, user_id)
            reply = check_status(user_id, token, withdrawal_id)
            await sendMessage(chat_id,  reply)
            print(timestamp() + " : "+ reply)
 
        elif '/viewE' in text:
            command = text.split(' ')
            phone:str = command[1]
            password:str = command[2]
            token, user_id = login(phone, password)
            reply = ewallet_info(token, user_id)
            await sendMessage(chat_id,  reply)
            print(timestamp() + " : "+reply)
 
        elif '/add' in text:
            if skey in ADMIN:
                param = text.split(' ')
                baccount:str = param[1] 
                await sendMessage(chat_id, f"*NOW AUTHENTICATED*\n\nAccount:\n`{baccount}`")
                print(timestamp() + " : "+f"*NOW AUTHENTICATED*\n\nAccount:\n`{baccount}`")
                s = [baccount]
                accounts.extend(s)
                write_accounts_to_file(filename, accounts)
 
        elif '/del' in text:
            if skey in ADMIN:
                param = text.split(' ')
                baccount:str = param[1]
                reply = delete_account(baccount, accounts, filename)
                print(timestamp() + " : "+ reply)
                await sendMessage(chat_id, reply)
 
        elif '/..' in text:
            if skey in ADMIN:
                sending = ""
                for account in accounts:
                    sending += "`" + account + "`\n\n"
                await sendMessage(chat_id, f"*REGISTERED ACCOUNTS*\n\n{sending}")
 
        else:
            asyncio.create_task(sendMessage(chat_id, f"wrong command....."))
 
    else: 
        if '/start' in text:
            await sendMessage(chat_id, f"👋 Welcome to Simplicity Bot! 🤖\n\n This bot is provided by Simplicity DM @Simpli100. For full access, please note that this bot is not free. Enjoy farming! \n\n please chat /help to understand the bot  thanks!")
 
        elif '/help' in text:
            await sendMessage(chat_id, ms)
 
        elif '/auth' in text:
            reply = f"SECRETKEY:{GetAuthorizationKey(user.username, user.id)}"
            await sendMessage(chat_id, reply)
            print(timestamp() + " : " + reply)
 
        elif '/add' in text:
            if skey in ADMIN:
                param = text.split(' ')
                baccount:str = param[1] 
                await sendMessage(chat_id, f"*NOW AUTHENTICATED*\n\nAccount:\n`{baccount}`")
                print(timestamp() + " : "+f"*NOW AUTHENTICATED*\n\nAccount:\n`{baccount}`")
                s = [baccount]
                accounts.extend(s)
                write_accounts_to_file(filename, accounts)
 
        elif '/del' in text:
            if skey in ADMIN:
                param = text.split(' ')
                baccount:str = param[1]
                reply = delete_account(baccount, accounts, filename)
                print(timestamp() + " : "+ reply)
                await sendMessage(chat_id, reply)
 
        elif '/..' in text:
            if skey in ADMIN:
                sending = ""
                for account in accounts:
                    sending += "`" + account + "`\n\n"  
                await sendMessage(chat_id, f"*REGISTERED ACCOUNTS*\n\n{sending}")
 
        else:
            asyncio.create_task(sendMessage(chat_id, f"Unauthorized"))
 
 
async def act():
    last_update_id = None
 
    while True:
        updates = await bot.get_updates(offset=last_update_id)
 
        for update in updates:
            last_update_id = update.update_id + 1
 
            if update.message:
                try:
                    text = update.message.text
                    message_id = update.message.message_id
                    user = update.message.from_user
                    global chat_id
                    chat_id = update.message.chat_id
                    await readchat(text, message_id, user, chat_id)
 
                except Exception as e:
                    await sendMessage(update.message.chat_id, f"*SORRY ERROR OCCURED, TRY AGAIN...* \n\nERROR: {e}")
                    print(timestamp() + " : "+f"ERROR: {e}")
                    continue
        await asyncio.sleep(1)
 
async def main():
    while True:
        try:
            await act()
        except Exception as e:
            print(timestamp() + " : "+f"ERROR: {e} \nBot Coming Back Online...")
            continue
 
asyncio.run(main())
