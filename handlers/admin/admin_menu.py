from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database.db import async_session
from database.models import Category
from handlers.admin import add_product, manage_products, view_orders

router = Router()



@router.message(F.text == "/admin")
async def admin_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗂 Добавить категорию", callback_data="admin_add_category")],
        [InlineKeyboardButton(text="🛋 Добавить мебель", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="📦 Просмотреть товары", callback_data="admin_manage_products")],
        [InlineKeyboardButton(text="📊 Просмотр заказов", callback_data="admin_view_orders")]
    ])

    await message.answer(
        "⚙️ <b>Админ-панель</b>\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=kb
    )



class AddCategory(StatesGroup):
    name = State()
    description = State()
    confirm = State()



@router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Отменить", callback_data="cancel_add_category")]
    ])

    text = (
        "🆕 <b>Создание новой категории мебели</b>\n\n"
        "Введите название категории.\n\n"
        "🔹 <b>Совет:</b> добавьте эмодзи в начале названия — это делает меню заметнее.\n\n"
        "<b>Примеры:</b>\n"
        "🛏️ Спальная мебель\n"
        "🍳 Кухонная мебель\n"
        "🛋️ Мягкая мебель\n"
        "📚 Столы и стулья\n"
        "📺 Тумбы и комоды\n"
        "🛏️ Кровати\n"
        "🛏️️ Матрасы\n"
        "🚪 Шкафы\n\n"
        "Отправьте название или нажмите «Отменить»."
    )

    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(AddCategory.name)
    await callback.answer()



@router.message(AddCategory.name)
async def category_name_step(message: types.Message, state: FSMContext):
    name = message.text.strip()

    
    async with async_session() as session:
        result = await session.execute(Category.__table__.select().where(Category.name == name))
        if result.fetchone():
            await message.answer(f"⚠️ Категория <b>{name}</b> уже существует!", parse_mode="HTML")
            await state.clear()
            return

    await state.update_data(name=name)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Отменить", callback_data="cancel_add_category")]
    ])

    await message.answer(
        f"✅ Название сохранено: <b>{name}</b>\n\n"
        "Теперь введите краткое описание для категории — одно-две фразы.\n"
        "Описание поможет покупателям быстрее понять, что внутри категории.\n\n"
        "Если хотите отменить — нажмите «Отменить».",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(AddCategory.description)



@router.message(AddCategory.description)
async def category_description_step(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    data = await state.get_data()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💾 Сохранить", callback_data="save_category"),
            InlineKeyboardButton(text="🚫 Отменить", callback_data="cancel_add_category")
        ]
    ])

    await message.answer(
        f"🎯 <b>Предпросмотр новой категории</b>\n\n"
        f"{data['name']}\n"
        f"{data['description']}\n\n"
        "Проверьте, всё ли верно.\n"
        "Когда будете готовы — нажмите «Сохранить» или «Отменить».",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(AddCategory.confirm)



@router.callback_query(F.data == "save_category")
async def save_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    description = data["description"]

    async with async_session() as session:
        new_category = Category(name=name, description=description)
        session.add(new_category)
        await session.commit()

    await callback.message.answer(f"✅ Категория <b>{name}</b> добавлена!", parse_mode="HTML")
    await state.clear()
    await callback.answer()



@router.callback_query(F.data == "cancel_add_category")
async def cancel_add_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Добавление категории отменено.")
    await callback.answer()

@router.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    await add_product.start_add_product_for_admin(
        user_id=callback.from_user.id,
        message=callback.message,
        state=state
    )
    await callback.answer()




@router.callback_query(F.data == "admin_manage_products")
async def admin_view_products(callback: CallbackQuery):
    await manage_products.list_products(callback.message, callback.from_user)
    await callback.answer()


@router.callback_query(F.data == "admin_view_orders")
async def admin_view_orders(callback: CallbackQuery):
    await view_orders.view_orders(callback.message, user=callback.from_user)
    await callback.answer()