"""Batch test: questions per forum topic (or the bot's private chat), one at a time — the next one only after the bot
answered (or WAIT seconds passed). Prints: topic | seconds | OK/TIMEOUT | question. Read rich answers from the bot's storage.
    python batch.py              # all topics in questions.json
    python batch.py 8 10         # only these topics ("bot" = private chat)
    RETEST=1 python batch.py     # only retest.json: [["8", "question"], ...]
    TG_SESSION=path/copy python batch.py 10   # second session file for a parallel run"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from telethon import TelegramClient

from tg import HERE, load

WAIT = int(os.environ.get("WAIT", 150))


def plan() -> list[tuple[str, str]]:
    if os.environ.get("RETEST"):
        return [(str(t), q) for t, q in json.loads((HERE.parent / "retest.json").read_text(encoding="utf-8"))]
    qs = json.loads((HERE.parent / "questions.json").read_text(encoding="utf-8"))
    only = sys.argv[1:] or [k for k in qs if not k.startswith("_")]  # "_silence" etc. are run by hand with tg.py
    out = [(t, q) for t in only for q in qs[t]]
    if any("<" in q and ">" in q for _, q in out):
        sys.exit("Replace the <XODIM> / <VAKANSIYA> placeholders in questions.json with real names first")
    return out


async def main():
    cfg = load()
    async with TelegramClient(cfg["session"], cfg["api_id"], cfg["api_hash"]) as c:
        me = await c.get_me()
        group = await c.get_entity(int(cfg["group_id"])) if cfg.get("group_id") else None
        bot = await c.get_entity(cfg["bot"])
        by_name = {v: k for k, v in cfg.get("topics", {}).items()}  # "payroll" -> "2"
        for topic, q in plan():
            topic = by_name.get(topic, topic)
            if topic != "bot" and not topic.isdigit():
                sys.exit(f"Unknown topic '{topic}': add it to config.json 'topics' as {{\"<id>\": \"{topic}\"}}")
            ent, thread = (bot, None) if topic == "bot" else (group, int(topic))
            sent = await c.send_message(ent, q, reply_to=thread)
            t0, ok = time.time(), False
            while time.time() - t0 < WAIT:
                await asyncio.sleep(3)
                kw = {"min_id": sent.id, "limit": 10}
                msgs = await c.get_messages(ent, reply_to=thread, **kw) if thread else await c.get_messages(ent, **kw)
                if any(m.sender_id != me.id for m in msgs):
                    ok = True
                    break
            name = cfg.get("topics", {}).get(topic, topic)
            print(f"{name:>12} | {time.time() - t0:5.0f}s | {'OK     ' if ok else 'TIMEOUT'} | {q}", flush=True)
            await asyncio.sleep(4)


if __name__ == "__main__":
    asyncio.run(main())
