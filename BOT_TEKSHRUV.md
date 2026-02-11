# Bot ishlamasa tekshirish

## 1. Status sahifasini oching

Brauzerda: **https://sertifikatlar.vercel.app/api/status**

- **`BOT_TOKEN not set`** chiqsa → Vercel’da token qo‘shilmagan.
- **`webhook_url: ""`** (bo‘sh) chiqsa → Webhook o‘rnatilmagan.
- **`webhook_ok: true`** chiqsa → Sozlama to‘g‘ri, bot ishlashi kerak.

## 2. BOT_TOKEN qo‘shish (Vercel)

1. [vercel.com](https://vercel.com) → **Sertifikatlar** loyihasi.
2. **Settings** → **Environment Variables**.
3. **Name:** `BOT_TOKEN`, **Value:** Telegram’dan olingan token (masalan `123456:ABC-DEF...`).
4. **Save** → **Redeploy** (Deployments → ... → Redeploy).

## 3. Webhook o‘rnatish

Token qo‘shilgach, brauzerda quyidagi linkni oching (TOKEN o‘rniga haqiqiy token yozing):

```
https://api.telegram.org/botTOKEN/setWebhook?url=https://sertifikatlar.vercel.app/api/webhook
```

Javobda `{"ok":true}` bo‘lishi kerak.

## 4. Tekshirish

- **/api/status** ni qayta oching — `webhook_url` endi `https://sertifikatlar.vercel.app/api/webhook` ko‘rinishi kerak.
- Telegram’da botga **/start** yoki **/ping** yuboring — javob kelishi kerak (/ping → "pong").

## 5. Yana ham javob bo‘lmasa

- Vercel → **Sertifikatlar** → **Logs** (yoki **Runtime Logs**). Telegram’da /ping yuborganingizdan keyin "Webhook: received update" ko‘rinishi kerak. Ko‘rinmasa — Telegram yangilanishlarni boshqa URL ga yubormoqda (webhook noto‘g‘ri). Ko‘rinsa lekin xatolik bo‘lsa — xato matnini o‘qing.
- Agar bot **"Xatolik: ..."** xabarini yuborsa — shu matnni Vercel Logs bilan solishtiring.
