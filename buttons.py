from aiogram.types import KeyboardButton,ReplyKeyboardMarkup

start_btn= ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="IT Live o'quv markazi haqida"),
    ],
    [
        KeyboardButton(text="Kurslar"),
        KeyboardButton(text="Mentorlar"),
    ],
    [
        KeyboardButton(text="Biz bilan bog'lanish",request_contact=True),
        KeyboardButton(text="📍 Lokatsiyamiz")
    ]
],
    resize_keyboard=True,
    one_time_keyboard=True
)



back_btn=ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Orqaga🔙")
    ]
],
    resize_keyboard=True
)



kurslar= ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Robototexnika")
    ],
    [
        KeyboardButton(text="Foundation"),
    ],
    [
        KeyboardButton(text="Frontend"),
    ],
    [
        KeyboardButton(text="Backend")
    ],
    [
        KeyboardButton(text="Buxgalteriya")
    ],
    [
        KeyboardButton(text="Grafik dizayn")
    ],
    [
        KeyboardButton(text="Kurslarga yozilish")
    ],
    [
        KeyboardButton(text="Orqaga🔙")
    ]

],
    resize_keyboard=True
)

