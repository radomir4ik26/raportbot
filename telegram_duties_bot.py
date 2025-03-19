from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка базы данных и модели для SQLite
DATABASE_URL = "sqlite:///duties.db"  # Путь к базе данных SQLite
Base = declarative_base()

# Модель данных для нарядов
class Duty(Base):
    __tablename__ = 'duties'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    place = Column(String, nullable=False)

# Подключение к базе данных SQLite
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)  # Создание таблиц (если они еще не созданы)
Session = sessionmaker(bind=engine)
session = Session()

# Инициализация бота
API_TOKEN = "7513010157:AAGvIev8OmCt3KWRNuvLxzyP6gTxFnMKUnA"  # Замените на свой токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())  # Инициализация Dispatcher до хендлеров

# Определение состояний
class DutyForm(StatesGroup):
    name = State()
    date = State()
    place = State()

# Функция для добавления наряда в базу данных
def add_duty_to_db(name, date, place):
    new_duty = Duty(name=name, date=date, place=place)
    session.add(new_duty)
    session.commit()  # Сохраняем изменения

# Хендлеры для добавления наряда
@dp.message_handler(commands=['add_duty'], state='*')
async def start_add_duty(message: types.Message):
    await message.reply("Введите имя для добавления наряда:")
    await DutyForm.name.set()

@dp.message_handler(state=DutyForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("Введите дату наряда (например, 2025-03-19):")
    await DutyForm.next()

@dp.message_handler(state=DutyForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
    await message.reply("Введите место наряда:")
    await DutyForm.next()

@dp.message_handler(state=DutyForm.place)
async def process_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['place'] = message.text
        # Добавляем данные в базу данных
        add_duty_to_db(data['name'], data['date'], data['place'])
        await message.reply(f"Наряд добавлен: {data['name']} на {data['date']} в {data['place']}")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)