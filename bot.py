import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8898328974:AAFL1wKGtZMEeT1EjXaK2OxVaXfELis-XVw"
ADMIN_ID = 7911907272  # Замените на ваш Telegram ID (число без кавычек)
PASS_THRESHOLD = 17   # Порог прохождения теста

# Вставьте сюда file_id ваших 4 видеоуроков после того, как загрузите их в бота
VIDEOS = [
    {
        "title": "🎬 Видеоурок 1: Роль менеджера и правила текста",
        "file_id": "BAACAgIAAxkBAAMfatSkwJRTTOiDBQcYCgwfcRnZw8MAApirAAJj-3BKdVKh1MI2HQM9BA",
        "description": "Понимание роли, эмпатия, структура сообщения и Tone of Voice."
    },
    {
        "title": "🎬 Видеоурок 2: Сбор данных и работа в CRM",
        "file_id": "BAACAgIAAxkBAAMhatSlXAvuPuiqtOaQRbpZ4PQWN8MAAvisAAJj-3BKwm3d9ls9KaY9BA",
        "description": "Минимум рабочей информации, фиксация действий и поиск по опорным данным."
    },
    {
        "title": "🎬 Видеоурок 3: Алгоритмы решения типовых проблем",
        "file_id": "BAACAgIAAxkBAAMjatSlZuGd__AQy5kbkqF6ZCPqnE0AAhStAAJj-3BKPbgq3vgWM2M9BA",
        "description": "Задержки заказов, возвраты, двойные списания, ошибки и работа с негативом."
    },
    {
        "title": "🎬 Видеоурок 4: Эскалация, безопасность и KPI",
        "file_id": "BAACAgIAAxkBAAMlatSlcvmrtO3qXPYQcJg2h4ZVza4AAjKtAAJj-3BK5keIlDLr2gY9BA",
        "description": "Как передавать задачи коллегам, защита данных клиентов, шаблоны и точки роста."
    }
]

# ================= БАЗА ВОПРОСОВ (20 ШТ.) =================
QUESTIONS = [
    {
        "q": "1/20. Какой главный подход в работе чат-менеджера снижает раздражение клиента?",
        "options": ["Решить всё молча и быстро", "Услышать — объяснить — сделать", "Ответить шаблоном и закрыть чат"],
        "correct": 1
    },
    {
        "q": "2/20. Какие три роли одновременно выполняет менеджер на смене?",
        "options": ["Продавец, аналитик, кассир", "Слушатель, документалист, координатор", "Модератор, техподдержка, курьер"],
        "correct": 1
    },
    {
        "q": "3/20. Зачем менеджеру выполнять роль «Аккуратного документалиста»?",
        "options": ["Чтобы другой отдел понял контекст без переспросов клиента", "Для красивой статистики в конце месяца", "Чтобы клиент видел длинный текст"],
        "correct": 0
    },
    {
        "q": "4/20. Каков правильный порядок «формулы понятного сообщения»?",
        "options": [
            "Приветствие и имя -> Подтверждение проблемы -> Что делаю сейчас -> Срок/шаг -> Короткое закрытие",
            "Срок ожидания -> Приветствие -> Запрос скриншота -> Прощание",
            "Извинение -> Шаблон ответа -> Перевод на другого специалиста"
        ],
        "correct": 0
    },
    {
        "q": "5/20. Как правильно подать клиенту план действий из нескольких шагов?",
        "options": ["Одним длинным предложением через запятую", "Разбить короткими пунктами 1), 2), 3) в несколько строк", "Отправить голосовое сообщение"],
        "correct": 1
    },
    {
        "q": "6/20. Что входит в «минимум рабочей информации» при обращении клиента с проблемой?",
        "options": [
            "Только имя и номер телефона",
            "Кто, что случилось, номер/ID, время события, вложение (скрин/фото)",
            "История всех покупок клиента за год"
        ],
        "correct": 1
    },
    {
        "q": "7/20. Что делать, если клиент не помнит номер заказа?",
        "options": [
            "Отказать в обслуживании до поиска номера",
            "Спросить опорные данные: адрес доставки, примерное время заказа, способ оплаты",
            "Попросить клиента позвонить на горячую линию"
        ],
        "correct": 1
    },
    {
        "q": "8/20. Какие данные обязательно нужно запросить при технической ошибке в приложении (например, код 403)?",
        "options": [
            "Модель устройства, версию приложения, точное время ошибки и скриншот",
            "Пароль от аккаунта и домашний адрес",
            "Скорость интернета и имя провайдера"
        ],
        "correct": 0
    },
    {
        "q": "9/20. Как правильно реагировать на запрос «Где мой заказ?», если номер заказа уже указан?",
        "options": [
            "Промолчать, пока логистика не ответит",
            "Подтвердить, что проверяете заказ, дать текущий статус и ориентир по времени",
            "Сразу предложить оформить возврат"
        ],
        "correct": 1
    },
    {
        "q": "10/20. Что нужно сообщить клиенту на первом этапе оформления возврата товара?",
        "options": [
            "Краткий порядок действий, список нужных материалов (фото, номер заказа, причина) и срок проверки",
            "Сразу дать телефон курьера",
            "Сказать, что возвраты обрабатываются только через суд"
        ],
        "correct": 0
    },
    {
        "q": "11/20. Какое главное правило при обращении клиента по поводу двойного списания средств?",
        "options": [
            "Пообещать мгновенный возврат денег в течение 5 минут",
            "Не говорить просто «подождите», сразу попросить скрин и время списания для передачи в финотдел",
            "Попросить клиента прислать фото банковской карты с двух сторон"
        ],
        "correct": 1
    },
    {
        "q": "12/20. С чего ВСЕГДА нужно начинать ответ на жесткую жалобу или негатив клиента?",
        "options": [
            "С цитирования правил компании",
            "С признания эмоции и извинения («Понимаю, это расстраивает. Извините за неудобства»)",
            "С предупреждения о блокировке за грубость"
        ],
        "correct": 1
    },
    {
        "q": "13/20. Что можно предложить клиенту при жалобе, чтобы сгладить негатив?",
        "options": [
            "Компенсационный вариант (скидка/купон/возврат), но строго в рамках своих полномочий",
            "Любую сумму денег, которую потребует клиент",
            "Личный номер телефона руководителя"
        ],
        "correct": 0
    },
    {
        "q": "14/20. Что такое грамотная эскалация (передача проблемы другому отделу)?",
        "options": [
            "Пересылка чата коллеге без комментариев",
            "Передача понятного досье: кратко суть, что уже сделано, вложения, контакт, срочность",
            "Просьба к клиенту самостоятельно написать в другой отдел"
        ],
        "correct": 1
    },
    {
        "q": "15/20. В каких случаях при эскалации нужно особо подчеркнуть важность проблемы?",
        "options": [
            "Если клиент угрожает публичной жалобой, речь о крупных суммах или о безопасности",
            "Только если клиент написал сообщение капсом",
            "В каждом обращении без исключения"
        ],
        "correct": 0
    },
    {
        "q": "16/20. Что менеджер должен сделать ПОСЛЕ передачи задачи в другой отдел?",
        "options": [
            "Забыть про чат, так как это больше не его зона ответственности",
            "Поставить себе напоминание, сообщить клиенту о передаче вопроса и дать ориентир по времени ответа",
            "Закрыть диалог без предупреждения"
        ],
        "correct": 1
    },
    {
        "q": "17/20. Что делать, если клиент прислал в чат пароль, CVV-код или код из SMS?",
        "options": [
            "Сохранить их в карточку CRM на всякий случай",
            "Предупредить о безопасности, попросить удалить сообщение и отправить защищённую форму/ссылку",
            "Проигнорировать и продолжить диалог"
        ],
        "correct": 1
    },
    {
        "q": "18/20. Какие две вещи обязательно должны быть в любом шаблоне (макросе) при отправке клиенту?",
        "options": [
            "Имя клиента и 1–2 специфические строки по сути его конкретной ситуации",
            "Смайлики и подпись «С любовью, команда»",
            "Ссылки на соцсети компании"
        ],
        "correct": 0
    },
    {
        "q": "19/20. О чем сигнализирует рост показателя «Повторные обращения» в вашем KPI?",
        "options": [
            "О том, что вы слишком долго ищете шаблоны",
            "О том, что в первом ответе вы не закрываете проблему клиента полностью",
            "О том, что клиентам просто нравится с вами общаться"
        ],
        "correct": 1
    },
    {
        "q": "20/20. Какая полезная привычка поможет менеджеру вырасти в качестве работы за месяц?",
        "options": [
            "Утром тратить 5 минут на обновления базы знаний и сохранять удачные переписки",
            "Отвечать клиентам одним словом для ускорения тайминга",
            "Копировать ответы коллег не глядя"
        ],
        "correct": 0
    }
]

# ================= МАШИНА СОСТОЯНИЙ (FSM) =================
class OnboardingState(StatesGroup):
    watching_videos = State()
    in_quiz = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= ВСПОМОГАТЕЛЬНЫЙ ХЕНДЛЕР ДЛЯ АДМИНА =================
# Отправьте видео боту со своего аккаунта, чтобы получить его file_id
@dp.message(F.video, F.from_user.id == ADMIN_ID)
async def get_video_file_id(message: types.Message):
    await message.reply(
        f"✅ Видео получено!\nЕго `file_id`:\n\n`{message.video.file_id}`",
        parse_mode="Markdown"
    )

# ================= СТАРТ БОТА =================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(OnboardingState.watching_videos)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть видеоурок 1", callback_data="video_0")]
    ])
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Добро пожаловать на обучение для начинающих онлайн-менеджеров.\n"
        "Тебе предстоит посмотреть **4 коротких видеоурока**, после чего откроется итоговый тест на **20 вопросов**.\n\n"
        f"⚠️ Для успешного прохождения нужно набрать минимум **{PASS_THRESHOLD} из 20** правильных ответов.\n\n"
        "Нажми кнопку ниже, чтобы начать!",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ================= ПОКАЗ ВИДЕОУРОКОВ =================
@dp.callback_query(F.data.startswith("video_"))
async def send_video_lesson(callback: types.CallbackQuery, state: FSMContext):
    video_index = int(callback.data.split("_")[1])
    lesson = VIDEOS[video_index]
    
    # Формируем кнопку под видео
    if video_index + 1 < len(VIDEOS):
        next_btn = InlineKeyboardButton(
            text=f"➡️ Далее (Видеоурок {video_index + 2})",
            callback_data=f"video_{video_index + 1}"
        )
    else:
        next_btn = InlineKeyboardButton(
            text="📝 Перейти к тесту (20 вопросов)",
            callback_data="start_quiz"
        )
        
    kb = InlineKeyboardMarkup(inline_keyboard=[[next_btn]])
    
    # убираем кнопку у предыдущего сообщения, чтобы не нажимали дважды
    await callback.message.edit_reply_markup(reply_markup=None)
    
    caption_text = f"**{lesson['title']}**\n\n{lesson['description']}"
    
    # Отправляем видео (если file_id еще не вставлен, отправит текст-заглушку для теста)
    if lesson["file_id"].startswith("ВСТАВЬТЕ"):
        await callback.message.answer(
            f"⚙️ *[Тестовый режим: здесь будет видеофайл]*\n\n{caption_text}",
            reply_markup=kb,
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer_video(
            video=lesson["file_id"],
            caption=caption_text,
            reply_markup=kb,
            parse_mode="Markdown"
        )
    await callback.answer()

# ================= ЗАПУСК И ПРОХОЖДЕНИЕ ТЕСТА =================
@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(OnboardingState.in_quiz)
    await state.update_data(q_index=0, score=0)
    
    await send_question(callback.message, 0)
    await callback.answer()

async def send_question(message: types.Message, q_index: int):
    q_data = QUESTIONS[q_index]
    
    buttons = []
    for idx, opt in enumerate(q_data["options"]):
        buttons.append([InlineKeyboardButton(text=opt, callback_data=f"ans_{q_index}_{idx}")])
        
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(f"❓ **{q_data['q']}**", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(OnboardingState.in_quiz, F.data.startswith("ans_"))
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    _, q_idx_str, ans_idx_str = callback.data.split("_")
    q_index = int(q_idx_str)
    ans_index = int(ans_idx_str)
    
    data = await state.get_data()
    # Защита от повторного нажатия на старый вопрос
    if data.get("q_index") != q_index:
        await callback.answer("На этот вопрос вы уже ответили!")
        return

    score = data.get("score", 0)
    correct_index = QUESTIONS[q_index]["correct"]
    
    if ans_index == correct_index:
        score += 1

    # Убираем кнопки у отвеченного вопроса
    selected_text = QUESTIONS[q_index]["options"][ans_index]
    await callback.message.edit_text(
        f"**{QUESTIONS[q_index]['q']}**\nВаш ответ: _{selected_text}_",
        parse_mode="Markdown"
    )
    
    next_q_index = q_index + 1
    if next_q_index < len(QUESTIONS):
        await state.update_data(q_index=next_q_index, score=score)
        await send_question(callback.message, next_q_index)
    else:
        await finish_quiz(callback.message, callback.from_user, score, state)
        
    await callback.answer()

# ================= ПОДВЕДЕНИЕ ИТОГОВ И ОТПРАВКА АДМИНУ =================
async def finish_quiz(message: types.Message, user: types.User, score: int, state: FSMContext):
    await state.clear()
    total = len(QUESTIONS)
    passed = score >= PASS_THRESHOLD
    
    # 1. Сообщение пользователю
    if passed:
        user_text = (
            f"🎉 **Поздравляем! Вы успешно прошли тест!**\n\n"
            f"Ваш результат: **{score} из {total}** (проходной балл — {PASS_THRESHOLD}).\n"
            "Ваши результаты отправлены руководителю, скоро с вами свяжутся!"
        )
        kb = None
    else:
        user_text = (
            f"😔 **К сожалению, тест не пройден.**\n\n"
            f"Ваш результат: **{score} из {total}**.\n"
            f"Для прохождения необходимо набрать минимум **{PASS_THRESHOLD}** правильных ответов.\n\n"
            "Рекомендуем пересмотреть материалы или сразу попробовать пройти тест еще раз:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="start_quiz")],
            [InlineKeyboardButton(text="🎬 Пересмотреть видео с 1-го урока", callback_data="video_0")]
        ])
        
    await message.answer(user_text, reply_markup=kb, parse_mode="Markdown")
    
    # 2. Уведомление администратору (вам)
    username = f"@{user.username}" if user.username else "нет username"
    status_emoji = "✅ СДАЛ(А)" if passed else "❌ НЕ СДАЛ(А)"
    
    admin_report = (
        f"📊 **Новый результат тестирования лида!**\n\n"
        f"👤 **Имя:** {user.full_name} ({username})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"📈 **Результат:** {score} / {total}\n"
        f"📌 **Статус:** {status_emoji}"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_report, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Не удалось отправить отчет админу: {e}")

# ================= ЗАПУСК =================
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())