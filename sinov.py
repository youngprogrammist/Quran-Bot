import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
import html

from main import sura_names  # bu faylingizda sura_names ro'yxati bo'lishi kerak

API_TOKEN = "8180198467:AAE16PCAmQ7FJ8Wtxok88fNhz9h7Dj2yTSo"

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()

# Tugmali menyu
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

# /start komandasi
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

            # Tarjima formatda chiqariladi
            if "uzbek" in data:
                tarjima = data["uzbek"]
                formatted_text = f"📖 <b>{html.escape(message.text)} surasi tarjimasi:</b>\n\n"
                for i, oyat_text in enumerate(tarjima, start=1):
                    matn = html.escape(oyat_text)
                    formatted_text += f"<b>{i}.</b> {matn}\n"

                # 4096 belgidan oshsa, bo‘lib yuborish
                chunks = [formatted_text[i:i+4000] for i in range(0, len(formatted_text), 4000)]
                for chunk in chunks:
                    await message.answer(chunk)
                    await asyncio.sleep(1.5)  # flood xatolikni oldini olish uchun kechikish

            else:
                await message.answer("❌ Tarjima topilmadi.")

            # 5-oyat audiosi
            audio_url = f"https://server11.mp3quran.net/yasser/{sura_index:03d}.mp3"
            try:
                await message.answer_audio(audio=audio_url)
            except Exception as e:
                await message.answer("🎧 Audio yuborishda xatolik yuz berdi.")

        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi:\n<code>{str(e)}</code>")

    else:
        await message.answer("Iltimos, quyidagi menyudan surani tanlang.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
