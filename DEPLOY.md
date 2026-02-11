# Vercelga deploy qilish

Bot Telegram **webhook** rejimida ishlaydi (polling emas). Quyidagi qadamlarni bajarishingiz kifoya.

## 0. Vercel CLI orqali (Git siz)

Agar Git ishlatmasangiz, loyiha papkasida:

```bash
npm i -g vercel
vercel
```

So‘ng Environment Variables ni Vercel dashboard da qo‘shing: `BOT_TOKEN`, `ADMIN_IDS` (ixtiyoriy). Keyin 3- va 4-qadamlar (webhook + tekshirish).

## 1. Loyihani Git orqali ulash

Vercel odatda GitHub / GitLab / Bitbucket orqali deploy qiladi.

```bash
cd c:\Users\PC\Documents\Sertifikatlar
git init
git add .
git commit -m "Vercel webhook bot"
# GitHub da repo yarating va:
git remote add origin https://github.com/USERNAME/Sertifikatlar.git
git push -u origin main
```

## 2. Vercelda loyiha yaratish

1. [vercel.com](https://vercel.com) ga kiring va GitHub bilan login qiling.
2. **Add New** → **Project**.
3. `Sertifikatlar` reponi tanlang, **Import** bosing.
4. **Environment Variables** qo‘shing:
   - `BOT_TOKEN` — Telegram bot token (@BotFather dan).
   - `ADMIN_IDS` — ixtiyoriy, vergul bilan ajratilgan admin ID lar (masalan: `123456789`).
5. **Deploy** bosing.

## 3. Webhook o‘rnatish

Deploy tugagach, sizga URL beriladi, masalan:  
`https://sertifikatlar-xxx.vercel.app`

Quyidagi URL ni o‘zingizning domeningiz bilan almashtiring va brauzerda bir marta oching (yoki curl bilan):

```
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://SIZNING-DOMAIN.vercel.app/api/webhook
```

Misol (BOT_TOKEN o‘rniga haqiqiy token yozing):

```
https://api.telegram.org/bot123456:ABC-DEF/setWebhook?url=https://sertifikatlar-xxx.vercel.app/api/webhook
```

Brauzerda `{"ok":true}` chiqsa, webhook o‘rnatilgan.

## 4. Tekshirish

- Botga Telegram da `/start` yuboring — javob kelsa, deploy ishlayapti.
- Sertifikat kerak bo‘lgan maqola linkini yuborib ham tekshirishingiz mumkin.

## Eslatmalar

- **SQLite** Vercelda faqat `/tmp` da ishlaydi va **saqlanmaydi** (har so‘rov yangi muhit bo‘lishi mumkin). Certificate ID lar vaqtincha bo‘ladi. Doimiy saqlash uchun keyinroq Vercel Postgres yoki boshqa DB ulashingiz mumkin.
- **Shablonlar** (`template_human_studies.png`, `template_human_studies2.png`) va **font** (`unicode.corsiva.ttf`, `CORSIVA_BOLD_ITALIC.TTF`) loyihada qolishi kerak — ular avtomatik deploy qilinadi.
- Lokalda eski usulda (polling) ishlatish uchun: `python main.py` — bu holda `VERCEL` o‘rnatilmaydi va `output/` va `certificates.db` joyida ishlaydi.
