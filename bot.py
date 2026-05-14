import os
import requests
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8105173071:AAGazfT6NIT3VqT6iayapnGpmm9alc9XvVY"
LOGO_FILE = "logo.png"
ADMIN_ID = 8486116629 # << උඹේ ID එක දාපන්
USERS_FILE = "users.json"

PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = "https://paper-bot-5ddc.onrender.com" # https://your-app.onrender.com

SUBJECTS = {
    "physics": {
        "name": "⚛️ Physics", "emoji": "⚛️", "years": "2016-2021",
        "papers": {
            "phy_2021": {"year": "2021", "id": "1ICLaJDoStL3J3wRDmPSJmqihX1tf6ORR"},
            "phy_2020": {"year": "2020", "id": "1jbpikdzS2tj1Q_X2tOiKYNVPYtZSg-tz"},
            "phy_2019": {"year": "2019", "id": "1N1I1-HzZdU1_YJ04I5GipyOcpQsn11uF"},
            "phy_2018": {"year": "2018", "id": "1HWCycDpK82X6ENdrc775BIr3x-CVBAYx"},
            "phy_2017": {"year": "2017", "id": "14jLO0EA2U4g9O1HX_7bHEjt4cCWgh4LS"},
            "phy_2016": {"year": "2016", "id": "1yP8OWb5e0ce2dKGV_Yrb95WGozDOXIYY"}
        }
    },
    "chemistry": {
        "name": "🧪 Chemistry", "emoji": "🧪", "years": "2016-2024",
        "papers": {
            "chem_2024": {"year": "2024", "id": "1i6JkE6gvFfa4I5Z8AiGFClmKDECCIifg"},
            "chem_2021": {"year": "2021", "id": "1nBr3BIdVWEgfOPNw1auOYdE6x9N-k6mu"},
            "chem_2020": {"year": "2020", "id": "1EjtW5p8HuOAo4QH5RBpHXi1FxvxZpk0I"},
            "chem_2019": {"year": "2019", "id": "1r8ugsWaHd7B1Rk56fr__hR1TCKhoLRIx"},
            "chem_2018": {"year": "2018", "id": "1FNKEb3ElNF-K830K93g87Q0uAvIqoXnm"},
            "chem_2017": {"year": "2017", "id": "14jLO0EA2U4g9O1HX_7bHEjt4cCWgh4LS"},
            "chem_2016": {"year": "2016", "id": "1XqsC_8__XMv6XhkABCIqBeu2FZk7wMzX"}
        }
    },
    "biology": {
        "name": "🧬 Biology", "emoji": "🧬", "years": "2011-2023",
        "papers": {
            "bio_2023": {"year": "2023", "id": "1dsc1-TXuXySD2Tb26pZafqZLoZUL3DBy"},
            "bio_2022": {"year": "2022", "id": "1US231ibZFSYwVqEQWmfFXrI2KYumY-S1"},
            "bio_2021": {"year": "2021", "id": "1U7fnfUZ6wsslU7L7eAxZXXTgEjViKdEm"},
            "bio_2020": {"year": "2020", "id": "1uyfLx5tIoaEkZuu9-S9iJXkoK1w5YH5u"},
            "bio_2019": {"year": "2019", "id": "1yWEcJFPxXmHsWqtN-mZWb3vytfq_RWAv"},
            "bio_2018": {"year": "2018", "id": "1LNL7D8cRJekfuGCUMkCXoDdBqeqw-g"},
            "bio_2017": {"year": "2017", "id": "1fCEvtD07JA32TwP_pudB31mptU-MVE3-"},
            "bio_2016": {"year": "2016", "id": "1qd3D35yz-TglQ_3yJDcqPm7f7Vj8Uxjx"},
            "bio_2015": {"year": "2015", "id": "1OcaqyWatw1E9AU6gsbhyDOJSUyEnXOFL"},
            "bio_2014": {"year": "2014", "id": "1tO8s6-fFa9QEoHVF14LDeSWq9CTKV2Vg"},
            "bio_2013": {"year": "2013", "id": "1-w0U7c_rP_sUzTwNXJjiuCvAoHIc3IJg"},
            "bio_2012": {"year": "2012", "id": "1Vple1rcjSM_ZCB2hFpHi2g26ZwOmnqFD"},
            "bio_2011": {"year": "2011", "id": "1m46B0XwT0wILto45xmfJbLVyVO7SotwI"}
        }
    },
    "maths": {
        "name": "📐 Combined Maths", "emoji": "📐", "years": "2012-2023",
        "papers": {
            "maths_2023": {"year": "2023", "id": "1KnfBXqXDt8XdQgo-fJ23N3dXVYM3iNnS"},
            "maths_2022": {"year": "2022", "id": "1rV1FfRrLZViSyhdBscYiwU3Z0HRBJGqc"},
            "maths_2021": {"year": "2021", "id": "1USBVSnWN3HoKz0N_c1j2w7x0xmtA_436"},
            "maths_2020": {"year": "2020", "id": "1WPASU4XjshbDAcjDN08O452oJ3J3ZdOu"},
            "maths_2019": {"year": "2019", "id": "1x5X4GOnkM56waRoSjpZW21ijNf62i39v"},
            "maths_2018": {"year": "2018", "id": "1FH8POD5jAEP1zlMV-Df6d4YiTtwkUR55"},
            "maths_2017": {"year": "2017", "id": "1DILTRLHAsasTPEeO31_aOvP63xvUA1jD"},
            "maths_2016": {"year": "2016", "id": "1-Mp8RFORpf1vXw_-547olWS5Ema-NNKO"},
            "maths_2015": {"year": "2015", "id": "14VFJKE0wPuurBzJnY2_yVYq8st6mCRr7"},
            "maths_2014": {"year": "2014", "id": "1TuVDuV_WPV8lIdTI1_U_B4e7XVMECv5d"},
            "maths_2013": {"year": "2013", "id": "19F-Q8jYfIwGXvVO9SCpeTlqN003Syq3A"},
            "maths_2012": {"year": "2012", "id": "1UwCR0d--pDEGwdiK9hwuIMRnSYpiw-7Z"}
        }
    },
    "agri": {
        "name": "🌾 Agri Science", "emoji": "🌾", "years": "2015-2023",
        "papers": {
            "agri_2023": {"year": "2023", "id": "PASTE_2023_AGRI_ID"},
            "agri_2022": {"year": "2022", "id": "PASTE_2022_AGRI_ID"},
            "agri_2021": {"year": "2021", "id": "PASTE_2021_AGRI_ID"},
            "agri_2020": {"year": "2020", "id": "PASTE_2020_AGRI_ID"},
            "agri_2019": {"year": "2019", "id": "PASTE_2019_AGRI_ID"},
            "agri_2018": {"year": "2018", "id": "PASTE_2018_AGRI_ID"},
            "agri_2017": {"year": "2017", "id": "PASTE_2017_AGRI_ID"},
            "agri_2016": {"year": "2016", "id": "PASTE_2016_AGRI_ID"},
            "agri_2015": {"year": "2015", "id": "PASTE_2015_AGRI_ID"}
        }
    }
}

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

def get_total_papers():
    return sum(len(sub["papers"]) for sub in SUBJECTS.values())

def download_gdrive(file_id):
    session = requests.Session()
    response = session.get("https://drive.google.com/uc", params={'export': 'download', 'id': file_id}, stream=True)
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break
    if token:
        response = session.get("https://drive.google.com/uc", params={'export': 'download', 'id': file_id, 'confirm': token}, stream=True)
    return response

def main_menu():
    keyboard = []
    row = []
    for sub_key, sub_data in SUBJECTS.items():
        count = len(sub_data["papers"])
        btn = InlineKeyboardButton(f"{sub_data['emoji']} {sub_key.title()} ({count})", callback_data=f"sub_{sub_key}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(f"📊 Total Papers: {get_total_papers()}", callback_data="stats")])
    return InlineKeyboardMarkup(keyboard)

def papers_menu(subject_key):
    keyboard = []
    papers = SUBJECTS[subject_key]["papers"]
    sorted_papers = dict(sorted(papers.items(), reverse=True))
    row = []
    for paper_key, paper_data in sorted_papers.items():
        btn = InlineKeyboardButton(f"📘 {paper_data['year']}", callback_data=f"paper_{subject_key}_{paper_key}")
        row.append(btn)
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back to Subjects", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    caption = """
🌟 𝐋𝐚𝐧𝐤𝐚 𝐏𝐚𝐩𝐞𝐫 𝐇𝐮𝐛 🇱🇰 🌟
━━━━━━━━━━━━
⚛️ Physics | 🧪 Chemistry | 🧬 Biology
📐 Maths | 🌾 Agri Science
📚 A/L Past Papers Sinhala Medium
━━━━━━━━━━━━
👇 Select Subject Below
    """
    try:
        with open(LOGO_FILE, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, reply_markup=main_menu())
    except FileNotFoundError:
        await update.message.reply_text(text=caption, reply_markup=main_menu())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id!= ADMIN_ID:
        await update.message.reply_text("❌ Admin Only Command")
        return
    if not context.args:
        await update.message.reply_text("📢 Usage:\n/broadcast Your Message Here")
        return
    message = " ".join(context.args)
    users = load_users()
    await update.message.reply_text(f"📤 Broadcasting to {len(users)} users...")
    success = 0
    failed = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Announcement\n━━━━━━━━━━━━\n{message}\n━━━━━━━━━━━━\n_𝐋𝐚𝐧𝐤𝐚 𝐏𝐚𝐩𝐞𝐫 𝐇𝐮𝐛 🇱🇰_")
            success += 1
        except:
            failed += 1
    await update.message.reply_text(f"✅ Broadcast Complete\n━━━━━━━━━━━━\n📤 Sent: {success}\n❌ Failed: {failed}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        caption = """
🌟 𝐋𝐚𝐧𝐤𝐚 𝐏𝐚𝐩𝐞𝐫 𝐇𝐮𝐛 🇱🇰 🌟
━━━━━━━━━━━━
⚛️ Physics | 🧪 Chemistry | 🧬 Biology
📐 Maths | 🌾 Agri Science
📚 A/L Past Papers Sinhala Medium
━━━━━━━━━━━━
👇 Select Subject Below
        """
        await query.message.edit_caption(caption=caption, reply_markup=main_menu())
        return

    if data == "stats":
        stats = "📊 Bot Statistics\n━━━━━━━━━━━━\n"
        for sub_data in SUBJECTS.values():
            stats += f"{sub_data['emoji']} {sub_data['name']}: {len(sub_data['papers'])} Papers\n"
        stats += f"━━━━━━━━━━━━\n🎯 Total: {get_total_papers()} Papers\n👥 Users: {len(load_users())}"
        await query.answer(stats, show_alert=True)
        return

    if data.startswith("sub_"):
        subject_key = data.split("_")[1]
        sub = SUBJECTS[subject_key]
        caption = f"""
{sub['emoji']} {sub['name']} Past Papers
━━━━━━━━━━━━
📅 Years: {sub['years']}
📚 Total: {len(sub['papers'])} Papers
━━━━━━━━━━━━
👇 Select Year Below
        """
        await query.message.edit_caption(caption=caption, reply_markup=papers_menu(subject_key))
        return

    if data.startswith("paper_"):
        _, subject_key, paper_key = data.split("_", 2)
        paper = SUBJECTS[subject_key]["papers"][paper_key]
        sub = SUBJECTS[subject_key]

        if "PASTE_" in paper['id']:
            await query.message.reply_text(f"⚠️ {sub['name']} {paper['year']} Paper එක තාම Add කරලා නෑ මචං")
            return

        msg = await query.message.reply_text(f"⏳ Downloading...\n{sub['emoji']} {sub['name']} {paper['year']}")
        try:
            r = download_gdrive(paper['id'])
            size_bytes = int(r.headers.get('Content-Length', 0))
            size_mb = size_bytes / 1024 / 1024

            await msg.edit_text(f"📤 Uploading...\n{sub['emoji']} {sub['name']} {paper['year']}")
            await query.message.reply_document(
                document=r.content,
                filename=f"A/L_{sub['name']}_{paper['year']}_Sinhala.pdf",
                caption=f"✅ {sub['emoji']} {sub['name']} {paper['year']} Sinhala\n💾 Size: {size_mb:.1f}MB\n_𝐋𝐚𝐧𝐤𝐚 𝐏𝐚𝐩𝐞𝐫 𝐇𝐮𝐛 🇱🇰_"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Error: File එක Public කරලා නෑ\n📄 {sub['name']} {paper['year']}")

# Flask App for Webhook
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CallbackQueryHandler(button_handler))

@app.route("/")
def home():
    return "Bot is Running ✅"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

def main():
    # Webhook set කරනවා
    application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == '__main__':
    main()
