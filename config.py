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

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
