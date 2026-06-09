import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Journal Settings
JOURNAL_DOMAIN = "mijournals.com"
JOURNAL_PATH = "/Human_Studies/article/view/"

# Vercel serverless: faqat /tmp yozishga ruxsat
if os.environ.get("VERCEL"):
    OUTPUT_DIR = "/tmp/output"
    DB_FILENAME = "/tmp/certificates.db"
else:
    OUTPUT_DIR = "output"
    DB_FILENAME = "certificates.db"

# Human Studies journal
TEMPLATE_FILENAME = "template_human_studies.png"
# International Conference on Social Sciences and Humanities Research
TEMPLATE_ICSSHR = "template_human_studies2.png"
# Virginia EduLab journal
TEMPLATE_VEL = "template_vel.png"
# Journal of Social and Theological Studies
TEMPLATE_JSTS = "template_jsts.png"

# =====================================================================
# JURNALLAR RO'YXATI
# Yangi jurnal qo'shish uchun shu lug'atga bitta yozuv qo'shing:
#   "path"     — mijournals.com dagi maqola yo'li (article/view/ gacha)
#   "name"     — sertifikat va xabarlarda ko'rinadigan jurnal nomi
#   "prefix"   — Certificate ID prefiksi (masalan VEL → VEL-2026-000001)
#   "generator"— certificate_generator.py dagi qaysi funksiya ishlatiladi
# Eslatma: Human Studies ichida konferensiya (ICSSHR) bo'limi avtomatik
#          aniqlanadi (ojs_parser.py dagi section nomiga qarab).
# =====================================================================
JOURNALS = {
    "human_studies": {
        "path": "/Human_Studies/article/view/",
        "name": "Human Studies",
        "prefix": "MIHS",
        "generator": "human_studies",  # journal/conference avtomatik aniqlanadi
    },
    "vel": {
        "path": "/vel/article/view/",
        "name": "Virginia EduLab",
        "prefix": "VEL",
        "generator": "vel",
    },
    "jsts": {
        "path": "/jsts/article/view/",
        "name": "Journal of Social and Theological Studies",
        "prefix": "JSTS",
        "generator": "jsts",
    },
}

# Konferensiya (Human Studies ichidagi maxsus bo'lim) uchun prefiks
CONFERENCE_PREFIX = "ICSSHR"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
