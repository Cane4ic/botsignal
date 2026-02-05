import logging
import threading
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from flask import Flask, request
from supabase import create_client, Client

# --- НАСТРОЙКИ ---
# Приоритет берется из Переменных Окружения (Railway Variables), иначе значения по умолчанию
TOKEN = os.environ.get("TOKEN", "8534463280:AAE5HDQiisEyJS4FeQEIBuPmFbcGcImpiu0")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7951945463))
# ВАЖНО: После деплоя на Railway замените эту ссылку в переменных на ту, что выдаст Railway
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://signalbotnew-cane4ic-cane4ics-projects.vercel.app/")

# Supabase настройки
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://etiubthfjhxtlbhbkpxw.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_YjJGR4yQzgVaEQzEpPGkhA_enSb6xsb")

AFFILIATE_LINK = "https://u3.shortink.io/register?utm_campaign=836773&utm_source=affiliate&utm_medium=sr&a=zSsLjb68CplcNs&ac=my&code=HIM634"
SUPPORT_LINK = "https://t.me/mystery_td" 

# --- НАСТРОЙКИ КАРТИНОК ---
# Вставьте ссылки (http...) ИЛИ названия файлов (image.jpg), лежащих рядом с main.py
IMG_LANG_SELECTION = "selectlanguage.jpg" 

# --- ПЕРЕВОДЫ (TEXTS) ---
TEXTS = {
    'ru': {
        'img_menu': "glavnoe.jpg", 
        'img_instr': "instrukciya.jpg", 
        
        'main_menu': "<b>Главное меню</b>\n\nВыберите нужный пункт:",
        'btn_instr': "📘 Инструкция",
        'btn_support': "💬 Поддержка",
        'btn_lang': "🌐 Язык",
        'btn_signal': "📲 Получить сигнал",
        'btn_back': "🔙 Назад",
        'instruction': (
            "📘 <b>Инструкция</b>\n\n"
            "1. Нажмите 'Получить сигнал'.\n"
            "2. Зарегистрируйтесь на платформе.\n"
            "3. Внесите минимальный депозит.\n"
            "4. Вернитесь в бота и нажмите 'Проверить'.\n"
            "5. После проверки вам откроется доступ к сигналам.\n\n"
            "<i>Удачи в торговле!</i>"
        ),
        'reg_step_1': (
            "👋 <b>Шаг 1: Регистрация</b>\n\n"
            "Для работы с сигналами необходим аккаунт.\n"
            "Нажми кнопку ниже для регистрации."
        ),
        'btn_reg_link': "🔗 Регистрация",
        'btn_check_reg': "✅ Проверить регистрацию",
        'reg_success_dep_step': (
            "✅ <b>Регистрация подтверждена!</b>\n\n"
            "<b>Шаг 2: Депозит</b>\n"
            "Внесите депозит на платформе, чтобы активировать бота."
        ),
        'btn_check_dep': "💰 Проверить депозит",
        'signals_open': "🚀 <b>Доступ открыт!</b>\n\nНажмите кнопку ниже, чтобы открыть терминал сигналов.",
        'btn_open_app': "📱 ОТКРЫТЬ СИГНАЛЫ",
        'err_no_reg': "❌ Регистрация не найдена.",
        'err_no_dep': "❌ Депозит не найден."
    },
    'en': {
        'img_menu': "mainmenu.jpg",
        'img_instr': "instruction.jpg",

        'main_menu': "<b>Main Menu</b>\n\nSelect an option:",
        'btn_instr': "📘 Instructions",
        'btn_support': "💬 Support",
        'btn_lang': "🌐 Language",
        'btn_signal': "📲 Get Signal",
        'btn_back': "🔙 Back",
        'instruction': (
            "📘 <b>Instructions</b>\n\n"
            "1. Click 'Get Signal'.\n"
            "2. Register on the platform.\n"
            "3. Make a minimum deposit.\n"
            "4. Return to the bot and click 'Check'.\n"
            "5. After verification, signal access will open.\n\n"
            "<i>Good luck trading!</i>"
        ),
        'reg_step_1': (
            "👋 <b>Step 1: Registration</b>\n\n"
            "An account is required to use signals.\n"
            "Click the button below to register."
        ),
        'btn_reg_link': "🔗 Register",
        'btn_check_reg': "✅ Check Registration",
        'reg_success_dep_step': (
            "✅ <b>Registration confirmed!</b>\n\n"
            "<b>Step 2: Deposit</b>\n"
            "Make a deposit on the platform to activate the bot."
        ),
        'btn_check_dep': "💰 Check Deposit",
        'signals_open': "🚀 <b>Access Granted!</b>\n\nClick the button below to open the signal terminal.",
        'btn_open_app': "📱 OPEN SIGNALS",
        'err_no_reg': "❌ Registration not found.",
        'err_no_dep': "❌ Deposit not found."
    },
    'ua': {
        'img_menu': "golovne.jpg",
        'img_instr': "instrukcia.jpg",

        'main_menu': "<b>Головне меню</b>\n\nОберіть пункт:",
        'btn_instr': "📘 Інструкція",
        'btn_support': "💬 Підтримка",
        'btn_lang': "🌐 Мова",
        'btn_signal': "📲 Отримати сигнал",
        'btn_back': "🔙 Назад",
        'instruction': (
            "📘 <b>Інструкція</b>\n\n"
            "1. Натисніть 'Отримати сигнал'.\n"
            "2. Зареєструйтесь на платформі.\n"
            "3. Зробіть мінімальний депозит.\n"
            "4. Поверніться в бота і натисніть 'Перевірити'.\n"
            "5. Після перевірки відкриється доступ до сигналів.\n\n"
            "<i>Успіхів у торгівлі!</i>"
        ),
        'reg_step_1': (
            "👋 <b>Крок 1: Реєстрація</b>\n\n"
            "Для роботи з сигналами потрібен акаунт.\n"
            "Натисніть кнопку нижче для реєстрації."
        ),
        'btn_reg_link': "🔗 Реєстрація",
        'btn_check_reg': "✅ Перевірити реєстрацію",
        'reg_success_dep_step': (
            "✅ <b>Реєстрація підтверджена!</b>\n\n"
            "<b>Крок 2: Депозит</b>\n"
            "Зробіть депозит на платформі, щоб активувати бота."
        ),
        'btn_check_dep': "💰 Перевірити депозит",
        'signals_open': "🚀 <b>Доступ відкрито!</b>\n\nНатисніть кнопку нижче, щоб відкрити термінал сигналів.",
        'btn_open_app': "📱 ВІДКРИТИ СИГНАЛИ",
        'err_no_reg': "❌ Реєстрацію не знайдено.",
        'err_no_dep': "❌ Депозит не знайдено."
    }
}

# --- ИНИЦИАЛИЗАЦИЯ ---
logging.basicConfig(level=logging.INFO)
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase init error: {e}")

app = Flask(__name__)

# Состояния админа
admin_states = {} 

# Кэш языков в памяти для быстродействия и стабильности
# Format: {user_id (int): 'ru'|'en'|'ua'}
USER_LANGS_CACHE = {}

# --- POSTBACK СЕРВЕР ---
@app.route('/postback', methods=['GET', 'POST'])
def postback():
    user_id = request.args.get('sub_id1')
    sumdep = request.args.get('sumdep')
    trader_id = request.args.get('trader_id')
    
    if not user_id: return "OK", 200

    data = {'user_id': user_id, 'registered': True}
    if trader_id: data['trader_id'] = trader_id
    if sumdep:
        try:
            if float(sumdep) > 0:
                data['deposited'] = True
                data['deposit_sum'] = float(sumdep)
        except: pass
        
    try:
        supabase.table('users').upsert(data).execute()
    except Exception as e:
        logging.error(f"DB Error: {e}")
        return "Error", 500
    return "OK", 200

def run_flask():
    # Railway и другие хостинги передают порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 5000))
    # Важно слушать 0.0.0.0, а не 127.0.0.1
    app.run(host='0.0.0.0', port=port)

# --- БД ХЕЛПЕРЫ ---
async def get_user(user_id):
    # Пытаемся получить из кэша для оптимизации
    # Но если там нет, идем в БД
    cached_lang = USER_LANGS_CACHE.get(user_id)
    
    # --- ШАГ 1: Попытка найти пользователя в БД ---
    try:
        res = supabase.table('users').select("*").eq('user_id', str(user_id)).execute()
        if res.data and len(res.data) > 0:
            user = res.data[0]
            # Обновляем кэш языка, если он есть в БД
            if user.get('language'):
                 USER_LANGS_CACHE[user_id] = user['language']
            elif cached_lang:
                # Если в БД нет, а в кэше есть - вернем с кэшем
                user['language'] = cached_lang
            return user
    except Exception as e:
        # Если ошибка связана с отсутствием колонки language, игнорируем при чтении
        print(f"⚠️ [WARNING] DB Select Error (User {user_id}): {e}")

    # --- ШАГ 2: Если пользователь не найден или ошибка - Создаем ---
    print(f"ℹ️ User {user_id} not found in DB. Creating...")
    
    default_lang = cached_lang if cached_lang else 'ru'
    new_user = {
        'user_id': str(user_id), 
        'registered': False, 
        'deposited': False, 
        'language': default_lang
    }

    try:
        # Попытка 1: Вставка с языком
        res_insert = supabase.table('users').insert(new_user).execute()
        print(f"✅ [SUCCESS] User {user_id} successfully added to DB.")
        USER_LANGS_CACHE[user_id] = default_lang
        return new_user
        
    except Exception as e:
        err_str = str(e)
        # Если ошибка связана с отсутствующей колонкой 'language', пробуем вставить без неё
        if "language" in err_str and ("column" in err_str or "PGRST204" in err_str):
            print(f"⚠️ Column 'language' missing in DB. Retrying insert without it...")
            try:
                new_user_no_lang = new_user.copy()
                new_user_no_lang.pop('language', None)
                supabase.table('users').insert(new_user_no_lang).execute()
                print(f"✅ [SUCCESS] User {user_id} added (without language column).")
                
                # Язык храним только в кэше
                USER_LANGS_CACHE[user_id] = default_lang
                return new_user
            except Exception as e2:
                 print(f"❌ [ERROR] Retry failed: {e2}")
        
        print(f"❌ [ERROR] FAILED TO ADD USER {user_id} TO DB!")
        print(f"❌ Error details: {e}")
        
        # Возвращаем объект из памяти, чтобы бот не падал
        return new_user

async def update_user_field(user_id, field, value):
    # Обновляем кэш если это язык
    if field == 'language':
        USER_LANGS_CACHE[user_id] = value
        
    try:
        supabase.table('users').update({field: value}).eq('user_id', str(user_id)).execute()
        return True
    except Exception as e:
        # Не спамим ошибкой если это язык и колонки нет
        if field == 'language' and ("language" in str(e) or "PGRST204" in str(e)):
             return True
             
        print(f"❌ [ERROR] Update failed for {user_id}: {e}")
        return False

async def get_stats():
    try:
        res = supabase.table('users').select("*").execute()
        users = res.data
        total = len(users)
        regs = len([u for u in users if u.get('registered')])
        deps = len([u for u in users if u.get('deposited')])
        return total, regs, deps
    except: return 0, 0, 0

async def get_all_user_ids():
    try:
        res = supabase.table('users').select("user_id").execute()
        return [u['user_id'] for u in res.data]
    except: return []

async def get_users_for_list():
    try:
        res = supabase.table('users').select("*").execute()
        data = res.data
        return data[::-1][:40] 
    except: return []

# --- ОТПРАВКА СООБЩЕНИЙ ---
async def send(update, context, text, kb, photo=None):
    chat_id = update.effective_chat.id
    reply_markup = InlineKeyboardMarkup(kb)
    
    # Определяем, локальный ли файл
    is_local_file = False
    if photo and isinstance(photo, str):
        if not photo.startswith(('http://', 'https://', 'AgAC')): # AgAC - начало file_id телеграма
            if os.path.exists(photo):
                is_local_file = True
            else:
                # Если файл не найден, но строка есть - логируем и шлем без фото или как текст
                logging.warning(f"File not found: {photo}")
                # Можно сбросить photo в None, чтобы отправить просто текст, 
                # или оставить как есть, тогда телеграм может выдать ошибку, если это не валидный file_id
                pass 

    # Хелпер для безопасного удаления
    async def safe_delete():
        if update.callback_query:
            try: await update.callback_query.message.delete()
            except: pass

    if photo:
        # --- ФУНКЦИЯ ОТПРАВКИ/РЕДАКТИРОВАНИЯ ФОТО ---
        async def send_media_msg(is_edit=False):
            # Подготовка медиа (открываем файл если локальный)
            media_obj = open(photo, 'rb') if is_local_file else photo
            
            try:
                if is_edit:
                    media = InputMediaPhoto(media=media_obj, caption=text, parse_mode=ParseMode.HTML)
                    await update.callback_query.edit_message_media(media=media, reply_markup=reply_markup)
                else:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=media_obj,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML
                    )
            finally:
                # Если открывали файл, нужно закрыть, если телеграм сам не закрыл (обычно send_photo читает и все)
                # В питоне при выходе из скоупа файл закроется GC, но явно закрыть надежнее.
                # Однако InputMediaPhoto может читать его асинхронно. 
                # python-telegram-bot обычно справляется с открытыми файлами.
                if is_local_file and hasattr(media_obj, 'close'):
                    media_obj.close()

        # Логика выбора: редактировать или новое
        if update.callback_query and update.callback_query.message.photo:
            try:
                await send_media_msg(is_edit=True)
                return
            except Exception as e:
                pass # Fallback к удалению и отправке нового

        # Если не вышло отредактировать или не было фото -> удаляем старое, шлем новое
        await safe_delete()
        await send_media_msg(is_edit=False)
        
    else:
        # --- ТОЛЬКО ТЕКСТ ---
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    text=text, 
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                await safe_delete()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

# --- ЛОГИКА БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Всегда вызываем get_user, который внутри попробует создать запись в БД
    user = await get_user(user_id)
    saved_lang = user.get('language')
    
    if saved_lang and saved_lang in TEXTS:
        await show_main_menu(update, context, saved_lang)
    else:
        await show_lang_selection(update, context)

async def show_lang_selection(update, context):
    text = "Please select your language / Пожалуйста, выберите язык:"
    kb = [
        [
            InlineKeyboardButton("🇺🇦 UA", callback_data="lang_ua"),
            InlineKeyboardButton("🇬🇧 EN", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 RU", callback_data="lang_ru")
        ]
    ]
    await send(update, context, text, kb, photo=IMG_LANG_SELECTION)

async def show_main_menu(update, context, lang):
    user_id = update.effective_user.id
    user = await get_user(user_id)

    t = TEXTS.get(lang, TEXTS['ru'])
    text = t['main_menu']
    photo = t.get('img_menu')

    # Если депозит есть - кнопка открывает WebApp сразу
    if user.get('deposited'):
        btn_signal = InlineKeyboardButton(t['btn_signal'], web_app=WebAppInfo(url=WEBAPP_URL))
    else:
        # Иначе запускаем флоу регистрации
        btn_signal = InlineKeyboardButton(t['btn_signal'], callback_data="menu_signal")

    kb = [
        [InlineKeyboardButton(t['btn_instr'], callback_data="menu_instruction")],
        [
            InlineKeyboardButton(t['btn_support'], url=SUPPORT_LINK),
            InlineKeyboardButton(t['btn_lang'], callback_data="menu_language")
        ],
        [btn_signal]
    ]
    await send(update, context, text, kb, photo=photo)

async def show_instruction(update, context, lang):
    t = TEXTS.get(lang, TEXTS['ru'])
    text = t['instruction']
    photo = t.get('img_instr')
    kb = [[InlineKeyboardButton(t['btn_back'], callback_data="menu_back")]]
    await send(update, context, text, kb, photo=photo)

async def check_user_status_flow(update, context, lang):
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if user.get('deposited'):
        await show_main_menu(update, context, lang)
    elif user.get('registered'):
        await show_deposit(update, context, lang)
    else:
        await show_registration(update, context, user_id, lang)

async def show_registration(update, context, user_id, lang):
    t = TEXTS.get(lang, TEXTS['ru'])
    sep = '&' if '?' in AFFILIATE_LINK else '?'
    link = f"{AFFILIATE_LINK}{sep}sub_id1={user_id}"
    text = t['reg_step_1']
    kb = [
        [InlineKeyboardButton(t['btn_reg_link'], url=link)],
        [InlineKeyboardButton(t['btn_check_reg'], callback_data="check_reg")],
        [InlineKeyboardButton(t['btn_back'], callback_data="menu_back")]
    ]
    await send(update, context, text, kb) # Фото не передаем

async def show_deposit(update, context, lang):
    t = TEXTS.get(lang, TEXTS['ru'])
    text = t['reg_success_dep_step']
    kb = [
        [InlineKeyboardButton(t['btn_check_dep'], callback_data="check_dep")],
        [InlineKeyboardButton(t['btn_back'], callback_data="menu_back")]
    ]
    await send(update, context, text, kb) # Фото не передаем

async def show_signals(update, context, lang):
    # Fallback
    t = TEXTS.get(lang, TEXTS['ru'])
    text = t['signals_open']
    kb = [[InlineKeyboardButton(t['btn_open_app'], web_app=WebAppInfo(url=WEBAPP_URL))]]
    await send(update, context, text, kb)

# --- АДМИН ПАНЕЛЬ ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID: return

    total, regs, deps = await get_stats()
    
    text = (
        f"👑 <b>Админ Панель</b>\n\n"
        f"👥 Пользователи: <b>{total}</b>\n"
        f"📝 Регистрации: <b>{regs}</b>\n"
        f"💰 Депозиты: <b>{deps}</b>\n\n"
        f"Выберите действие:"
    )
    kb = [
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users_list")],
        [InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")]
    ]
    admin_states[user_id] = None 
    await send(update, context, text, kb)

async def show_users_list(update, context):
    users = await get_users_for_list()
    
    if not users:
        await send(update, context, "Список пуст.", [[InlineKeyboardButton("🔙 Назад", callback_data="admin_refresh")]])
        return

    kb = []
    for u in users:
        uid = u['user_id']
        reg = "✅" if u.get('registered') else "❌"
        dep = "✅" if u.get('deposited') else "❌"
        btn_text = f"{uid} | R:{reg} D:{dep}"
        kb.append([InlineKeyboardButton(btn_text, callback_data=f"adm_manage_{uid}")])
    
    kb.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_refresh")])
    await send(update, context, "<b>👥 Список пользователей (последние 40):</b>\nНажмите на пользователя для управления.", kb)

async def show_user_manage(update, context, target_user_id):
    user = await get_user(target_user_id)
    
    reg_status = "✅ YES" if user.get('registered') else "❌ NO"
    dep_status = "✅ YES" if user.get('deposited') else "❌ NO"
    dep_sum = user.get('deposit_sum', 0)
    trader_id = user.get('trader_id', 'Нет')

    text = (
        f"👤 <b>Управление пользователем</b>\n\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"🆔 Trader ID: <code>{trader_id}</code>\n\n"
        f"®️ Registered: <b>{reg_status}</b>\n"
        f"💰 Deposited: <b>{dep_status}</b>\n"
        f"💵 Сумма: <b>{dep_sum}$</b>"
    )

    btn_reg = InlineKeyboardButton(f"®️ {'Выключить' if user.get('registered') else 'Включить'}", callback_data=f"adm_toggle_reg_{target_user_id}")
    btn_dep = InlineKeyboardButton(f"💰 {'Выключить' if user.get('deposited') else 'Включить'}", callback_data=f"adm_toggle_dep_{target_user_id}")
    btn_sum = InlineKeyboardButton("💵 Изм. сумму", callback_data=f"adm_edit_sum_{target_user_id}")
    btn_back = InlineKeyboardButton("🔙 К списку", callback_data="admin_users_list")

    kb = [
        [btn_reg, btn_dep],
        [btn_sum],
        [btn_back]
    ]
    await send(update, context, text, kb)

# --- ОБРАБОТЧИК КНОПОК ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    # 1. СМЕНА ЯЗЫКА
    if data.startswith("lang_"):
        new_lang = data.split("_")[1]
        await update_user_field(user_id, 'language', new_lang)
        await show_main_menu(update, context, new_lang)
        return

    # 2. Обычная логика
    user = await get_user(user_id)
    lang = user.get('language')
    if not lang or lang not in TEXTS:
        lang = 'ru'

    if data == "menu_instruction": 
        await show_instruction(update, context, lang)
    elif data == "menu_language": 
        await show_lang_selection(update, context)
    elif data == "menu_back": 
        await show_main_menu(update, context, lang)
    elif data == "menu_signal": 
        await check_user_status_flow(update, context, lang)
    
    elif data == "check_reg":
        if user.get('registered'): 
            await show_deposit(update, context, lang)
        else: 
            await context.bot.send_message(user_id, TEXTS[lang]['err_no_reg'])
    
    elif data == "check_dep":
        if user.get('deposited'): 
            await show_main_menu(update, context, lang)
        else: 
            await context.bot.send_message(user_id, TEXTS[lang]['err_no_dep'])

    # --- АДМИН FLOW ---
    elif user_id == ADMIN_ID:
        if data == "admin_refresh":
            await admin_panel(update, context)
            
        elif data == "admin_broadcast":
            admin_states[user_id] = "broadcast"
            await context.bot.send_message(user_id, "✍️ <b>Рассылка:</b> Введите текст или отправьте фото.\n/cancel для отмены.", parse_mode=ParseMode.HTML)

        elif data == "admin_users_list":
            await show_users_list(update, context)

        elif data.startswith("adm_manage_"):
            target_uid = data.split("_")[-1]
            await show_user_manage(update, context, target_uid)

        elif data.startswith("adm_toggle_reg_"):
            target_uid = data.split("_")[-1]
            t_user = await get_user(target_uid)
            new_val = not t_user.get('registered', False)
            await update_user_field(target_uid, 'registered', new_val)
            await show_user_manage(update, context, target_uid)
        
        elif data.startswith("adm_toggle_dep_"):
            target_uid = data.split("_")[-1]
            t_user = await get_user(target_uid)
            new_val = not t_user.get('deposited', False)
            await update_user_field(target_uid, 'deposited', new_val)
            await show_user_manage(update, context, target_uid)

        elif data.startswith("adm_edit_sum_"):
            target_uid = data.split("_")[-1]
            admin_states[user_id] = f"edit_sum_{target_uid}"
            await context.bot.send_message(user_id, f"💵 Введите новую сумму депозита для ID <code>{target_uid}</code>:", parse_mode=ParseMode.HTML)

# --- ОБРАБОТЧИК СООБЩЕНИЙ ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id != ADMIN_ID: return

    current_state = admin_states.get(user_id)

    if text == "/cancel":
        admin_states[user_id] = None
        await update.message.reply_text("❌ Отменено.")
        await admin_panel(update, context)
        return

    if current_state == "broadcast":
        admin_states[user_id] = None
        users_ids = await get_all_user_ids()
        count = 0
        await update.message.reply_text(f"⏳ Рассылка на {len(users_ids)}...")
        for uid in users_ids:
            try:
                await update.message.copy(chat_id=uid)
                count += 1
                await asyncio.sleep(0.05)
            except: pass
        await update.message.reply_text(f"✅ Успешно: {count}")

    elif current_state and current_state.startswith("edit_sum_"):
        target_uid = current_state.split("_")[-1]
        try:
            new_sum = float(text)
            await update_user_field(target_uid, 'deposit_sum', new_sum)
            admin_states[user_id] = None
            await update.message.reply_text("✅ Сумма обновлена.")
            await show_user_manage(update, context, target_uid)
        except:
            await update.message.reply_text("❌ Введите число (например 10.5) или /cancel")

# --- ЗАПУСК ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app_bot = Application.builder().token(TOKEN).build()
    
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("admin", admin_panel))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    
    print("Bot started...")
    app_bot.run_polling()

if __name__ == '__main__':

    main()




