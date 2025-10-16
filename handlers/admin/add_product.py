from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID
from database.db import async_session
from database.models import Category, Product, ProductPhoto

router = Router()


class AddProduct(StatesGroup):
    description = State()
    category = State()
    country_or_type = State()
    photos = State()


async def start_add_product_for_admin(user_id: int, message: types.Message, state: FSMContext):
    if user_id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа.")

    text = (
        "🪄 <b>Добавление новой мебели</b>\n\n"
        "📝 <b>Шаг 1 из 5: Описание мебели</b>\n\n"
        "Пожалуйста, введите подробное описание мебели:\n"
        "• Материалы и отделка\n"
        "• Габариты (Д×Ш×В)\n"
        "• Особенности конструкции\n"
        "• Стиль и назначение\n\n"
        "<b>Пример:</b>\n"
        "Элегантный кожаный диван «Комфорт» с мягким наполнением,\n"
        "размеры 200×90×85 см, каркас из березовой фанеры,\n"
        "подушки сиденья на пружинном блоке, цвет черный."
    )

    await message.answer(text, parse_mode="HTML")
    await state.set_state(AddProduct.description)



@router.message(AddProduct.description)
async def step_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())

    async with async_session() as session:
        result = await session.execute(Category.__table__.select())
        categories = result.fetchall()

    if not categories:
        return await message.answer("📭 Категорий пока нет. Сначала добавьте категорию в админ-панели.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c._mapping["name"], callback_data=f"cat_{c._mapping['id']}")]
        for c in categories
    ])

    await message.answer(
        "📋 <b>Шаг 2 из 5: Выбор категории</b>\n\n"
        "Выберите категорию мебели, к которой относится описание:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(AddProduct.category)



@router.callback_query(F.data.startswith("cat_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        result = await session.execute(Category.__table__.select().where(Category.id == category_id))
        category = result.fetchone()

    if not category:
        return await callback.message.answer("❌ Ошибка: категория не найдена.")

    category_name = category._mapping["name"]
    await state.update_data(category_id=category_id, category_name=category_name)

    
    if "кухон" in category_name.lower():
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➡️ Прямая кухня", callback_data="type_straight"),
                InlineKeyboardButton(text="↩️ Угловая кухня", callback_data="type_corner")
            ]
        ])
        await callback.message.answer(
            f"🍳 Категория выбрана: <b>{category_name}</b>\n\n"
            "📋 Шаг 3 из 5: Тип кухни\n\n"
            "Выберите тип кухни из списка ниже:",
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
       
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Россия", callback_data="country_ru"),
                InlineKeyboardButton(text="🇹🇷 Турция", callback_data="country_tr")
            ]
        ])
        await callback.message.answer(
            f"🗂 Категория выбрана: <b>{category_name}</b>\n\n"
            "📋 Шаг 3 из 5: Страна производства\n\n"
            "Теперь укажите страну происхождения мебели 🌍\n"
            "Выберите из списка ниже:",
            parse_mode="HTML",
            reply_markup=kb
        )

    await state.set_state(AddProduct.country_or_type)
    await callback.answer()



@router.callback_query(F.data.in_(["type_straight", "type_corner", "country_ru", "country_tr"]))
async def choose_country_or_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("type_"):
        country = "🇷🇺 Россия"
        kitchen_type = "Прямая кухня" if callback.data == "type_straight" else "Угловая кухня"
    else:
        country = "🇷🇺 Россия" if callback.data.endswith("ru") else "🇹🇷 Турция"
        kitchen_type = None


    await state.update_data(country=country, kitchen_type=kitchen_type)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить добавление", callback_data="finish_photos")]
    ])

    text = (
        f"🌍 Страна выбрана: <b>{country}</b>\n"
        f"{('🍽️ Тип кухни: ' + kitchen_type) if kitchen_type else ''}\n\n"
        "📋 Шаг 4 из 5: Фотографии\n\n"
        "Теперь отправьте фотографии мебели 📸\n"
        "• Можно отправить до 10 фото\n"
        "• После каждого фото будет показан прогресс\n\n"
        "Когда закончите — нажмите «Завершить добавление»."
    )

    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await state.update_data(photos=[])
    await state.set_state(AddProduct.photos)
    await callback.answer()



@router.message(AddProduct.photos, F.photo)
async def receive_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 10:
        return await message.answer("⚠️ Достигнут лимит — не более 10 фото!")

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить добавление", callback_data="finish_photos")]
    ])

    await message.answer(
        f"✅ Фото добавлено ({len(photos)}/10)\n\n"
        "📸 Отправьте еще фотографии или нажмите «Завершить добавление».",
        reply_markup=kb
    )


@router.callback_query(F.data == "finish_photos")
async def finish_adding(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_name = data.get("category_name", "Не указано")
    description = data.get("description", "Без описания")
    country = data.get("country", "Не указана")
    kitchen_type = data.get("kitchen_type", "Не указано")
    photos = data.get("photos", [])

    
    if not photos:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить фото", callback_data="noop")]
        ])
        await callback.message.answer(
            "⚠️ Пожалуйста, добавьте хотя бы одно фото перед завершением.",
            reply_markup=kb
        )
        await state.set_state(AddProduct.photos)
        await callback.answer()
        return

    async with async_session() as session:
        subcategory = kitchen_type if kitchen_type is not None else "Не указано"

        new_product = Product(
            name=f"Мебель ({category_name})",
            category=category_name,
            subcategory=subcategory,
            country=country,
            size="Не указано",
            price="Не указана",
            description=description
        )
        session.add(new_product)
        await session.flush()  

        
        for file_id in photos:
            session.add(ProductPhoto(product_id=new_product.id, file_id=file_id))

        await session.commit()

    await callback.message.answer(
        f"✅ Фотографии добавлены\n\n"
        f"🎉 Мебель успешно добавлена!\n\n"
        f"📊 Детали добавления:\n"
        f"• Категория: {category_name}\n"
        f"• Тип кухни: {kitchen_type}\n"
        f"• Страна: {country}\n"
        f"• Фото: {len(photos)}\n\n"
        f"📄 Описание:\n{description}\n\n"
        f"Спасибо за добавление! ✅",
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer()