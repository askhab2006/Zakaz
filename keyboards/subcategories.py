from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def sleep_kb():
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Российская", callback_data="sleep_ru")],
        [InlineKeyboardButton(text="🇹🇷 Турецкая", callback_data="sleep_tr")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def beds_kb():
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Российская", callback_data="beds_ru")],
        [InlineKeyboardButton(text="🇹🇷 Турецкая", callback_data="beds_tr")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def kitchen_kb():
    kb = [
        [InlineKeyboardButton(text="📐 Прямая", callback_data="kitchen_straight")],
        [InlineKeyboardButton(text="🔽 Угловая", callback_data="kitchen_corner")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def soft_kb():
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Российская", callback_data="soft_ru")],
        [InlineKeyboardButton(text="🇹🇷 Турецкая", callback_data="soft_tr")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def tables_chairs_kb():
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Российская", callback_data="tables_chairs_ru")],
        [InlineKeyboardButton(text="🇹🇷 Турецкая", callback_data="tables_chairs_tr")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def chests_kb():
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Российская", callback_data="chests_ru")],
        [InlineKeyboardButton(text="🇹🇷 Турецкая", callback_data="chests_tr")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)








