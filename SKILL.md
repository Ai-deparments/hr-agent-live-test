---
name: hr-agent-live-test
description: Live-test a Telegram HR agent bot from the owner's own account — send batches of real questions (Uzbek/Russian) to the bot's private chat and to each forum topic of the HR group, wait for every answer, collect them, grade them with a checklist (speed, numbers, language, honesty, phone format, right topic, right tool), fix what failed and re-run only the failed questions. Use when the user asks to "test the bot", "agentni tekshir", "задай вопросы в каждой теме", "10-15 savol har bir mavzuda", "прогони вопросы", or after deploying a new agent feature.
---

# HR agent live test

Real questions through the real Telegram client find what unit tests miss: lost answers under load, missing tools,
wrong topic, stale chat memory, wrong language, wide tables on a phone.

## 0. Safety first (say this to the user in full prose)

Logging in with the Telegram API gives **full access to the account**. So:
- the user types the login code / 2FA password **in their own terminal**, never into the chat;
- the session file and `config.json` stay on the user's machine (gitignored), never on a server or in git;
- `scripts/tg.py` and `scripts/batch.py` can reach **only** the bot and the group from `config.json`;
- revoke any time: Telegram → Settings → Devices → terminate "HR test".
- The questions are visible to everyone in the group — tell the user before a big batch.

## 1. Setup (once)

1. `pip install telethon` (+ `qrcode[pil]` for QR login).
2. API ID / HASH: https://my.telegram.org → API development tools (App title any, Platform Desktop).
3. The user runs in their own PowerShell/terminal: `python scripts/login.py` (phone code) or `python scripts/login.py --qr`
   (scan in Telegram → Settings → Devices → Link Desktop Device). It writes `config.json` + `hr_test.session` next to the scripts.
4. Fill the target in `config.json`: `"bot": "your_bot_username"`, `"group_id": -100…`, and `"topics": {"2": "payroll", …}`.
   Topic ids: open a topic link `t.me/c/<id>/<topic>`; the number after the last `/` is the topic id.

## 2. Questions

`questions.json` (repo root) maps a topic — its id, its role name from `config.json` `topics`, or `"bot"` for the private
chat — to a list of questions. Copy `questions/hr-uz-ru.json` to `questions.json` and replace the `<XODIM>` /
`<VAKANSIYA>` placeholders (the batch refuses to run with them). The file has 64 HR questions (bot chat + payroll, analytics, head of HR / attendance, recruiter, onboarding);
adapt names to real employees. Per topic mix: facts with numbers, a person by name, a "how do I…" question,
one Russian question, one action ("prepare a certificate for X") and one question that belongs to another topic.
Silence checks (`_silence` list) are run by hand: `WAIT=30 python scripts/tg.py send group:8 "rahmat"` must end with
"(no answer…)"; also reply to another human's message — the bot must stay silent.

## 3. Run

```
python scripts/batch.py                      # every topic in questions.json, one question at a time
python scripts/batch.py 8 10                 # only topics 8 and 10
RETEST=1 python scripts/batch.py             # only the questions listed in retest.json
python scripts/tg.py send bot "bugun kim kech qoldi?"   # one question, prints the answers
python scripts/tg.py read group:6 5
```
The next question is sent only after the bot answered the previous one (or after `WAIT` seconds → `TIMEOUT`).
Two batches in parallel need two session files (copy the `.session`): one file cannot be used by two processes.
Parallel runs are also a good load test — that is how "database is locked" was found.

## 4. Collect the answers

Bots that answer with Telegram **rich messages** (`sendRichMessage`) show up as `<no text: rich…>` in Telethon.
Then read the answers where the bot stores them (e.g. its `chat_messages` table over ssh, read-only:
`sqlite3 "file:/path/hr.db?mode=ro" "select …"`). Otherwise the printed text is enough.

## 5. Grade every answer — `references/review-checklist.md`

Table per topic: question · seconds · ✅/❌ · what is wrong. Typical failures and their fixes:

| Symptom | Usual cause | Fix |
|---|---|---|
| TIMEOUT, log says `database is locked` | SQLite without WAL under parallel writes | `PRAGMA journal_mode=WAL`, `busy_timeout` |
| "I have no tool for that" | the agent really lacks a tool | add a small read-only tool (or an action tool with role check) |
| Totals contradict the list | tool returns a filtered list without saying so | add `note` + the missing group to the tool output |
| Old wrong number repeated | shared topic memory keeps the earlier answer | fix the data; memory heals on the next answers |
| Answer about the wrong thing | ambiguous word ("suhbat" = interview vs onboarding talk) | one line in the persona that separates them |
| English words in Uzbek/Russian | model fallback ("no data", "draft") | persona rule with the local words |
| Wide table on a phone | Markdown table with 4+ columns | lists, max 3 short columns |
| "How do I…" → "I can't" | agent does not know the UI | persona: panel section names for each how-to |

## 6. Fix → deploy → re-run only the failed questions

Put the failed ones into `retest.json` and run `RETEST=1`. Report to the user: before/after table, what was fixed,
what is a data gap (empty library, missing hire date) rather than a bug. Never present a data gap as fixed.
