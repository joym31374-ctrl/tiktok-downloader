import json, os, time, qrcode, asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "8729101567:AAEVvwr6SvfmEe47oCNFraRibpfQjad3E3o"
BOT_USERNAME = "@Video_Audio_Photo_Bot"

FORCE_CHANNEL = "@Shadow_ST_12"
FORCE_CHANNEL_2 = "@The_Shadow_123"
AD_LINK = "https://t.me/The_Shadow_123"

DB_FILE = "files.json"
files_db = {}
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, 'r') as f: files_db = json.load(f)
    except: files_db = {}

def save_db():
    with open(DB_FILE, 'w') as f: json.dump(files_db, f)

waiting = {}
user_mode = {}

MAIN_KEYBOARD = ReplyKeyboardMarkup([
    ["🎬 Video Link", "🎵 Audio Link"],
    ["🖼️ Photo Link"],
    ["📱 Video QR", "📱 Audio QR"],
    ["📱 Photo QR"]
], resize_keyboard=True)

SEVEN_DAYS = 7*24*60*60

async def is_joined(user_id, context, channel):
    try:
        member = await context.bot.get_chat_member(channel, user_id)
        return member.status in ['member','administrator','creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if FORCE_CHANNEL:
        joined1 = await is_joined(update.effective_user.id, context, FORCE_CHANNEL)
        joined2 = await is_joined(update.effective_user.id, context, FORCE_CHANNEL_2)
        if not joined1 or not joined2:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"📢 Join {FORCE_CHANNEL}", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")],
                [InlineKeyboardButton(f"📢 Join {FORCE_CHANNEL_2}", url=f"https://t.me/{FORCE_CHANNEL_2.replace('@','')}")],
                [InlineKeyboardButton("✅ Joined - Check", callback_data="check_join")]
            ])
            await update.message.reply_text(
                f"⚠️ ফাইল পেতে হলে ২টা চ্যানেলে Join করতে হবে:\n\n1️⃣ {FORCE_CHANNEL}\n2️⃣ {FORCE_CHANNEL_2}\n\nJoin করে Check বাটনে ক্লিক করো",
                reply_markup=btn
            )
            return

    if context.args and context.args[0].startswith("file_"):
        file_key = context.args[0].replace("file_", "")
        if file_key not in files_db:
            await update.message.reply_text("❌ ফাইল মেয়াদ উত্তীর্ণ (7 দিন)।")
            return
        waiting[update.effective_user.id] = file_key
        await update.message.reply_text("🔒 ফাইল লক করা আছে। পাসওয়ার্ড পাঠাও:")
        return

    await update.message.reply_text(
        "✅ File Store Bot Ready\n\n"
        f"📢 Channel 1: {FORCE_CHANNEL}\n"
        f"📢 Channel 2: {FORCE_CHANNEL_2}\n\n"
        "🎬 Video Link / 📱 Video QR\n🎵 Audio Link / 📱 Audio QR\n🖼️ Photo Link / 📱 Photo QR",
        reply_markup=MAIN_KEYBOARD
    )

async def check_join_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    j1 = await is_joined(query.from_user.id, context, FORCE_CHANNEL)
    j2 = await is_joined(query.from_user.id, context, FORCE_CHANNEL_2)
    if j1 and j2:
        await query.message.reply_text("✅ Join Done! এখন /start দাও")
    else:
        await query.message.reply_text("❌ এখনো Join করোনি")

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    uid = update.effective_user.id
    if "Video Link" in txt: user_mode[uid]="video_link"; await update.message.reply_text("🎬 ভিডিও পাঠাও")
    elif "Audio Link" in txt: user_mode[uid]="audio_link"; await update.message.reply_text("🎵 অডিও পাঠাও")
    elif "Photo Link" in txt: user_mode[uid]="photo_link"; await update.message.reply_text("🖼️ ছবি পাঠাও")
    elif "Video QR" in txt: user_mode[uid]="video_qr"; await update.message.reply_text("📱 Video QR এর জন্য ভিডিও পাঠাও")
    elif "Audio QR" in txt: user_mode[uid]="audio_qr"; await update.message.reply_text("📱 Audio QR এর জন্য অডিও পাঠাও")
    elif "Photo QR" in txt: user_mode[uid]="photo_qr"; await update.message.reply_text("📱 Photo QR এর জন্য ছবি পাঠাও")

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    mode = user_mode.get(uid, "video_link")
    password = update.message.caption or "1234"
    file_id, f_type = None, "video"
    if update.message.video: file_id=update.message.video.file_id; f_type="video"
    elif update.message.audio: file_id=update.message.audio.file_id; f_type="audio"
    elif update.message.photo: file_id=update.message.photo[-1].file_id; f_type="photo"
    elif update.message.document: file_id=update.message.document.file_id; f_type="document"
    if not file_id: return
    file_key = str(int(time.time()))
    files_db[file_key] = {"id":file_id, "pass":password, "type":f_type, "time":time.time()}
    save_db()
    long_link = f"https://t.me/{BOT_USERNAME}?start=file_{file_key}"
    qr = qrcode.make(long_link)
    path = f"/tmp/qr_{file_key}.png"
    qr.save(path)

    if "qr" in mode:
        await update.message.reply_photo(
            photo=open(path,"rb"),
            caption=f"✅ {mode.upper()} + EARNING ON\n\n🔑 Pass: {password}\n🔗 Link: {long_link}\n\n📢 2টা চ্যানেল:\n1. https://t.me/Shadow_ST_12\n2. https://t.me/The_Shadow_123"
        )
    else:
        await update.message.reply_text(f"✅ {mode.upper()} Ready\n\n🔑 {password}\n🔗 {long_link}\n⏰ 7 দিন")

async def check_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in waiting and update.message.text:
        file_key = waiting[uid]
        if file_key not in files_db: return
        if update.message.text.strip() == files_db[file_key]["pass"]:
            f = files_db[file_key]
            cap = f"📢 Join: @Shadow_ST_12 | @The_Shadow_123"
            if f["type"]=="video": await update.message.reply_video(video=f["id"], caption=cap)
            elif f["type"]=="audio": await update.message.reply_audio(audio=f["id"], caption=cap)
            elif f["type"]=="photo": await update.message.reply_photo(photo=f["id"], caption=cap)
            else: await update.message.reply_document(document=f["id"], caption=cap)
            del waiting[uid]
        else:
            await update.message.reply_text("❌ ভুল পাসওয়ার্ড!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_cb, pattern="check_join"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(MessageHandler(filters.VIDEO | filters.PHOTO | filters.AUDIO | filters.VOICE | filters.Document.ALL, save_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_pass))
    app.run_polling()

if __name__=="__main__": main()
