import requests
import random
import string
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# --- Configuration ---
BOT_TOKEN = '8518792607:AAE_7a4jESQA-aT5yMTsCbsNnxUPOagbbag'
BASE_URL = 'https://api.mail.tm'

user_sessions = {}

def generate_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_mail_domain():
    try:
        res = requests.get(f"{BASE_URL}/domains", timeout=10).json()
        return res['hydra:member'][0]['domain']
    except Exception as e:
        logging.error(f"Domain error: {e}")
        return "mail.tm"

def create_mail_acc(email, password):
    data = {"address": email, "password": password}
    try:
        res = requests.post(f"{BASE_URL}/accounts", json=data, timeout=10)
        return res.status_code == 201
    except:
        return False

def fetch_token(email, password):
    data = {"address": email, "password": password}
    try:
        res = requests.post(f"{BASE_URL}/token", json=data, timeout=10)
        return res.json().get('token')
    except:
        return None

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📧 Create New Mail", callback_data='create_mail')],
        [InlineKeyboardButton("📥 Check Inbox", callback_data='check_inbox')],
        [InlineKeyboardButton("🗑 Delete Current", callback_data='delete_mail')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✨ **━━━━ SAKil Temp Mail ━━━━** ✨\n\n"
        "Welcome! আমি আপনাকে দ্রুত এবং নিরাপদ টেম্পোরারি মেইল সার্ভিস দিতে পারি।\n\n"
        "🚀 **Fast | Free | Secure**\n\n"
        "নিচের মেনু থেকে একটি অপশন সিলেক্ট করুন:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'create_mail':
        domain = get_mail_domain()
        email = f"{generate_id()}@{domain}"
        password = generate_id(12)
        
        if create_mail_acc(email, password):
            token = fetch_token(email, password)
            user_sessions[user_id] = {'email': email, 'token': token, 'pass': password}
            
            text = (
                "✨ **SAKil Temp Mail - Ready** ✨\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Password:** `{password}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💡 *মেইলটি কপি করতে উপরে ক্লিক করুন।*"
            )
            await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ মেইল তৈরি করতে সমস্যা হচ্ছে।", reply_markup=main_menu_keyboard())

    elif query.data == 'check_inbox':
        if user_id not in user_sessions:
            await query.edit_message_text("❌ আপনার কোনো একটিভ মেইল নেই!", reply_markup=main_menu_keyboard())
            return

        token = user_sessions[user_id]['token']
        headers = {'Authorization': f'Bearer {token}'}
        try:
            res = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=10).json()
            messages = res.get('hydra:member', [])

            if not messages:
                await query.edit_message_text("📭 **Inbox Empty!**\nএখনো কোনো মেইল আসেনি।", reply_markup=back_to_menu_keyboard(), parse_mode='Markdown')
            else:
                inbox_text = "📬 **Your Inbox:**\n\n"
                for msg in messages[:5]:
                    inbox_text += f"👤 **From:** {msg['from']['address']}\n📝 **Subject:** {msg['intro']}\n\n"
                await query.edit_message_text(inbox_text, reply_markup=back_to_menu_keyboard(), parse_mode='Markdown')
        except:
            await query.edit_message_text("❌ ইনবক্স চেক করতে সমস্যা হচ্ছে।", reply_markup=main_menu_keyboard())

    elif query.data == 'back_to_menu':
        current_email = user_sessions.get(user_id, {}).get('email', 'No Active Mail')
        text = (
            "✨ **━━━━ SAKil Temp Mail ━━━━** ✨\n\n"
            f"📧 **Current Email:** `{current_email}`\n\n"
            "আপনি এখন মেনুতে আছেন। কি করতে চান?"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

    elif query.data == 'delete_mail':
        user_sessions.pop(user_id, None)
        await query.edit_message_text("🗑 **Mail Deleted!**\nনতুন মেইল তৈরি করুন।", reply_markup=main_menu_keyboard(), parse_mode='Markdown')

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    print("SAKil Temp Mail Bot is Live! 🚀")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

def fetch_token(email, password):
    data = {"address": email, "password": password}
    try:
        res = requests.post(f"{BASE_URL}/token", json=data, timeout=10)
        return res.json().get('token')
    except:
        return None

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📧 Create New Mail", callback_data='create_mail')],
        [InlineKeyboardButton("📥 Check Inbox", callback_data='check_inbox')],
        [InlineKeyboardButton("🗑 Delete Current", callback_data='delete_mail')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✨ **━━━━ SAKil Temp Mail ━━━━** ✨\n\n"
        "Welcome! আমি আপনাকে দ্রুত এবং নিরাপদ টেম্পোরারি মেইল সার্ভিস দিতে পারি।\n\n"
        "🚀 **Fast | Free | Secure**\n\n"
        "নিচের মেনু থেকে একটি অপশন সিলেক্ট করুন:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'create_mail':
        domain = get_mail_domain()
        email = f"{generate_id()}@{domain}"
        password = generate_id(12)
        
        if create_mail_acc(email, password):
            token = fetch_token(email, password)
            user_sessions[user_id] = {'email': email, 'token': token, 'pass': password}
            
            text = (
                "✨ **SAKil Temp Mail - Ready** ✨\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Password:** `{password}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💡 *মেইলটি কপি করতে উপরে ক্লিক করুন।*"
            )
            await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ মেইল তৈরি করতে সমস্যা হচ্ছে। আবার চেষ্টা করুন।", reply_markup=main_menu_keyboard())

    elif query.data == 'check_inbox':
        if user_id not in user_sessions:
            await query.edit_message_text("❌ আপনার কোনো একটিভ মেইল নেই!", reply_markup=main_menu_keyboard())
            return

        token = user_sessions[user_id]['token']
        headers = {'Authorization': f'Bearer {token}'}
        try:
            res = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=10).json()
            messages = res.get('hydra:member', [])

            if not messages:
                await query.edit_message_text("📭 **Inbox Empty!**\nএখনো কোনো মেইল আসেনি।", reply_markup=back_to_menu_keyboard(), parse_mode='Markdown')
            else:
                inbox_text = "📬 **Your Inbox:**\n\n"
                for msg in messages[:5]:
                    inbox_text += f"👤 **From:** {msg['from']['address']}\n📝 **Subject:** {msg['intro']}\n\n"
                await query.edit_message_text(inbox_text, reply_markup=back_to_menu_keyboard(), parse_mode='Markdown')
        except:
            await query.edit_message_text("❌ ইনবক্স চেক করতে সমস্যা হচ্ছে।", reply_markup=main_menu_keyboard())

    elif query.data == 'back_to_menu':
        current_email = user_sessions.get(user_id, {}).get('email', 'No Active Mail')
        text = (
            "✨ **━━━━ SAKil Temp Mail ━━━━** ✨\n\n"
            f"📧 **Current Email:** `{current_email}`\n\n"
            "আপনি এখন মেনুতে আছেন। কি করতে চান?"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

    elif query.data == 'delete_mail':
        user_sessions.pop(user_id, None)
        await query.edit_message_text("🗑 **Mail Deleted!**\nনতুন মেইল তৈরি করতে নিচের বাটনে ক্লিক করুন।", reply_markup=main_menu_keyboard(), parse_mode='Markdown')

def main():
    # Application builder v20+ এর জন্য সঠিক পদ্ধতি
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("SAKil Temp Mail Bot is Live! 🚀")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
        [InlineKeyboardButton("📧 Create New Mail", callback_data='create_mail')],
        [InlineKeyboardButton("📥 Check Inbox", callback_data='check_inbox')],
        [InlineKeyboardButton("🗑 Delete Current", callback_data='delete_mail')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]])

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✨ **━━━━ SAKil Temp Mail ━━━━** ✨\n\n"
        "Welcome! আমি আপনাকে দ্রুত এবং নিরাপদ টেম্পোরারি মেইল সার্ভিস দিতে পারি।\n\n"
        "🚀 **Fast | Free | Secure**\n\n"
        "নিচের মেনু থেকে একটি অপশন সিলেক্ট করুন:"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'create_mail':
        domain = get_mail_domain()
        email = f"{generate_id()}@{domain}"
        password = generate_id(12)
        
        if create_mail_acc(email, password):
            token = fetch_token(email, password)
            user_sessions[user_id] = {'email': email, 'token': token, 'pass': password}
            
            text = (
                "✨ **SAKil Temp Mail - Ready** ✨\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Password:** `{password}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💡 *মেইলটি কপি করতে উপরে ক্লিক করুন।*"
            )
            await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

    elif query.data == 'check_inbox':
        if user_id not in user_sessions:
            await query.edit_message_text("❌ আপনার কোনো একটিভ মেইল নেই!", reply_markup=main_menu_keyboard())
            return

        token = user_sessions[user_id]['token']
        headers = {'Authorization': f'Bearer {token}'}
        res = requests.get(f"{BASE_URL}/messages", headers=headers).json()
        messages = res.get('hydra:member', [])

        if not messages:
            await query.edit_message_text("📭 **Inbox Empty!**\nএখনো কোনো মেইল আসেনি।", reply_markup=back_to_menu_keyboard(), parse_mode='Markdown')
        else:
            inbox_text = "📬 **Your Inbox:**\n\n"
            for msg in messages[:5]: # Show last 5 messages
                inbox_text += f"👤 **From:** {msg['from']['address']}\n📝 **Subject:** {msg['intro']}\n\n"
            
            await query.edit_message_text(inbox_text, reply_markup=back_to_menu_keyboard(), parse_mode='Markdown')

    elif query.data == 'back_to_menu':
        current_email = user_sessions.get(user_id, {}).get('email', 'No Active Mail')
        text = (
            "✨ **━━━━ SAKil Temp Mail ━━━━** ✨\n\n"
            f"📧 **Current Email:** `{current_email}`\n\n"
            "আপনি এখন মেনুতে আছেন। কি করতে চান?"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

    elif query.data == 'delete_mail':
        if user_id in user_sessions:
            del user_sessions[user_id]
            await query.edit_message_text("🗑 **Mail Deleted!**\nনতুন মেইল তৈরি করতে নিচের বাটনে ক্লিক করুন।", reply_markup=main_menu_keyboard(), parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ ডিলিট করার মতো কোনো মেইল নেই।", reply_markup=main_menu_keyboard())

# --- Launcher ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("SAKil Temp Mail Bot is Live! 🚀")
    app.run_polling()

if __name__ == '__main__':
    main()
