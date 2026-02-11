# GitHub ga yuklash

## 1. GitHub da yangi repository yarating

1. **GitHub sahifasi ochiq** bo‘lsa, **New** (yoki **+** → **New repository**) bosing.
2. **Repository name:** `Sertifikatlar` (yoki xohlagan nom).
3. **Public** tanlang.
4. **README, .gitignore, license qo‘shmang** — "Create repository" bosing (bo‘sh repo).

## 2. Lokal loyihani GitHub ga ulash va push

Repository yaratilgach, GitHub sizga ko‘rsatadigan **URL** dan foydalaning. Quyidagilarni **PowerShell** yoki **CMD** da loyiha papkasida ishlating (USERNAME o‘rniga o‘zingizning GitHub username yozing):

```bash
cd c:\Users\PC\Documents\Sertifikatlar

git remote add origin https://github.com/USERNAME/Sertifikatlar.git
git branch -M main
git push -u origin main
```

Agar repo nomi boshqacha bo‘lsa (masalan `certificate-bot`), URL shunday bo‘ladi:
`https://github.com/USERNAME/certificate-bot.git`

---

**GitHubda login qilmagan bo‘lsangiz:**  
`git push` paytida brauzer ochiladi yoki username/token so‘raydi. GitHub → Settings → Developer settings → Personal access tokens orqali token yaratib parol o‘rniga ishlatishingiz mumkin.
