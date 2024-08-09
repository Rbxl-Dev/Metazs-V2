# script is part of version '091c2383a27d4dcbbefae5be0a5905dd' by © BitsProxy

from threading import Thread
from robfuncs import *
import time
import os

VERSION = "091c2383a27d4dcbbefae5be0a5905dd"

def saveToAssetsFile(content, userId):
    if not os.path.exists(os.path.join(os.getcwd(), f"output\\{VERSION}\\assets")):
        os.makedirs(os.path.join(os.getcwd(), f"output\\{VERSION}\\assets"))
    with open(os.path.join(os.getcwd(), f"output\\{VERSION}\\assets", f"{userId}.txt"), 'a') as file:
        file.write(f"{content}\n")

def addToPending(content):
    with open(os.path.join(os.getcwd(), "output", "pending.txt"), 'a') as file:
        file.write(f"https://www.roblox.com/library/{content}\n")

def sendToDiscord(webhook, assetInfo, userId):
    randomColor = random.randint(0, 0xFFFFFF)
    data = {
        "content": "",
        "embeds": [
            {
                "title": "Asset Information",
                "fields": [
                    {
                        "name": "Asset Id",
                        "value": f"[{assetInfo["targetId"]}](https://www.roblox.com/library/{assetInfo["targetId"]})",
                        "inline": True
                    },
                    {
                        "name": "Created By",
                        "value": f"[{userId}](https://www.roblox.com/users/{userId})",
                        "inline": True
                    }
                ],
                "image": {
                    "url": assetInfo["imageUrl"]
                },
                "color": randomColor
            }
        ]
    }
    response = requests.post(webhook, json=data)
    if response.status_code == 204:
        print(f"\033[32mSuccessfully sent {assetInfo["targetId"]} to webhook\033[0m")
    else:
        time.sleep(1.25)
        return sendToDiscord(webhook, assetInfo, userId)

def getImageId(assetId, position=8):
    url = f"https://assetdelivery.roblox.com/v1/asset/?id={assetId}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            xml_data = response.text
            imageId = EXTRACTIMAGEID(xml_data, position)
            return imageId
        else:
            return None
    except Exception as e:
        return None

def EXTRACTIMAGEID(xml_data, pos):
    try:
        start_tag = '<Content>'
        end_tag = '</Content>'
        start_idx = xml_data.find(start_tag) + len(start_tag)
        end_idx = xml_data.find(end_tag)
        
        if start_idx == -1 or end_idx == -1:
            return None
        
        content_url = xml_data[start_idx:end_idx].strip()

        if '=' in content_url:
            imageId = content_url.split('=')[pos].replace("</url>", "")
            return imageId
        else:
            return None
    except Exception as e:
        return None
if __name__ == "__main__":
    cookie = input("\033[35mCookie (not required for public inventories): \033[0m")
    userId = input("\033[35mUserId: \033[0m")
    webhook = input("\033[35mWebhook (Not Required type 'n'): \033[0m")
    assetType = input("\033[35mAsset Type: \033[0m").lower()
    if assetType.startswith("d"): assetType = 13
    elif assetType.startswith("t"): assetType = 2
    else: assetType = 13
    accepted = []
    assets = []
    cursor = ""
    def assetsAdd(assetId, position):
        assets.append(getImageId(assetId, position))
    while True:
        response = GetInventoryV2(userId, assetType, cookie, cursor)
        threads = []
        if response.json()["data"]:
            for asset in response.json()["data"]:
                thread = Thread(target=assetsAdd, args=(asset["assetId"], 12 if assetType == 13 else 8,))
                thread.start()
                threads.append(thread)
        for thread in threads:
            thread.join()
        else:
            time.sleep(3)
            response = GetInventoryV2(userId, assetType, cookie, cursor)
            threads2 = []
            if response.json()["data"]:
                for asset in response.json()["data"]:
                    thread = Thread(target=assetsAdd, args=(asset["assetId"], 12 if assetType == 13 else 8,))
                    thread.start()
                    threads2.append(thread)
            for thread in threads2:
                thread.join()
        if response.json()["nextPageCursor"]:
            cursor = response.json()["nextPageCursor"]
        else:
            break
        time.sleep(1)
    for i in range(0, len(assets), 100):
        print(f"Ranging {i}-{i+100} / {len(assets)}")
        batch = assets[i:i+100]
        assets_str = ','.join(batch)
        for _ in range(3):
            response = GetAssetThumbnails(assets_str, "420x420", "Png")
            if _ == 2 and response.json()["data"]:
                for info in response.json()["data"]:
                    if info["state"] == "Completed":
                        accepted.append(info)
                    elif info["state"] == "Pending":
                        addToPending(info["targetId"])
            time.sleep(0.75)
    for asset in accepted:
        print(info)
        saveToAssetsFile(f"https://www.roblox.com/library/{asset["targetId"]}", userId)
    if webhook.startswith("https://discord.com/"):
        for asset in accepted:
            sendToDiscord(webhook, asset, userId)
            time.sleep(1.25)
    print(f"Finished inventory checking {userId}.")
