import os
import html
import asyncio
import requests
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from main import sura_names  # sura_names bo'lishi kerak

API_TOKEN = os.getenv("8180198467:AAE3R0woUcTCGQ8Fx3wnUmdkyA2sdujWZJY")
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Menyu tugmalari
def build_reply_keyboard():
    keyboard = []
    row = []
    for i, name in enumerate(sura_names, 1):
        row.append(KeyboardButton(text=name))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("🕌 <b>Assalomu alaykum!</b>\nQuyidagi suralardan birini tanlang 👇", reply_markup=build_reply_keyboard())

@dp.message()
async def sura_selected(message: Message):
    if message.text in sura_names:
        sura_index = sura_names.index(message.text) + 1
        url = f"https://quranapi.pages.dev/api/{sura_index}.json"
        try:
            response = requests.get(url)
            data = response.json()
            if "uzbek" in data:
                tarjima = data["uzbek"]
                formatted_text = f"📖 <b>{html.escape(message.text)} surasi tarjimasi:</b>\n\n"
                for i, oyat_text in enumerate(tarjima, start=1):
                    formatted_text += f"<b>{i}.</b> {html.escape(oyat_text)}\n"
                chunks = [formatted_text[i:i+4000] for i in range(0, len(formatted_text), 4000)]
                for chunk in chunks:
                    await message.answer(chunk)
                    await asyncio.sleep(1.5)
            else:
                await message.answer("❌ Tarjima topilmadi.")
            audio_url = f"https://server11.mp3quran.net/yasser/{sura_index:03d}.mp3"
            await message.answer_audio(audio=audio_url)
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi:\n<code>{str(e)}</code>")
    else:
        await message.answer("Iltimos, menyudan surani tanlang.")

# Webhookni sozlash funksiyalari
async def on_startup(app):
    await bot.set_webhook(f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook")

async def on_shutdown(app):
    await bot.delete_webhook()

# Render uchun yagona main()
async def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    web.run_app(main(), host="0.0.0.0", port=port)
