import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_IDS
from db import init_db, get_next_certificate_id, save_certificate
from ojs_parser import validate_url, extract_metadata
from certificate_generator import generate_certificate, generate_certificate_icsshr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Bot and Dispatcher
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set in .env or config.py")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Handlers

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "Welcome! Send me an article link from mijournals.com/Human_Studies/ — "
        "I will detect whether it is a Journal or Conference article and send the matching certificate for each author."
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply(
        "Send an article URL, e.g.:\n"
        "https://mijournals.com/Human_Studies/article/view/90\n\n"
        "• Journal articles → Journal certificate (1st template).\n"
        "• Conference articles (International Conference on Social Sciences and Humanities Research) → Conference certificate (2nd template)."
    )

@dp.message(F.text)
async def process_url(message: types.Message):
    url = message.text.strip()
    
    # 1. Validate URL
    if not validate_url(url):
        await message.reply("Invalid OJS link. Please send a valid article URL from mijournals.com/Human_Studies/")
        return

    # 2. Extract Metadata
    status_msg = await message.reply("Processing link... Please wait.")
    
    try:
        metadata = extract_metadata(url)
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        metadata = None
        
    if not metadata:
        await status_msg.edit_text("Could not see article metadata. Please check the link.")
        return
        
    authors = metadata.get('authors', [])
    if not authors:
        await status_msg.edit_text("No authors found on this article page.")
        return
        
    title = metadata.get('title', 'Untitled')
    date = metadata.get('date', '')
    doi = metadata.get('doi')
    is_conference = metadata.get('is_conference', False)

    cert_type = "Conference (ICSSHR)" if is_conference else "Journal (Human Studies)"
    await status_msg.edit_text(
        f"Found: {title}\nAuthors: {', '.join(authors)}\nType: {cert_type}\nGenerating certificates..."
    )

    # 3. Generate Certificates — jurnal uchun 1-shablon, konferensiya uchun 2-shablon
    generated_files = []
    cert_prefix = "ICSSHR" if is_conference else "MIHS"
    generate_fn = generate_certificate_icsshr if is_conference else generate_certificate

    try:
        for author in authors:
            cert_id = get_next_certificate_id(prefix=cert_prefix)
            save_certificate(cert_id, author, title)
            pdf_path = generate_fn(author, title, date, cert_id, doi=doi)
            generated_files.append((author, pdf_path))

        # 4. Send Files
        for author, pdf_path in generated_files:
            file_to_send = FSInputFile(pdf_path)
            await message.reply_document(file_to_send, caption=f"Certificate for {author} ({cert_type})")
            
    except Exception as e:
        logger.error(f"Generation error: {e}")
        await message.reply("An error occurred while generating certificates.")
        
    # Cleanup? 
    # User requirement: "Also save generated PDFs in a local folder: /output"
    # So we keeping them. No cleanup needed.

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
