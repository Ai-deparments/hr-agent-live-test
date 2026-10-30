"""One question at a time. Only the bot and the group from config.json are reachable.
    python tg.py send bot "kim kech qoldi?"        -> sends, waits for the bot's answers, prints them
    python tg.py send group:8 "yangi nomzodlar"    -> into forum topic 8 of the group
    python tg.py read bot 5  |  python tg.py read group:6 5
Never prints the session or API credentials."""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from telethon import TelegramClient

HERE = Path(__file__).resolve().parent
WAIT = int(os.environ.get("WAIT", 120))


def load() -> dict:
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    cfg["session"] = os.environ.get("TG_SESSION") or str(HERE / "hr_test")
    return cfg


def target(cfg: dict, arg: str) -> tuple[object, int | None]:
    if arg == "bot":
        return cfg["bot"], None
    if arg == "group" or arg.startswith("group:"):
        return int(cfg["group_id"]), int(arg.split(":")[1]) if ":" in arg else None
    sys.exit("Only 'bot' or 'group[:topic]' are allowed")


def show(m) -> str:
    text = m.raw_text or (f"<{type(m.media).__name__}>" if m.media else "<no text: rich message — read it from the bot's storage>")
    return f"[{m.date:%H:%M:%S}] {'ME ' if m.out else 'BOT'} {'file ' if m.file else ''}{text}"


async def main():
    cfg = load()
    async with TelegramClient(cfg["session"], cfg["api_id"], cfg["api_hash"]) as c:
        cmd, where = sys.argv[1], sys.argv[2]
        chat, thread = target(cfg, where)
        ent = await c.get_entity(chat)
        if cmd == "read":
            n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            msgs = await c.get_messages(ent, limit=n, reply_to=thread) if thread else await c.get_messages(ent, limit=n)
            for m in reversed(msgs):
                print(show(m))
            return
        if cmd != "send":
            sys.exit("send | read")
        sent = await c.send_message(ent, sys.argv[3], reply_to=thread)
        print(show(sent))
        me = await c.get_me()
        got, last_new, t0 = [], None, time.time()
        while time.time() - t0 < WAIT:
            await asyncio.sleep(3)
            kw = {"min_id": sent.id, "limit": 20}
            msgs = await c.get_messages(ent, reply_to=thread, **kw) if thread else await c.get_messages(ent, **kw)
            new = [m for m in reversed(msgs) if m.sender_id != me.id and m.id not in {g.id for g in got}]
            for m in new:
                got.append(m)
                print(show(m))
            if new:
                last_new = time.time()
            if got and time.time() - last_new > 8:  # answers stopped coming
                break
        if not got:
            print(f"(no answer in {WAIT}s)")


if __name__ == "__main__":
    asyncio.run(main())
