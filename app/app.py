from datetime import datetime, date, timedelta, timezone
import time
import schedule
import subprocess
import json
import os
import requests

SLACK_URL = os.getenv("SLACK_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ICON_URL = os.getenv("ICON_URL")
JST = timezone(timedelta(hours=+9), 'JST')

def daily_job():
    yesterday = datetime.now(JST) - timedelta(days=1)
    res = json.loads(
            subprocess.check_output(["python3", "tepco-watt-stats.py", str(yesterday.year) + "-" + str(yesterday.month).zfill(2), "--json"], encoding="utf-8")
        )
    amount_used_yesterday = res["使用量"][-1]["ご使用量"]
    

    requests.post(SLACK_URL, data = json.dumps({
        "channel": CHANNEL_ID,
        "username": "denkidai-bot",
        "icon_url": ICON_URL,
        "text": str(yesterday.year) + "年" + str(yesterday.month) + "月" + str(yesterday.day) + "日の電気使用量は " + str(amount_used_yesterday) + " kWhでした。",
    }))


# 21:00 UTC is 06:00 JST
schedule.every().day.at("21:00").do(daily_job)

print("starting...")

while True:
    schedule.run_pending()
    time.sleep(1)
