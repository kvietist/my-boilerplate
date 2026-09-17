import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# --- CONFIGURATIONS ---
TELEGRAM_TOKEN = "8976674295:AAE_K_YlHxzHcwJJcYYLB8wBDdmcnkG0nuE"
FASTAPI_URL = "http://127.0.0.1:8000"
MINI_APP_URL = "https://blog-app-rose-rho.vercel.app/"

# Tracks user JWT login states in-memory
USER_TOKENS = {}

# Conversation States
WAITING_FOR_REG_USER, WAITING_FOR_REG_PASS = 1, 2
WAITING_FOR_LOGIN_USER, WAITING_FOR_LOGIN_PASS = 3, 4
WAITING_FOR_DIARY_CONTENT = 5
WAITING_FOR_DIARY_ID = 6

# --- MAIN MENU HUD ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🚀 Launch LifeTracker",
            web_app=WebAppInfo(url=MINI_APP_URL),
        )]
    ])
    welcome_text = (
        "📖 Welcome to LifeTracker!\n\n"
        "Write your diaries daily and save them securely."
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, reply_markup=reply_markup
        )
    return ConversationHandler.END

# --- AUTH FLOW: REGISTER ---
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📝 Please enter a new username:")
    return WAITING_FOR_REG_USER

async def get_reg_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reg_user"] = update.message.text
    await update.message.reply_text("🔑 Great! Now choose a strong password:")
    return WAITING_FOR_REG_PASS

async def complete_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    username = context.user_data["reg_user"]
    
    # 🎯 FIX 1: Truncate the username automatically to stay under the 15-character limit
    if len(username) > 15:
        username = username[:15]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FASTAPI_URL}/users/get_info", 
                json={
                    "username": username, 
                    "password": password,
                    "email": f"{username}@test.com",  # 🎯 FIX 2: Added required email placeholder
                    "age": 20                          # 🎯 FIX 3: Added required age placeholder
                } 
            )
            
            if response.status_code == 201:
                await update.message.reply_text(f"✅ Account created successfully with username: {username}! Please click Log In to connect.")
            else:
                detail = response.json().get('detail', 'Registration rejected.')
                await update.message.reply_text(f"❌ Registration failed: {detail}")
                
        except Exception as e:
            await update.message.reply_text("❌ System connection error.")
            
    return await return_to_menu_prompt(update, context)


# --- AUTH FLOW: LOGIN ---
async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔓 Please enter your account username:")
    return WAITING_FOR_LOGIN_USER

async def get_login_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["login_user"] = update.message.text
    await update.message.reply_text("🔑 Enter your password:")
    return WAITING_FOR_LOGIN_PASS

async def complete_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    username = context.user_data["login_user"]
    user_id = update.message.from_user.id
    
    async with httpx.AsyncClient() as client:
        try:
            # Matches OAuth2 standard token endpoint routing schemas
            response = await client.post(
                f"{FASTAPI_URL}/login", 
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                token_data = response.json()
                USER_TOKENS[user_id] = token_data["access_token"]
                await update.message.reply_text("🔒 Authorization validated! Connection secure.")
            else:
                await update.message.reply_text("❌ Authentication failed. Incorrect credentials.")
        except Exception:
            await update.message.reply_text("❌ Connection error.")
            
    return await return_to_menu_prompt(update, context)

# --- DIARY FLOW: ADD ENTRY ---
async def start_add_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id not in USER_TOKENS:
        await query.edit_message_text("⚠️ Verification needed. Please use the 'Log In' engine first.")
        return await return_to_menu_prompt_from_query(query, context)
        
    await query.edit_message_text("✍️ Type your diary entry text block and send it:")
    return WAITING_FOR_DIARY_CONTENT

async def complete_add_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = update.message.text
    user_id = update.message.from_user.id
    headers = {"Authorization": f"Bearer {USER_TOKENS[user_id]}"}
    
    async with httpx.AsyncClient() as client:
        try:
            # Matches schemas database requirement variables
            response = await client.post(
                f"{FASTAPI_URL}/diaries/", 
                json={"title": "Telegram Note", "content": content},
                headers=headers
            )
            if response.status_code in [200, 201]:
                await update.message.reply_text("📝 Content stored successfully in database.")
            else:
                await update.message.reply_text("❌ Request packaging rejected by schemas.")
        except Exception:
            await update.message.reply_text("❌ Backend processing failure.")
            
    return await return_to_menu_prompt(update, context)

# --- DIARY FLOW: DELETE ENTRY ---
async def start_delete_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in USER_TOKENS:
        await query.edit_message_text("⚠️ Verification required. Please authenticate via the menu.")
        return await return_to_menu_prompt_from_query(query, context)

    await query.edit_message_text("🗑️ Enter the ID of the diary entry to delete:")
    return WAITING_FOR_DIARY_ID

async def complete_delete_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        diary_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid numeric diary ID.")
        return WAITING_FOR_DIARY_ID

    context.user_data["target_delete_id"] = diary_id
    return await trigger_delete_confirmation(update, context)

async def trigger_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entry_id = context.user_data.get("target_delete_id")
    if entry_id is None:
        await update.message.reply_text("❌ No diary entry was selected.")
        return await return_to_menu_prompt(update, context)

    keyboard = [
        [
            InlineKeyboardButton("🚨 Yes, Delete It", callback_data=f"confirm_del_{entry_id}"),
            InlineKeyboardButton("❌ No, Keep It", callback_data="btn_menu"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    warning = (
        "⚠️ *CRITICAL WARNING* ⚠️\n\n"
        f"Are you sure you want to permanently delete diary entry ID *{entry_id}*?\n"
        "This cannot be undone."
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            warning, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            warning, reply_markup=reply_markup, parse_mode="Markdown"
        )
    return ConversationHandler.END

async def execute_final_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in USER_TOKENS:
        await query.edit_message_text("⚠️ Your session expired. Please log in again.")
        return await return_to_menu_prompt_from_query(query, context)

    try:
        entry_id = int(query.data.removeprefix("confirm_del_"))
    except ValueError:
        await query.edit_message_text("❌ Invalid diary entry ID.")
        return await return_to_menu_prompt_from_query(query, context)

    headers = {"Authorization": f"Bearer {USER_TOKENS[user_id]}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{FASTAPI_URL}/diaries/{entry_id}", headers=headers
            )
            if response.status_code == 204:
                await query.edit_message_text("🗑️ Diary entry deleted successfully.")
            elif response.status_code == 404:
                await query.edit_message_text("❌ Diary entry not found.")
            elif response.status_code == 401:
                await query.edit_message_text("❌ You are not authorized to delete this entry.")
            else:
                await query.edit_message_text("❌ Diary entry could not be deleted.")
        except httpx.HTTPError:
            await query.edit_message_text("❌ Connection error processing deletion.")

    context.user_data.pop("target_delete_id", None)

    return await return_to_menu_prompt_from_query(query, context)

# --- DIARY FLOW: VIEW ENTRIES ---
async def list_diaries_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id not in USER_TOKENS:
        await query.edit_message_text("⚠️ Verification required. Please authenticate via the menu.")
        return await return_to_menu_prompt_from_query(query, context)
        
    headers = {"Authorization": f"Bearer {USER_TOKENS[user_id]}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{FASTAPI_URL}/diaries/", headers=headers)
            if response.status_code == 200:
                entries = response.json()
                if not entries:
                    await query.edit_message_text("📖 Database records empty.")
                else:
                    msg = "📋 Your System Entries:\n\n"
                    for item in entries:
                        msg += f"🆔 ID: {item.get('id')} | 📌 {item.get('title')}\n✍️ {item.get('content')}\n\n"
                    await query.edit_message_text(msg)
            else:
                await query.edit_message_text("❌ Database retrieval denied.")
        except Exception:
            await query.edit_message_text("❌ Network timeout error.")
            
    return await return_to_menu_prompt_from_query(query, context)

# --- UTILITIES ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action canceled.")
    return await start(update, context)

async def return_to_menu_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 Return to Main Menu", callback_data="btn_menu")]]
    await update.message.reply_text("Click below to go back:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def return_to_menu_prompt_from_query(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 Return to Main Menu", callback_data="btn_menu")]]
    await query.message.reply_text("Click below to go back:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

# --- BOOT ENGINE ---
if __name__ == "__main__":
    print("Launching Integrated Telegram-FastAPI App Layout...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Multi-state dialogue tree tracking system
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_registration, pattern="^btn_register$"),
            CallbackQueryHandler(start_login, pattern="^btn_login$"),
            CallbackQueryHandler(start_add_diary, pattern="^btn_add$"),
            CallbackQueryHandler(start_delete_diary, pattern="^btn_delete$"),
        ],
        states={
            WAITING_FOR_REG_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reg_username)],
            WAITING_FOR_REG_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_registration)],
            WAITING_FOR_LOGIN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_login_username)],
            WAITING_FOR_LOGIN_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_login)],
            WAITING_FOR_DIARY_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_add_diary)],
            WAITING_FOR_DIARY_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_delete_diary)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(list_diaries_click, pattern="^btn_list$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^btn_menu$"))
    app.add_handler(CallbackQueryHandler(execute_final_delete, pattern=r"^confirm_del_\d+$"))
    app.add_handler(conv_handler)
    
    app.run_polling()
