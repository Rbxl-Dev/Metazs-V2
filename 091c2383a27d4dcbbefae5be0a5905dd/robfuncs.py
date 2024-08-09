# script is part of version '091c2383a27d4dcbbefae5be0a5905dd' by © BitsProxy

import requests
import random
import time
import json

def heads(csrf, cookie):
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-Csrf-Token": csrf,
        "Cookie": f".ROBLOSECURITY={cookie}"
    }

def GetUserId(cookie):
    response = requests.get("https://www.roblox.com/MobileApi/UserInfo", cookies={'.ROBLOSECURITY': cookie})
    if response.status_code == 200: return response.json()["UserID"]
    return None

def GetCsrfToken(cookie):
    response = requests.post("https://friends.roblox.com/v1/users/1/request-friendship", cookies={".ROBLOSECURITY": cookie})
    if response.status_code == 403: return response.headers["x-csrf-token"]
    return None

def GetApiKeyIds(cookie, csrf):
    response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKeys", headers=heads(csrf, cookie), json={
        "cursor": "",
        "limit": 100,
        "reverse": False
    })
    if response.status_code == 200: return response.json()["cloudAuthInfo"]
    return []

def CreateApiKey(cookie, csrf, data):
    return requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", headers=heads(csrf, cookie), json=data, timeout=8)

def DeleteApiKey(cookie, csrf, id):
    return requests.delete(f"https://apis.roblox.com/cloud-authentication/v1/apiKey/{id}", headers=heads(csrf, cookie))

def UploadAsset(apikey, binaryImage, data, proxies=None):
    headers = {"x-api-key": apikey}
    fileContent = {'fileContent': ("091c2383a27d4dcbbefae5be0a5905dd.tampa", binaryImage, "image/png")}
    payload = {"request": json.dumps({
        "assetType": data["assetType"],
        "displayName": data["displayName"],
        "description": data["description"],
        "creationContext": {"creator": {"userId": str(data["userId"])}}
    })}
    try:
        response = requests.post("https://apis.roblox.com/assets/v1/assets", headers=headers, files=fileContent, data=payload, proxies=proxies)
        response.raise_for_status()
        return response, response.json()
    except Exception as e:
        return None, e
    
def GetInventoryV2(userId, assetType, cookie="", cursor=""):
    return requests.get(f"https://inventory.roblox.com/v2/users/{userId}/inventory/{assetType}?limit=100&cursor={cursor}&sortOrder=Asc", cookies={".ROBLOSECURITY": cookie})

def GetAssetThumbnails(assetIds, size, format):
    return requests.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={assetIds}&size={size}&format={format}")

def requestDataScripts(cookie, data):
    # X-BOUND-TOKEN NOT SUPPORTED
    csrf = GetCsrfToken(cookie)
    userId = GetUserId(cookie)
    for request in data:
        if not request["api"] or not request["method"] or not request["json"]:
            print("Forbidden request, ignored.")
            continue
        API = request["api"].replace("-userId-", str(userId))
        JSON = request["json"]
        for key, value in JSON.items():
            if isinstance(value, str):
                JSON[key] = value.replace("-userId-", str(userId))
        RETRY = request["retry"] or False
        CSRF = request["csrf"] or False
        if request["method"] == "POST":
            response = requests.post(API, json=JSON, headers=heads(csrf, cookie))
            if not response.ok and RETRY == True:
                if request["retry_json"]:
                    JSON = request["retry_json"]
                    for key, value in JSON.items():
                        if isinstance(value, str):
                            JSON[key] = value.replace("-userId-", str(userId))
                if CSRF == True:
                    csrf = GetCsrfToken(cookie)
                if request["retries"]:
                    retries = request["retries"]
                    retry = 1
                    while True:
                        print(f"Retrying [{API}]...")
                        response = requests.post(API, json=JSON, headers=heads(csrf, cookie))
                        if response.ok:
                            print(f"Successfully POSTED [{API}]")
                            break
                        retry += 1
                        if retry == retries:
                            print(f"Failed to POST [{API}]")
                            break
                        time.sleep(0.75)
                else:
                    response = requests.post(API, json=JSON, headers=heads(csrf, cookie))
                    if response.ok: print(f"Successfully POSTED [{API}]")
                    else: print(f"Failed to POST [{API}]")
            else:
                print(f"Successfully POSTED [{API}]")
        elif request["method"] == "PATCH":
            response = requests.patch(API, json=JSON, headers=heads(csrf, cookie))
            if not response.ok and RETRY == True:
                if request["retry_json"]:
                    JSON = request["retry_json"]
                    for key, value in JSON.items():
                        if isinstance(value, str):
                            JSON[key] = value.replace("-userId-", str(userId))
                if CSRF == True:
                    csrf = GetCsrfToken(cookie)
                if request["retries"]:
                    retries = request["retries"]
                    retry = 1
                    while True:
                        print(f"Retrying [{API}]...")
                        response = requests.patch(API, json=JSON, headers=heads(csrf, cookie))
                        if response.ok:
                            print(f"Successfully PATCHED [{API}]")
                            break
                        retry += 1
                        if retry == retries:
                            print(f"Failed to PATCH [{API}]")
                            break
                        time.sleep(0.75)
                else:
                    response = requests.patch(API, json=JSON, headers=heads(csrf, cookie))
                    if response.ok: print(f"Successfully PATCHED [{API}]")
                    else: print(f"Failed to PATCH [{API}]")
            else:
                print(f"Successfully PATCHED [{API}]")
    return True

def proxiez():
    proxylist = []
    try:
        with open("proxies.txt", "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                proxy = line.strip()
                proxies = {'http': proxy, 'https': proxy}
                proxylist.append(proxies)
    except FileNotFoundError:
        try:
            proxy_response = requests.get(f'https://api.proxyscrape.com/v2/?request=displayproxies&protocol={random.choices(["http", "https"])}&timeout=9500&country=all&ssl=all&anonymity=all')
            proxy_response.raise_for_status()
            lines = proxy_response.text.splitlines()
            for line in lines:
                proxy_url = line.strip()
                proxies = {'http': proxy_url, 'https': proxy_url}
                proxylist.append(proxies)
            return proxylist
        except Exception as e:
            raise ConnectionError(e)
    if not proxylist:
        raise AssertionError("No proxies available!")
    return proxylist
