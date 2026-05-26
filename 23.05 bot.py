import asyncio 
import sqlite3
from aiogram import Dispatcher,Bot,types
from aiogram.filters import Command
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  

TOKEN = os.getenv("BOT_TOKEN")   
bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("service.db")
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_name TEXT,
                item TEXT,
                date TEXT
            )
        ''')
    conn.commit()
    conn.close()

def add_expense(user_id,user_name,item):
    conn = sqlite3.connect('service.db')
    c = conn.cursor()
    c.execute('INSERT INTO expenses (user_id,user_name,item,date) VALUES (?,?,?,?)'
                ,(user_id, user_name,item,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_last_10():
    conn = sqlite3.connect('service.db')
    c = conn.cursor()
    c.execute('SELECT user_name, item, date FROM expenses ORDER BY id DESC LIMIT 10')
    rows=c.fetchall()
    conn.close()
    return rows

@dp.message(Command('start'))
async def start_cmd(message: types.Message):
    await message.answer("Привет! я бот для учета расходов .\n /add <наименование>-добавить расход\n/list -последние 10 записей")

@dp.message(Command('add'))
async def add_expense_cmd(message: types.Message):
    item = message.text.replace("/add","").strip()
    if not item:
        await message.answer("Напиши, что добавить, например: /add масло 5л")
        return
    add_expense(message.from_user.id, message.from_user.first_name,item)
    await message.answer(f"Добавлено: {item}")

@dp.message(Command('list'))
async def list_cmd(message: types.Message):
    rows = get_last_10()
    if not rows:
        await message.answer("Записей пока нет")
        return
    text = 'Последние 10 записей: \n'
    for name,item,date in rows:
        text += f"{name}: {item} ({date})\n"
    await message.answer(text)

@dp.message()
async def unknown(message: types.Message):
    await message.answer("Неизвестная команда попробуйте использовать /add или /list")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())