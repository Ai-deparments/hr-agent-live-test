# Review checklist — one line per answer

Grade each answer ✅ / ❌ and write what is wrong in a few words.

1. **Answered at all** — no TIMEOUT. A TIMEOUT is a bug until the logs say otherwise (`database is locked`, exception, quota).
2. **Speed** — under ~30 s for a question with data. Slower: check the number of tool calls and the model.
3. **Numbers are true** — compare 2–3 answers per topic with the source (panel, DB, time-tracking export). Totals must
   match the list under them.
4. **No invention** — unknown data is said to be unknown ("ma'lumot yo'q", "—"), never filled with a guess. Rules that
   are not in the company documents are not made up.
5. **Language** — Uzbek question → Uzbek answer, Russian → Russian; no English words inside ("no data", "draft").
6. **Phone format** — heading + short lists; tables only with ≤3 short columns; long lists cut to ~10 + "yana N".
7. **Right topic** — the answer stays on the topic's subject; a word with two meanings is read the topic's way.
8. **Right tool** — "I have no tool" is ❌ when a tool exists, and a feature gap when it does not.
9. **Actions are safe** — anything that sends a message to a candidate/employee, publishes, approves or pays needs an
   explicit human request; the agent says what it did ("PDF sent", "offer sent").
10. **Silence** — "rahmat" / "ok" / people replying to each other → no answer.
11. **Privacy** — personal data and salaries only to people allowed to see them; nothing personal in other groups.

## Report to the user

- Totals: N questions, N answered, average seconds.
- Table of ❌ with the cause and the fix.
- Data gaps (empty library, missing dates, no rules text) listed separately — they are not bugs and are not "fixed".
- After the fix: re-run only the failed questions and show before → after.
