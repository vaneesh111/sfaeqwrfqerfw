import sqlite3
import asyncio
import uuid
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

api_id = 24368087
api_hash = 'a33f41aa03ecd172d6aa433d7fa3943b'
bot_token = '7424923295:AAGsydgZPcH-1j0U68eU1ZJSBOvefim5lwk'

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

admin_chat_id = 5635629469  # Замените на ID администратора

products = []
current_order = {}
reviews = [
    {"author": "vanesh", "text": "Кура гений ахахахах👌", "date": "26 июн", "city": "АНГАРСК"},
        {"author": "Кто Убил Билли", "text": "Клад в касуху еду пробывать", "date": "18 июн", "city": "АНГАРСК"},
    {"author": "vanesh", "text": "мефчик птичка в клетке гусь в духовки", "date": "25 июн", "city": "АНГАРСК"},
    {"author": "Вася", "text": "Саврик дома", "date": "03 июн", "city": "АНГАРСК"},
    {"author": "антигерой", "text": "грам кристалов поднятные", "date": "02 июн", "city": "АНГАРСК"},
    {"author": "Valentin", "text": "мэджик спс в кэс", "date": "19 мая", "city": "АНГАРСК"},
    {"author": "Марина", "text": "Бралa в первый раз, по адресу были сложности, но тех.поддержка быстро решила этот вопрос, после уточнения заветный свёрток был найден 🥲", "date": "05 мая", "city": "ИРКУТСК"},
    {"author": "Kasper84", "text": "Выпил и в касание снят. В городе.", "date": "30 апр", "city": "АНГАРСК"},
    {"author": "Alla", "text": "Далеко, но всё супер!", "date": "17 апр", "city": "АНГАРСК"},
    {"author": "Лёха", "text": "Далеко, но поднял в кэс, качество з6с!!!! от души.", "date": "03 апр", "city": "АНГАРСК"},
    {"author": "Lust", "text": "Родной камень дома 👍", "date": "01 апр", "city": "АНГАРСК"},
    {"author": "Dark", "text": "Первый раз берём в данном маркете. От покупки до подъёма 15 мин. Адрес поднят в кэс магнит городская локация. За качество отпишем завтра", "date": "21 мар", "city": "АНГАРСК"},
    {"author": "Kasper84", "text": "вип ск был обнаружен и обезврежен.", "date": "15 мар", "city": "АНГАРСК"},
    {"author": "Kasper84", "text": "Саврик домашний", "date": "12 мар", "city": "АНГАРСК"},
    {"author": "Думаю", "text": "Всё красиво 👍", "date": "07 мар", "city": "АНГАРСК"},
]

# Инициализация базы данных
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (chat_id INTEGER PRIMARY KEY, user_id INTEGER)''')
conn.commit()

def get_user_id(chat_id):
    c.execute("SELECT user_id FROM users WHERE chat_id = ?", (chat_id,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        user_id = c.execute("SELECT COUNT(*) FROM users").fetchone()[0] + 1
        c.execute("INSERT INTO users (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
        conn.commit()
        return user_id

@app.on_message(filters.command("start"))
async def start(client, message):
    chat_id = message.chat.id
    user_id = get_user_id(chat_id)
    
    buttons = [
        [InlineKeyboardButton("Начать покупки [В наличии]", callback_data="start_shopping")],
        [InlineKeyboardButton("Личный кабинет", callback_data="personal_account")],
        [InlineKeyboardButton("Проблемы с оплатой?", callback_data="payment_issues")],
        [InlineKeyboardButton("Отзывы клиентов [15]", callback_data="customer_reviews")],
        [InlineKeyboardButton("Обновить страницу", callback_data="refresh_page")],
        [InlineKeyboardButton("Контакты магазина", callback_data="shop_contacts")],
        [InlineKeyboardButton("Швырокуры", url="https://t.me/+Zx3PQ4wedFA1OGUy")],
        [InlineKeyboardButton("Получил 50 рублей на счёт!", callback_data="get_bonus")],
        [InlineKeyboardButton("EPIC GROUP - Ровный чат РФ", url="https://t.me/+vWTGHDyhvP5mMTEx")],
        [InlineKeyboardButton("Анонимный фотохостинг", url="https://t.me/necroimg_bot")]
    ]

    await message.reply_text(
        f"Добро пожаловать в streetmagic38.\n"
        f"==============================\n"
        f"АНГАРСК - Есть наличие\n"
        f"Усолье-Сибирское - Пусто\n"
        f"Зима - Пусто\n"
        f"Саянск - Пусто\n"
        f"Иркутск - Пусто\n"
        f"==============================\n"
        f"О магазине:\n"
        f"Приветствую, маркет представляет витрину товара высочайшего качества\n"
        f"==============================\n"
        f"Ваш баланс: 0 рублей\n"
        f"Ваш ID внутри системы: {user_id}\n"
        f"Ваш CHAT-ID: {chat_id}\n"
        f"==============================\n"
        f"Скидки и акции: Отсутствуют",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_message(filters.command("admin") & filters.user(admin_chat_id))
async def admin_panel(client, message):
    await message.reply_text(
        "Админ панель\n"
        "Используйте команду /add_product <название>, <вес>, <район>, <цена> для добавления товара.\n"
        "Пример: /add_product Alphapvp, 1г, Центр, 5000₽"
    )

@app.on_message(filters.command("add_product") & filters.user(admin_chat_id))
async def add_product(client, message: Message):
    try:
        _, product_info = message.text.split(" ", 1)
        name, weight, location, price = map(str.strip, product_info.split(","))
        order_id = str(uuid.uuid4())
        products.append({"name": name, "weight": weight, "location": location, "price": price, "order_id": order_id})
        await message.reply_text(f"Товар {name} добавлен успешно!")
        print(f"Добавлен товар: {name}, {weight}, {location}, {price}, {order_id}")  # Отладочное сообщение
    except ValueError:
        await message.reply_text("Неверный формат. Используйте /add_product <название>, <вес>, <район>, <цена>")

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    global current_order

    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "start_shopping":
        buttons = [
            [InlineKeyboardButton("г.АНГАРСК [Есть наличие] [Выбрать]", callback_data="choose_angarsk")],
            [InlineKeyboardButton("Назад", callback_data="main_menu"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Оформление покупки\n"
            "==============================\n"
            "Выбери нужный город из наличия:\n"
            "г.АНГАРСК [Есть наличие] [Выбрать]",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "choose_angarsk":
        product_buttons = [
            [InlineKeyboardButton(f"{p['name']} ({p['weight']}) за {p['price']}₽ [Выбрать]", callback_data=f"buy_{i}")]
            for i, p in enumerate(products)
        ]
        if not product_buttons:
            product_buttons.append([InlineKeyboardButton("Товаров нет", callback_data="no_products")])
        product_buttons.append([InlineKeyboardButton("Назад", callback_data="start_shopping"), InlineKeyboardButton("Главное меню", callback_data="main_menu")])
        await callback_query.message.edit_text(
            "Оформление покупки\n"
            "==============================\n"
            "Город: АНГАРСК\n"
            "==============================\n"
            "Выберите нужный товар:",
            reply_markup=InlineKeyboardMarkup(product_buttons)
        )
    elif data.startswith("buy_"):
        product_index = int(data.split("_", 1)[1])
        product = products[product_index]
        current_order = {
            "product": product,
            "type": None,
            "location": None
        }
        buttons = [
            [InlineKeyboardButton("тип: Тайник [Выбрать]", callback_data=f"type_{product_index}_тайник")],
            [InlineKeyboardButton("Назад", callback_data="choose_angarsk"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            f"Оформление покупки\n"
            f"==============================\n"
            f"Город: АНГАРСК\n"
            f"Товар: {product['name']} ({product['weight']})\n"
            f"Описание товара: не указано\n"
            f"Выберите нужный тип клада:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data.startswith("type_"):
        product_index, product_type = data.split("_")[1:3]
        current_order["type"] = product_type
        product = products[int(product_index)]
        buttons = [
            [InlineKeyboardButton(f"р-н: {product['location']} [Выбрать]", callback_data=f"location_{product_index}_{product['location']}")],
            [InlineKeyboardButton("Назад", callback_data=f"buy_{product_index}"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            f"Оформление покупки\n"
            f"==============================\n"
            f"Город: АНГАРСК\n"
            f"Товар: {product['name']} ({product['weight']})\n"
            f"Тип клада: Тайник\n"
            f"==============================\n"
            f"Выберите нужный район:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data.startswith("location_"):
        product_index, product_location = data.split("_")[1:3]
        current_order["location"] = product_location
        buttons = [
            [InlineKeyboardButton("Всё понятно", callback_data="all_understood"), InlineKeyboardButton("Отменить заказ", callback_data="cancel_order")],
            [InlineKeyboardButton("Назад", callback_data=f"type_{product_index}_тайник"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Правила магазина\n"
            "==============================\n"
            "Перезаказов нет. Для решения, снимайте видео перед началом поисков, до того как дошли до места",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "all_understood":
        product = current_order["product"]
        buttons = [
            [InlineKeyboardButton(f"Город: АНГАРСК [изменить]", callback_data="change_city")],
            [InlineKeyboardButton(f"Товар: {product['name']} ({product['weight']}) [изменить]", callback_data="change_product")],
            [InlineKeyboardButton(f"Район: {current_order['location']} [изменить]", callback_data="change_location")],
            [InlineKeyboardButton(f"Тип клада: Тайник [изменить]", callback_data="change_type")],
            [InlineKeyboardButton(f"Оплатить {product['price']} [На карту]", callback_data="pay_card")],
            [InlineKeyboardButton(f"Оплатить {product['price']} [По СБП]", callback_data="pay_sbp")],
            [InlineKeyboardButton("Отменить заказ", callback_data="cancel_order")],
        ]
        await callback_query.message.edit_text(
            f"Финансовая инфа по заказу:\n"
            f"==============================\n"
            f"Баланс RUB: 0\n"
            f"Баланс BTC: 0.00000000\n"
            f"Баланс LTC: 0.00000000\n"
            f"==============================\n"
            f"Личная скидка: 0%\n"
            f"Общая скидка: 0%\n"
            f"Цена товара RUB: {product['price']}\n"
            f"Комиссия: 0%\n"
            f"==============================\n"
            f"Итого к оплате: {product['price']}\n"
            f"В Bitcoin: 0.00039669\n",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "cancel_order":
        current_order.clear()
        await callback_query.message.edit_text("Заказ был отменен.")
    elif data == "pay_card":
        product = current_order["product"]
        await display_payment_info(callback_query.message, product, "2200700457065448", "На карту")
    elif data == "pay_sbp":
        product = current_order["product"]
        await display_payment_info(callback_query.message, product, "2200700457065448", "По СБП")
    elif data == "card_and_amount":
        product = current_order["product"]
        await callback_query.message.reply_text(
            f"Реквизиты для оплаты:\n"
            f"Карта: 2200700457065448\n"
            f"Сумма к оплате: {product['price']} рублей"
        )
    elif data == "personal_account":
        chat_id = callback_query.message.chat.id
        user_id = get_user_id(chat_id)

        buttons = [
            [InlineKeyboardButton("Список Ваших счетов", callback_data="account_list")],
            [InlineKeyboardButton("Список Ваших покупок [0]", callback_data="purchase_list")],
            [InlineKeyboardButton("PIN-код блокировки бота: [Включить]", callback_data="pin_code")],
            [InlineKeyboardButton("Пополнить баланс", callback_data="top_up_balance")],
            [InlineKeyboardButton("Управление вашим ботом", callback_data="bot_management")],
            [InlineKeyboardButton("Обращения в поддержку [0]", callback_data="support_requests")],
            [InlineKeyboardButton("<< Вернуться на главную", callback_data="main_menu")]
        ]

        await callback_query.message.edit_text(
            f"Добро пожаловать в твой личный кабинет, выбери нужный пункт меню.\n"
            f"==============================\n"
            f"Ваш ID внутри системы: {user_id}\n"
            f"Ваш CHAT-ID: {chat_id}\n"
            f"==============================\n"
            f"Баланс RUB: 0\n"
            f"Баланс BTC: 0.00000000\n"
            f"Баланс LTC: 0.00000000\n"
            f"==============================\n"
            f"Покупок: 0\n"
            f"Отзывы: 0\n"
            f"Одобренных тикетов: 0\n"
            f"Отказанных тикетов: 0",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "account_list":
        buttons = [
            [InlineKeyboardButton("Назад", callback_data="personal_account"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Просмотр списка счетов\n"
            "==============================\n"
            "Здесь находится Ваша история платежей, так же здесь вы можете проверить истекшую, по времени, заявку.\n"
            "==============================\n"
            "Для проверки заявки, нажмите на нужную, далее нажмите проверить оплату",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "purchase_list":
        buttons = [
            [InlineKeyboardButton("Назад", callback_data="personal_account"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Ваши последние покупки\n"
            "==============================\n"
            "К большому сожалению у вас ещё нет покупок.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "top_up_balance":
        buttons = [
            [InlineKeyboardButton("Пополнить через VISA/MASTERCARD", callback_data="top_up_visa")],
            [InlineKeyboardButton("Пополнить через Litecoin", callback_data="top_up_litecoin")],
            [InlineKeyboardButton("Активировать купон", callback_data="activate_coupon")],
            [InlineKeyboardButton("Назад", callback_data="personal_account"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Пополнение личного баланса\n"
            "==============================\n"
            "Выберите удобный из доступных, способ пополнения баланса:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "bot_management":
        buttons = [
            [InlineKeyboardButton("Отменить", callback_data="personal_account"), InlineKeyboardButton("Продолжить", callback_data="continue_bot_management")]
        ]
        await callback_query.message.edit_text(
            "Твой неубиваемый бот от магазина streetmagic38.\n"
            "==============================\n"
            "1. Ты получаешь бонус за создание бота 50 руб. на баланс.\n"
            "2. Ты получаешь 5% на баланс, с каждого кто купит через твой бот.\n"
            "3. Ты всегда на связи со своим любимым магазином, т.к он только твой бот.\n"
            "==============================\n"
            "Больше не нужно бродить по чатам в поисках нового контакта нашего магазина, попадая на фейков и шаверщиков.\n"
            "==============================\n"
            "Шаг - 1: Создание бота.\n"
            "==============================\n"
            "Перейдите на этот аккаунт: @BotFather и нажмите или отправьте /start",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "support_requests":
        buttons = [
            [InlineKeyboardButton("Начать переписку", url="https://t.me/helpmagicc")],
            [InlineKeyboardButton("Назад", callback_data="personal_account"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Запросы в поддержку\n"
            "==============================\n"
            "Здесь находятся ваши активные и нет запросы в службу поддержки магазина.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "payment_issues":
        buttons = [
            [InlineKeyboardButton("Назад", callback_data="main_menu"), InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Проблемы с оплатой\n"
            "==============================\n"
            "1. Не ошибись в сумме, нажми на неё и она скопируется тебе в буфер, как и карта.\n"
            "2. Для твоего удобства, есть кнопка для выдачи тебе карты и суммы отдельными сообщениями.\n"
            "3. Если оплата не проходит более 40 минут, пишите оператору.\n"
            "4. По вопросам оплаты писать на Контакт: @helpmagicc",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "refresh_page":
        await callback_query.message.edit_text("Обновление страницы магазина...", reply_markup=callback_query.message.reply_markup)
        await callback_query.message.edit_text(
            "Добро пожаловать в streetmagic38.\n"
            "==============================\n"
            "АНГАРСК - Есть наличие\n"
            "Усолье-Сибирское - Пусто\n"
            "Зима - Пусто\n"
            "Саянск - Пусто\n"
            "Иркутск - Пусто\n"
            "==============================\n"
            "О магазине:\n"
            "Приветствую, маркет представляет витрину товара высочайшего качества\n"
            "==============================\n"
            "Ваш баланс: 0 рублей\n"
            "Ваш ID внутри системы: 1749519\n"
            "Ваш CHAT-ID: 672827437\n"
            "==============================\n"
            "Скидки и акции: Отсутствуют",
            reply_markup=callback_query.message.reply_markup
        )
    elif data == "shop_contacts":
        buttons = [
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        await callback_query.message.edit_text(
            "Контакты магазина:\n"
            "==============================\n"
            "Оператор: @helpmagicc\n"
            "==============================\n"
            "Бот: @streettmagic_bot\n"
            "==============================\n"
            "Второй бот: Не указано\n"
            "==============================\n"
            "Адрес сайта: не указано\n"
            "==============================\n"
            "Группа: Не указана ссылка на группу\n"
            "==============================\n"
            "Канал: Не указана ссылка на канал",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "get_bonus":
        buttons = [
            [InlineKeyboardButton("Отменить", callback_data="personal_account"), InlineKeyboardButton("Продолжить", callback_data="continue_get_bonus")]
        ]
        await callback_query.message.edit_text(
            "Твой неубиваемый бот от магазина streetmagic38.\n"
            "==============================\n"
            "1. Ты получаешь бонус за создание бота 50 руб. на баланс.\n"
            "2. Ты получаешь 5% на баланс, с каждого кто купит через твой бот.\n"
            "3. Ты всегда на связи со своим любимым магазином, т.к он только твой бот.\n"
            "==============================\n"
            "Больше не нужно бродить по чатам в поисках нового контакта нашего магазина, попадая на фейков и шаверщиков.\n"
            "==============================\n"
            "Шаг - 1: Создание бота.\n"
            "==============================\n"
            "Перейдите на этот аккаунт: @BotFather и нажмите или отправьте /start",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "main_menu":
        buttons = [
            [InlineKeyboardButton("Начать покупки [В наличии]", callback_data="start_shopping")],
            [InlineKeyboardButton("Личный кабинет", callback_data="personal_account")],
            [InlineKeyboardButton("Проблемы с оплатой?", callback_data="payment_issues")],
            [InlineKeyboardButton("Отзывы клиентов [15]", callback_data="customer_reviews")],
            [InlineKeyboardButton("Обновить страницу", callback_data="refresh_page")],
            [InlineKeyboardButton("Контакты магазина", callback_data="shop_contacts")],
            [InlineKeyboardButton("Швырокуры", url="https://t.me/+Zx3PQ4wedFA1OGUy")],
            [InlineKeyboardButton("Получил 50 рублей на счёт!", callback_data="get_bonus")],
            [InlineKeyboardButton("EPIC GROUP - Ровный чат РФ", url="https://t.me/+vWTGHDyhvP5mMTEx")],
            [InlineKeyboardButton("Анонимный фотохостинг", url="https://t.me/necroimg_bot")]
        ]

        await callback_query.message.edit_text(
            "Добро пожаловать в streetmagic38.\n"
            "==============================\n"
            "АНГАРСК - Есть наличие\n"
            "Усолье-Сибирское - Пусто\n"
            "Зима - Пусто\n"
            "Саянск - Пусто\n"
            "Иркутск - Пусто\n"
            "==============================\n"
            "О магазине:\n"
            "Приветствую, маркет представляет витрину товара высочайшего качества\n"
            "==============================\n"
            "Ваш баланс: 0 рублей\n"
            "Ваш ID внутри системы: 1749519\n"
            "Ваш CHAT-ID: 672827437\n"
            "==============================\n"
            "Скидки и акции: Отсутствуют",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "customer_reviews":
        await show_review(client, callback_query.message, 0)
    elif data.startswith("prev_review_"):
        index = int(data.split("_")[2])
        if index > 0:
            await show_review(client, callback_query.message, index - 1)
    elif data.startswith("next_review_"):
        index = int(data.split("_")[2])
        if index < len(reviews) - 1:
            await show_review(client, callback_query.message, index + 1)
    elif data == "check_payment":
        await check_payment_status(callback_query.message)
    elif data == "payment_help":
        await callback_query.message.edit_text(
            "1. Не ошибись в сумме, нажми на неё и она скопируется тебе в буфер, как и карта.\n"
            "2. Для твоего удобства, есть кнопка для выдачи тебе карты и суммы отдельными сообщениями.\n"
            "3. Если оплата не проходит более 40 минут, пишите оператору.\n"
            "4. По вопросам оплаты писать на Контакт: @helpmagicc",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Вернуться к заявке", callback_data="return_to_order")]
            ])
        )
    elif data == "return_to_order":
        await check_payment_status(callback_query.message)

async def check_payment_status(message):
    # Пример кода проверки оплаты. Здесь можно добавить логику проверки оплаты
    # и обновления статуса. Пока что просто обновим сообщение.
    product = current_order.get("product", {})
    card_number = "2200700457065448"
    buttons = [
        [InlineKeyboardButton("Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("Карта и сумма отдельно", callback_data="card_and_amount")],
        [InlineKeyboardButton("Помощь и информация по оплате", callback_data="payment_help")]
    ]

    # Таймер на 49 минут
    for remaining_minutes in range(49, -1, -1):
        await message.edit_text(
            f"Активный заказ.\n"
            f"==============================\n"
            f"Товар: {product.get('name', 'Неизвестно')} ({product.get('weight', 'Неизвестно')})\n"
            f"Город: АНГАРСК\n"
            f"Район: {current_order.get('location', 'Неизвестно')}\n"
            f"Тип клада: Тайник\n"
            f"==============================\n"
            f"Номер заказа: {product.get('order_id', 'Неизвестно')}\n"
            f"Карта для оплаты: {card_number}\n"
            f"Сумма к оплате: {product.get('price', 'Неизвестно')} рублей\n"
            f"==============================\n"
            f"ВНИМАТЕЛЬНО проверьте сумму заказа, оплатили не точную сумму - оплатили чужой заказ.\n"
            f"Ожидаем твою оплату {product.get('price', 'Неизвестно')} рублей.\n"
            f"До отмены осталось: {remaining_minutes} мин.\n",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await asyncio.sleep(60)  # Ожидание 1 минуты

async def display_payment_info(message, product, card_number, payment_method):
    buttons = [
        [InlineKeyboardButton("Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("Карта и сумма отдельно", callback_data="card_and_amount")],
        [InlineKeyboardButton("Помощь и информация по оплате", callback_data="payment_help")]
    ]

    await message.edit_text(
        f"Активный заказ.\n"
        f"==============================\n"
        f"Товар: {product['name']} ({product['weight']})\n"
        f"Город: АНГАРСК\n"
        f"Район: {product['location']}\n"
        f"Тип клада: Тайник\n"
        f"==============================\n"
        f"Номер заказа: {product['order_id']}\n"
        f"Карта для оплаты: {card_number}\n"
        f"Сумма к оплате: {product['price']} рублей\n"
        f"==============================\n"
        f"ВНИМАТЕЛЬНО проверьте сумму заказа, оплатили не точную сумму - оплатили чужой заказ.\n"
        f"Ожидаем твою оплату {product['price']} рублей.\n"
        f"До отмены осталось: 49 мин.\n",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_review(client, message, index):
    review = reviews[index]
    text = (
        f"Отзывы и тримы магазина\n"
        f"==============================\n"
        f"Пишет {review['author']}:\n"
        f"{review['text']}\n"
        f"==============================\n"
        f"Отзыв написан {review['date']}, {review['city']}\n"
    )

    buttons = [
        [InlineKeyboardButton("<<", callback_data=f"prev_review_{index}"), InlineKeyboardButton(f"{index + 1} из {len(reviews)}", callback_data="ignore"), InlineKeyboardButton(">>", callback_data=f"next_review_{index}")],
        [InlineKeyboardButton("Добавить новый отзыв", callback_data="add_review")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]

    await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

if __name__ == "__main__":
    app.run()
