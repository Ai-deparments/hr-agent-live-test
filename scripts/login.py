"""One-time login of YOUR Telegram account for bot tests. Run it yourself in a separate terminal:
    python scripts/login.py          # code from Telegram
    python scripts/login.py --qr     # scan a QR: Telegram -> Settings -> Devices -> Link Desktop Device
The code and the 2FA password are typed here, never into a chat with an AI assistant.
Writes config.json (api id/hash + target placeholders) and hr_test.session next to this file — both are gitignored.
Revoke any time: Telegram -> Settings -> Devices -> "HR test" -> Terminate."""
import getpass
import json
import os
import sys
from pathlib import Path

from telethon.sync import TelegramClient

HERE = Path(__file__).resolve().parent
CFG = HERE / "config.json"

print("API ID / API HASH: https://my.telegram.org -> API development tools")
api_id = int(input("API ID: ").strip())
api_hash = getpass.getpass("API HASH (hidden): ").strip()
client = TelegramClient(str(HERE / "hr_test"), api_id, api_hash, device_model="HR test", app_version="1.0")
client.connect()
if not client.is_user_authorized():
    if "--qr" in sys.argv:
        qr = client.qr_login()
        try:
            import qrcode
            q = qrcode.QRCode(border=1)
            q.add_data(qr.url)
            q.print_ascii(invert=True)
        except ImportError:
            print("pip install qrcode[pil] to see the QR here; or open this on another device:", qr.url)
        print("Scan: Telegram -> Settings -> Devices -> Link Desktop Device")
        try:
            qr.wait(120)
        except Exception as e:  # 2FA enabled
            if "password" not in str(e).lower() and "SessionPasswordNeeded" not in type(e).__name__:
                raise
            client.sign_in(password=getpass.getpass("2FA password: "))
    else:
        client.start(phone=lambda: input("Phone (+998…): ").strip(), code_callback=lambda: input("Code: ").strip(),
                     password=lambda: getpass.getpass("2FA password (if any): "))
me = client.get_me()
client.disconnect()

cfg = json.loads(CFG.read_text()) if CFG.exists() else {"bot": "your_bot_username", "group_id": 0, "topics": {}}
cfg.update(api_id=api_id, api_hash=api_hash)
CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
if os.name == "nt":  # only this Windows user can read the folder
    os.system(f'icacls "{HERE}" /inheritance:r /grant:r "%USERNAME%:(OI)(CI)F" >nul')
print(f"\nDone: {me.first_name}. Now set bot / group_id / topics in {CFG}")
