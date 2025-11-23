from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
import app.keyboards as kb
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import sqlite3


con = sqlite3.connect('database.db')
cursor = con.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT
)
""")

con.commit()


router = Router()


class TodoAdd(StatesGroup):
      text = State()
      


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я - Бот по созданию задач. Давай начнем, выбирай действие.", reply_markup=kb.main)




#Чисто для себя
# @router.callback_query(F.data == 'catalog')
# async def catalog(callback: CallbackQuery):
#       await callback.answer('Окак')
#       await callback.message.edit_text('Молодец братан', reply_markup=await kb.inline_cars())




@router.message(F.text == 'Добавить задачу')
async def add_todo(message: Message, state: FSMContext):
      await state.set_state(TodoAdd.text)
      await message.answer('Введите цель задачи')


@router.message(TodoAdd.text)
async def reg_two(message: Message, state: FSMContext):
     await state.update_data(text=message.text)
     data = await state.get_data()
     text = data['text']
     user_id = message.from_user.id
     await message.answer(f'Хорошо, ваша задача - {data["text"]} добавлена в список.')
     cursor.execute("INSERT INTO tasks (user_id, text) VALUES (?, ?)", (user_id, text))
     con.commit()
     await state.clear()




@router.message(F.text == 'Список задач')
async def list_todo(message: Message):
          user_id = message.from_user.id
          cursor.execute("SELECT id, text FROM tasks WHERE user_id = ?", (user_id,))
          rows = cursor.fetchall()
          text = 'Список задач:\n'
          for i in range(len(rows)):
               text += f'{i+1}) {rows[i][1]}\n'
          await message.answer(text)


class DeleteTask(StatesGroup):
    wait = State()


@router.message(F.text == 'Удалить задачу')
async def tododel(message: Message, state: FSMContext):
     user_id = message.from_user.id
     cursor.execute("SELECT id, text FROM tasks WHERE user_id = ?", (user_id,))
     rows = cursor.fetchall()
     text='Введите ID задачи, которую желаете удалить:\n'
     for i in range(len(rows)):
          text += f'{rows[i][0]}) {rows[i][1]}\n'
     await message.answer(text)
     await state.set_state(DeleteTask.wait)

@router.message(DeleteTask.wait)
async def delete(message:Message, state: FSMContext):
     user_id = message.from_user.id
     task_id = message.text
     if not task_id.isdigit():
          await message.answer("Пожалуйста, введи корректный числовой ID задачи.")
          return
     task = int(task_id)
     cursor.execute("SELECT text FROM tasks WHERE id = ? AND user_id = ?", (task, user_id))
     row = cursor.fetchone()
     if not row:
          await message.answer("Задач с таким ID нет.")
     else:
          cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task, user_id))
          con.commit()
          await message.answer(f"Задача успешно удалена.")