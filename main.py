import asyncio,logging, sys
from aiogram import Bot, Dispatcher,F,Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv


from buttons import start_btn,kurslar,back_btn



load_dotenv()



TOKEN = "8040811407:AAFO3Ak0b3mV5w5DtZFIL7ADtEb56chvmTU"
dp = Dispatcher()
router=Router()
bot=Bot(token=TOKEN)
dp.include_router(router)

@dp.message(Command(commands="start"))
async  def startCommand(msg:Message):
    await msg.answer(f"Salom {msg.from_user.full_name}\nMenulardan birini tanla.",reply_markup=start_btn)


@dp.message(F.text=="Kurslar")
async  def answer_kurslar(msg:Message):
    await msg.answer("Kurslardan birini tanlang.",reply_markup=kurslar)



@dp.message(F.text=="IT Live o'quv markazi haqida")
async  def answer_about(msg:Message):
    await msg.answer("""Biz haqimizda
IT LIVE ACADEMY - 08.09.2022 yil tashkil etilgan va hozirgacha faoliyat olib kelmoqda. 
IT LIVE ACADEMY kompaniyasining asosiy faoliyat turi ikkiga bo'linadi, -Kelajak kasblariga o'qitish -IT sohasida xizmatlarini yetkazib berish dan iborat. 
Bizning akademiyamiz axborot texnologiyalarining barcha tendensiyalari bilan yaqindan tanishtiradi. 
Shinam o‘quv binosi va zamonaviy texnologiyalarga asoslangan kurslar dasturi bilan yurtimizning eng yirik, xalqaro kompaniyalarida IT karyerangizni boshlaysiz.""",reply_markup=back_btn)

@dp.message(F.text=="Orqaga🔙")
async  def answer_back(msg:Message):
    await msg.answer("Asosiy menyu.",reply_markup=start_btn)

@dp.message(F.text=="Kurslarga yozilish")
async  def send_link(msg:Message):
    await  msg.answer("Shu link orqali online kursga yozilishiz mumkin.\nhttps://itlive.livesphere.uz/lead/instagram")


@router.message(F.contact)
async def get_contact(message: Message):
    contact = message.contact
    await message.answer("Kontakt uchun rahmat!")

    # Masalan, kontakt ma’lumotlarini adminga yuborish
    admin_id = 893521695  # o'zingizga moslashtiring
    await bot.send_contact(
        chat_id=admin_id,
        phone_number=contact.phone_number,
        first_name=contact.first_name,
        last_name=contact.last_name
    )

@router.message(F.text == "📍 Lokatsiyamiz")
async def send_location(msg: Message):
    # Lokatsiya (masalan, Toshkentdagi bir nuqta)
    latitude = 40.49743606530408
    longitude = 68.76729864746862

    await msg.answer_location(latitude=latitude, longitude=longitude)
    await msg.answer("Mana o‘quv markazimiz joylashuvi 📍")




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


