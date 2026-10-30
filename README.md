# hr-agent-live-test

Claude Code / agent skill: **live test of a Telegram HR agent bot** from the owner's own account. Batches of real
questions go to the bot's private chat and to every forum topic of the HR group, one at a time; the answers are
collected, graded with a checklist, failures are fixed and only the failed questions are re-run.

## O'zbekcha

Telegram HR-agent botini **egasining akkauntidan jonli tekshirish** uchun skill. Bot chatiga va HR guruhining har bir
mavzusiga haqiqiy savollar ketma-ket yuboriladi, javoblar yig'iladi va ro'yxat bo'yicha baholanadi: tezlik, raqamlar
to'g'riligi, til, o'ylab topilmaganmi, telefon uchun format, to'g'ri mavzu, to'g'ri vosita. Xatolar tuzatiladi va faqat
xato chiqqan savollar qayta yuboriladi.

- `SKILL.md` — ish tartibi: xavfsizlik, sozlash, savollar, ishga tushirish, baholash, qayta tekshirish.
- `questions/hr-uz-ru.json` — 64 savol (oylik, tahlil, HR boshlig'i / davomat, rekruter, onboarding, bot chati).
- `scripts/` — `login.py` (kirish: kod yoki QR), `tg.py` (bitta savol), `batch.py` (to'plam).
- `references/review-checklist.md` — har bir javob uchun tekshiruv ro'yxati.

**Xavfsizlik:** API orqali kirish akkauntga to'liq kirish beradi. Kod va 2FA parolni faqat o'zingiz, o'z terminalingizda
kiritasiz; sessiya fayli va `config.json` faqat kompyuteringizda qoladi (`.gitignore`). Skriptlar faqat `config.json`
dagi bot va guruhga yoza oladi. O'chirish: Telegram → Sozlamalar → Qurilmalar → «HR test».

## Русский

Скилл для **живого теста Telegram-бота HR-агента с аккаунта владельца**. Настоящие вопросы по очереди уходят в чат с
ботом и в каждую тему HR-группы, ответы собираются и проверяются по чек-листу: скорость, верные цифры, язык,
ничего не выдумано, формат под телефон, нужная тема, нужный инструмент. Ошибки исправляются, повторно отправляются
только вопросы с ошибками.

**Безопасность:** вход через API = полный доступ к аккаунту. Код и пароль 2FA вводите только сами в своём терминале;
файл сессии и `config.json` остаются на вашем компьютере (в `.gitignore`). Скрипты пишут только в бота и группу из
`config.json`. Отключить: Telegram → Настройки → Устройства → «HR test».

## Quick start

```bash
pip install telethon "qrcode[pil]"
python scripts/login.py --qr            # run it yourself; writes scripts/config.json + hr_test.session
# edit scripts/config.json: bot, group_id, topics (see scripts/config.example.json)
cp questions/hr-uz-ru.json questions.json   # replace <XODIM> / <VAKANSIYA>
python scripts/batch.py                 # or: python scripts/batch.py recruiter onboarding
```

Install as a Claude Code skill: copy this folder to `~/.claude/skills/hr-agent-live-test`.

Made while testing the HR agents of [hr-agents-kit](https://github.com/Ai-deparments/hr-agents-kit). MIT license.
