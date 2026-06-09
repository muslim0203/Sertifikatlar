import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_IDS, JOURNALS, CONFERENCE_PREFIX
from db import init_db, get_next_certificate_id, save_certificate
from ojs_parser import validate_url, extract_metadata
from certificate_generator import (
    generate_certificate,
    generate_certificate_icsshr,
    generate_certificate_vel,
    generate_certificate_jsts,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Bot and Dispatcher (Vercelda BOT_TOKEN env da bo'lishi kerak)
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()
if not BOT_TOKEN:
    logger.warning("BOT_TOKEN is not set. Vercel: Settings → Environment Variables da qo'shing.")

# Handlers

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "Welcome! Send me an article link from mijournals.com — supported journals:\n"
        "• Human Studies (/Human_Studies/) — Journal & Conference (ICSSHR)\n"
        "• Virginia EduLab (/vel/)\n"
        "• Journal of Social and Theological Studies (/jsts/)\n\n"
        "I will detect the journal automatically and send the matching certificate for each author."
    )

@dp.message(Command("ping"))
async def cmd_ping(message: types.Message):
    """Tekshirish: bot javob beryaptimi."""
    await message.reply("pong")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply(
        "Send an article URL, e.g.:\n"
        "https://mijournals.com/Human_Studies/article/view/90\n"
        "https://mijournals.com/vel/article/view/240\n\n"
        "• Human Studies article → Human Studies certificate.\n"
        "• Conference (ICSSHR) article → Conference certificate.\n"
        "• Virginia EduLab article → Virginia EduLab certificate."
    )

@dp.message(F.text)
async def process_url(message: types.Message):
    url = (message.text or "").strip()
    if not url:
        return

    # Darhol javob — foydalanuvchi link yuborilganini ko'rsin
    try:
        status_msg = await message.reply("Link qabul qilindi, qayta ishlanmoqda...")
    except Exception:
        status_msg = None

    try:
        # 1. Validate URL
        if not validate_url(url):
            await (status_msg.edit_text if status_msg else message.reply)(
                "Invalid OJS link. Please send a valid article URL from mijournals.com/Human_Studies/"
            )
            return

        # 2. Extract Metadata
        if status_msg:
            await status_msg.edit_text("Sahifa yuklanmoqda...")
        metadata = extract_metadata(url)

        if not metadata:
            await (status_msg.edit_text if status_msg else message.reply)(
                "Could not see article metadata. Please check the link."
            )
            return

        authors = metadata.get('authors', [])
        if not authors:
            await (status_msg.edit_text if status_msg else message.reply)(
                "No authors found on this article page."
            )
            return

        title = metadata.get('title', 'Untitled')
        date = metadata.get('date', '')
        doi = metadata.get('doi')
        is_conference = metadata.get('is_conference', False)
        journal_key = metadata.get('journal_key')
        journal_conf = JOURNALS.get(journal_key, {})

        # Qaysi sertifikat generatori, prefiks va nom ishlatiladi
        if is_conference:
            # Human Studies ichidagi konferensiya bo'limi (ICSSHR)
            cert_prefix = CONFERENCE_PREFIX
            generate_fn = generate_certificate_icsshr
            cert_type = "Conference (ICSSHR)"
        elif journal_key == "vel":
            cert_prefix = journal_conf.get("prefix", "VEL")
            generate_fn = generate_certificate_vel
            cert_type = f"Journal ({journal_conf.get('name', 'Virginia EduLab')})"
        elif journal_key == "jsts":
            cert_prefix = journal_conf.get("prefix", "JSTS")
            generate_fn = generate_certificate_jsts
            cert_type = f"Journal ({journal_conf.get('name', 'Journal of Social and Theological Studies')})"
        else:
            # Human Studies (default jurnal) yoki boshqa
            cert_prefix = journal_conf.get("prefix", "MIHS")
            generate_fn = generate_certificate
            cert_type = f"Journal ({journal_conf.get('name', 'Human Studies')})"

        await (status_msg.edit_text if status_msg else message.reply)(
            f"Found: {title}\nAuthors: {', '.join(authors)}\nType: {cert_type}\nGenerating certificates..."
        )

        # 3. Generate Certificates
        generated_files = []

        for author in authors:
            cert_id = get_next_certificate_id(prefix=cert_prefix)
            save_certificate(cert_id, author, title)
            pdf_path = generate_fn(author, title, date, cert_id, doi=doi)
            generated_files.append((author, pdf_path))

        for author, pdf_path in generated_files:
            file_to_send = FSInputFile(pdf_path)
            await message.reply_document(file_to_send, caption=f"Certificate for {author} ({cert_type})")

    except Exception as e:
        logger.exception("process_url error")
        err_msg = str(e)[:400]
        try:
            await message.reply(f"Xatolik: {err_msg}\n\nVercel Logs da batafsil ko'ring.")
        except Exception:
            pass

async def main():
    # Initialize DB
    init_db()
    
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
