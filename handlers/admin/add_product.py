from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from database.db import async_session
from database.models import Product, ProductPhoto

router = Router()



class AddProduct(StatesGroup):
    name = State()
    category = State()
    subcategory = State()
    country = State()
    size = State()
    price = State()
    photos = State()
    description = State()



@router.message(F.text == "/add_product")
async def start_add_product(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа.")
    await message.answer("🆕 Введите название товара:")
    await state.set_state(AddProduct.name)


@router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📂 Введите категорию (например: Спальная мебель, Кровати, Кухонная мебель, Мягкая мебель,\n" \
    " Столы и стулья, Тумбы и комоды, Матрасы, Шкафы):")
    await state.set_state(AddProduct.category)


@router.message(AddProduct.category)
async def add_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("📁 Введите подкатегорию (например: Российская, Турецкая, Прямая, Угловая):")
    await state.set_state(AddProduct.subcategory)


@router.message(AddProduct.subcategory)
async def add_subcategory(message: types.Message, state: FSMContext):
    await state.update_data(subcategory=message.text)
    await message.answer("🌍 Укажите страну производства:")
    await state.set_state(AddProduct.country)


@router.message(AddProduct.country)
async def add_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("📏 Введите размеры (например: 160x200 см):")
    await state.set_state(AddProduct.size)


@router.message(AddProduct.size)
async def add_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("💰 Укажите цену:")
    await state.set_state(AddProduct.price)



@router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(
        "📸 Отправьте одно или несколько фото подряд.\n"
        "Когда закончите — напишите <b>готово</b>.",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.photos)



@router.message(AddProduct.photos, F.photo)
async def collect_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer("✅ Фото добавлено! Отправьте ещё или напишите <b>готово</b>.", parse_mode="HTML")



@router.message(AddProduct.photos, F.text.lower() == "готово")
async def done_photos(message: types.Message, state: FSMContext):
    await message.answer("📝 Теперь введите описание товара:")
    await state.set_state(AddProduct.description)



@router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()

    async with async_session() as session:
        
        product = Product(
            name=data["name"],
            category=data["category"],
            subcategory=data["subcategory"],
            country=data["country"],
            size=data["size"],
            price=data["price"],
            description=data["description"]
        )
        session.add(product)
        await session.flush()  

        
        for file_id in data.get("photos", []):
            session.add(ProductPhoto(product_id=product.id, file_id=file_id))

        await session.commit()

    await message.answer("✅ Товар успешно добавлен с фото в базу данных.")
    await state.clear()
