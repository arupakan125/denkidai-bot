import argparse
import os
from datetime import datetime, date, timedelta, timezone
import subprocess
import json
import sys
import requests

JST = timezone(timedelta(hours=+9), 'JST')

parser = argparse.ArgumentParser(description='実行日の前日の消費電力量を取得し、SlackへWebhookを用いて通知します。')
parser.add_argument('--username', help="TEPCO Username", default=os.environ.get('TEPCO_WATT_USERNAME'), required=True)
parser.add_argument('--password', help="TEPCO Password", default=os.environ.get('TEPCO_WATT_PASSWORD'), required=True)
parser.add_argument('--webhook', help="Webhook URL", default=os.environ.get('DENKIDAI_WEBHOOK'), required=True)
parser.add_argument('--channel', help="Channel ID", default=os.environ.get('DENKIDAI_CHANNEL_ID'), required=True)
parser.add_argument('--icon', help="ICON URL", default=os.environ.get('DENKIDAI_ICON_URL'), required=True)

args = parser.parse_args()

os.environ['TEPCO_WATT_USERNAME'] = args.username
os.environ['TEPCO_WATT_PASSWORD'] = args.password

yesterday = datetime.now(JST) - timedelta(days=1)
res = json.loads(
        subprocess.check_output(
            ["python3", "tepco-watt-stats.py", str(yesterday.year) + "-" + str(yesterday.month).zfill(2), "--json"],
            encoding="utf-8",
        )
    )

if res["使用量"][-1]["年月日"] == str(yesterday.year) + "/" + str(yesterday.month).zfill(2) + "/" + str(yesterday.day).zfill(2):
    amount_used_yesterday = res["使用量"][-1]["ご使用量"]
else:
    print("Yesterday's data is not available yet.")
    sys.exit(1)

requests.post(args.webhook, data = json.dumps({
    "channel": args.channel,
    "username": "denkidai-bot",
    "icon_url": args.icon,
    "text": str(yesterday.year) + "年" + str(yesterday.month) + "月" + str(yesterday.day) + "日の電気使用量は " + str(amount_used_yesterday) + " kWhでした。",
}))
