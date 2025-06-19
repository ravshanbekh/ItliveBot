import asyncio, logging, sys
import sqlite3
import datetime
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from openai import OpenAI
from langdetect import detect

# OpenAI API sozlamalari
api = "sk-il8U3j-Bk5siRro15gJPikS2ZP3GmRkOsrCbqxMXvuqnv7Hj2joQQSzjtboXStyjAE1tWZUDBaRITnI2aOnPpA"
TOKEN = "7722450945:AAHsyQe_f3rJyePWUCBjGPx-9pmVTenm0l4"

client = OpenAI(
    base_url="https://api.langdock.com/openai/eu/v1",
    api_key=api
)

dp = Dispatcher()
DB_NAME = "database.db"

BOT_SYSTEM_PROMPT = """
You are a helpful, polite and knowledgeable assistant.
Always respond clearly and concisely.
If you do not know the answer, say "I'm not sure about that." Do not invent answers.
When user uploads an image, analyze and describe it.
"""

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT,
            total_messages INTEGER DEFAULT 0,
            last_active TEXT
        )
    """)
    conn.commit()
    conn.close()

def update_user_info(user):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    if cursor.fetchone():
        cursor.execute("""
            UPDATE users SET 
            total_messages = total_messages + 1,
            last_active = ?
            WHERE user_id = ?
        """, (datetime.datetime.now().isoformat(), user.id))
    else:
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, language, total_messages, last_active)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        """, (user.id, user.username, user.first_name, user.last_name, user.language_code, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def search_database(question):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM faq WHERE question LIKE ?", (f"%{question}%",))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def save_to_history(user_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                   (user_id, role, content, timestamp))
    conn.commit()
    conn.close()

def load_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    messages = []
    for role, content in reversed(rows):
        messages.append({"role": role, "content": content})
    return messages

def detect_language(text):
    try:
        lang_code = detect(text)
        if lang_code.startswith('uz'):
            return 'uzbek'
        elif lang_code.startswith('ru'):
            return 'russian'
        elif lang_code.startswith('en'):
            return 'english'
        else:
            return 'english'
    except:
        return 'english'

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="reset", description="Suhbatni yangilash"),
        BotCommand(command="draw", description="Rasm yaratish (AI)"),
        BotCommand(command="stats", description="Statistikani ko‘rish (admin)"),
    ]
    await bot.set_my_commands(commands)

@dp.message(Command(commands="start"))
async def start(message: Message):
    await message.chat.do("typing")
    update_user_info(message.from_user)
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}! Savolingizni yozing yoki rasm yuboring.")

@dp.message(Command(commands="help"))
async def help_command(message: Message):
    await message.answer("Men sizga yordam beraman. Matn, rasm va multimodal savollarni qabul qilaman.")

@dp.message(Command(commands="reset"))
async def reset_command(message: Message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()
    await message.answer("Suhbat yangilandi.")

@dp.message(Command(commands="stats"))
async def stats_command(message: Message):
    if message.from_user.id != YOUR_TELEGRAM_USER_ID:
        await message.answer("Siz admin emassiz.")
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total_messages) FROM users")
    total_messages = cursor.fetchone()[0]
    conn.close()
    await message.answer(f"Umumiy foydalanuvchilar: {total_users}\nUmumiy xabarlar: {total_messages}")

@dp.message(Command(commands="draw"))
async def draw_command(message: Message):
    await message.chat.do("typing")
    prompt = message.text.replace("/draw", "").strip()
    if not prompt:
        await message.answer("Rasm yaratish uchun tasvir yozing: /draw Sizning prompt")
        return
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        await message.answer_photo(image_url, caption="AI yaratgan rasm:")
    except Exception as e:
        await message.answer("Rasm yaratishda xatolik yuz berdi.")
        logging.error(f"DALL-E xatolik: {str(e)}")

@dp.message()
async def handle_message(message: Message):
    await message.chat.do("typing")
    update_user_info(message.from_user)
    user_id = message.from_user.id

    if message.photo:
        file_id = message.photo[-1].file_id
        bot = Bot(token=TOKEN)
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        messages = [{"role": "system", "content": BOT_SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this image."},
                        {"type": "image_url", "image_url": {"url": file_url}}
                    ]}]

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            reply = completion.choices[0].message.content
            await message.answer(reply, parse_mode="Markdown")
        except Exception as e:
            await message.answer("Rasmni tahlil qilishda xatolik yuz berdi.")
            logging.error(f"Rasm xatolik: {str(e)}")
    else:
        question = message.text.strip()
        save_to_history(user_id, "user", question)
        answer = search_database(question)
        if answer:
            save_to_history(user_id, "assistant", answer)
            await message.answer(answer)
            return
        history_messages = load_history(user_id)
        detected_language = detect_language(question)
        full_messages = [{"role": "system", "content": f"{BOT_SYSTEM_PROMPT} Always reply in {detected_language}."}] + history_messages
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages
            )
            reply = completion.choices[0].message.content
            save_to_history(user_id, "assistant", reply)
            await message.answer(reply, parse_mode="Markdown")
        except Exception as e:
            await message.answer("Uzr, javob bera olmadim. Keyinroq urinib ko'ring.")
            logging.error(f"Xatolik: {str(e)}")

async def main():
    create_database()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
