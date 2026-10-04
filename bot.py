import sqlite3
from datetime import datetime, timedelta
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ================= BUNLARI DƏYİŞ =================
TOKEN = "8949659457:AAFoW7ZyRSW-l-Umu8rW6EtL_XSLSdXuiYY"
DB_FILE = "elanlar.db"    # elanlar bu lokal faylda saxlanır
PER_PAGE = 5              # bir səhifədə neçə elan göstərilsin
# =================================================

MODES = {"al": "Hesab al", "sat": "Hesab sat"}

# Kateqoriyalar
ITEMS = {
    "plat": ("Platformalar", ["YouTube", "Instagram", "TikTok", "Facebook", "Snapchat", "Twitter (X)", "Discord"]),
    "game": ("Oyunlar", [
        "PUBG Mobile", "Free Fire", "Brawl Stars", "FIFA (EA SPORTS FC)",
        "eFootball", "Roblox", "Fortnite", "Call of Duty", "Counter-Strike 2"
    ])
}

# Hər platforma/oyun üçün 2 sual və hazır cavab düymələri
QUESTIONS = {
    "YouTube": [
        ("Abunəçi", "Kanalın neçə abunəçisi var?", ["0 - 1k", "1k - 10k", "10k - 50k", "50k+"]),
        ("Monetizasiya", "Monetizasiya açıqdır?", ["Bəli", "Xeyr"]),
    ],
    "Instagram": [
        ("İzləyici", "Hesabın neçə izləyicisi var?", ["0 - 1k", "1k - 10k", "10k - 50k", "50k+"]),
        ("Mövzu", "Hesabın ana mövzusu nədir?", ["Şəxsi / Blog", "Humor / Meme", "Mağaza / Biznes", "Digər"]),
    ],
    "TikTok": [
        ("İzləyici", "Hesabın neçə izləyicisi var?", ["0 - 1k", "1k - 10k", "10k - 50k", "50k+"]),
        ("Ümumi Like", "Hesabın ümumi like sayı nə qədərdir?", ["0 - 10k", "10k - 100k", "100k - 500k", "500k+"]),
    ],
    "Facebook": [
        ("İzləyici/Dost", "Neçə izləyici və ya dost var?", ["0 - 1k", "1k - 5k", "5k - 20k", "20k+"]),
        ("Növ", "Hesabın növsü nədir?", ["Şəxsi profil", "Səhifə (Page)", "Qrup"]),
    ],
    "Snapchat": [
        ("İzləyici", "Hesabın neçə izləyicisi var?", ["0 - 1k", "1k - 10k", "10k+"]),
        ("Snap Score", "Snap score nə qədərdir?", ["0 - 10k", "10k - 100k", "100k+"]),
    ],
    "Twitter (X)": [
        ("İzləyici", "Hesabın neçə izləyicisi var?", ["0 - 1k", "1k - 10k", "10k - 50k", "50k+"]),
        ("Təsdiq", "Təsdiqli (mavi tik) hesabdırmı?", ["Bəli", "Xeyr"]),
    ],
    "Discord": [
        ("Hesab yaşı", "Hesab neçənci ildə yaradılıb?", ["2015-2018", "2019-2021", "2022-2024", "2025+"]),
        ("Nitro/Rozet", "Nitro və ya nadir rozet varmı?", ["Var", "Yoxdur"]),
    ],
    "PUBG Mobile": [
        ("Level", "Hesabın səviyyəsi (level) nə qədərdir?", ["1 - 40", "41 - 60", "61 - 70", "71+"]),
        ("Rank", "Mövcud rank nədir?", ["Bronz/Gümüş/Qızıl", "Platin/Almaz", "Tac/Esh", "Fatih"]),
    ],
    "Free Fire": [
        ("Level", "Hesabın səviyyəsi neçədir?", ["1 - 30", "31 - 50", "51 - 65", "66+"]),
        ("Bağlantı", "Hesab neyə bağlıdır?", ["Facebook", "Google", "VK"]),
    ],
    "Brawl Stars": [
        ("Kubok", "Hesabın ümumi kubok sayı nə qədərdir?", ["0 - 5k", "5k - 15k", "15k - 30k", "30k+"]),
        ("Brawler", "Neçə brawler açıqdır?", ["1 - 30", "31 - 50", "51 - 70", "Hamısı / Demək olar hamısı"]),
    ],
    "FIFA (EA SPORTS FC)": [
        ("Platforma", "Hansı platformadadır?", ["Mobile", "PlayStation", "Xbox", "PC"]),
        ("Reytinq", "Komandanın ümumi reytinqi neçədir?", ["80 - 90", "91 - 95", "96 - 100", "100+"]),
    ],
    "eFootball": [
        ("Platforma", "Hansı platformadadır?", ["Mobile", "PlayStation / Xbox", "PC"]),
        ("Güc", "Komandanın ümumi gücü nə qədərdir?", ["2000 - 2800", "2801 - 3000", "3000+"]),
    ],
    "Roblox": [
        ("Robux/Limited", "Hesabda Robux və ya Limited əşya var?", ["Var", "Yoxdur"]),
        ("Hesab yaşı", "Hesab neçənci ildə yaradılıb?", ["2006-2015", "2016-2020", "2021-2024", "2025+"]),
    ],
    "Fortnite": [
        ("Skin sayı", "Hesabda neçə skin var?", ["1 - 20", "21 - 50", "51 - 100", "100+"]),
        ("OG Skin", "OG (Köhnə/Nadir) skinlər varmı?", ["Var", "Yoxdur"]),
    ],
    "Call of Duty": [
        ("Platforma", "Hansı platformadadır?", ["Mobile", "PlayStation / Xbox", "PC"]),
        ("Level", "Hesabın səviyyəsi nə qədərdir?", ["1 - 50", "51 - 150", "151 - 250", "250+ / Max"]),
    ],
    "Counter-Strike 2": [
        ("Prime", "Prime statusu varmı?", ["Bəli", "Xeyr"]),
        ("Rank/Oynama", "Premier / Faceit statusu necədir?", ["Başlanğıc", "Orta", "Yüksək"]),
    ],
}

KIND_NAME = {"s": "Elan", "b": "Alış sorğusu"}

# ------------------------- LOKAL BAZA (SQLITE) -------------------------
def db():
    return sqlite3.connect(DB_FILE)

def init_db():
    with db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                cat TEXT NOT NULL,
                item TEXT NOT NULL,
                price TEXT NOT NULL,
                a1 TEXT NOT NULL,
                a2 TEXT NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )

# 7 gündən köhnə olan bütün elanları avtomatik silən funksiya
def clean_old_ads():
    with db() as con:
        con.execute("DELETE FROM ads WHERE created < datetime('now', '-7 days')")

def add_ad(kind, user_id, username, cat, item, price, answers):
    clean_old_ads()
    with db() as con:
        con.execute(
            "INSERT INTO ads (kind, user_id, username, cat, item, price, a1, a2) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (kind, user_id, username, cat, item, price, answers[0], answers[1]),
        )

def count_ads(kind, item):
    clean_old_ads()
    with db() as con:
        return con.execute(
            "SELECT COUNT(*) FROM ads WHERE kind = ? AND item = ?", (kind, item)
        ).fetchone()[0]

def get_ads(kind, item, offset, limit):
    clean_old_ads()
    with db() as con:
        return con.execute(
            "SELECT id, username, price, a1, a2, created FROM ads "
            "WHERE kind = ? AND item = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (kind, item, limit, offset),
        ).fetchall()

def my_ads(user_id):
    clean_old_ads()
    with db() as con:
        return con.execute(
            "SELECT id, kind, item, price FROM ads WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()

def delete_ad(ad_id, user_id):
    with db() as con:
        con.execute("DELETE FROM ads WHERE id = ? AND user_id = ?", (ad_id, user_id))

# ------------------------- MENYULAR -------------------------
def chunk(buttons, size):
    return [buttons[i:i + size] for i in range(0, len(buttons), size)]

def main_menu():
    rows = [
        [InlineKeyboardButton("Hesab al", callback_data="a:al")],
        [InlineKeyboardButton("Hesab sat", callback_data="a:sat")],
        [InlineKeyboardButton("Elanlarım", callback_data="m")],
    ]
    return "Xoş gəldiniz! Nə etmək istəyirsiniz?", InlineKeyboardMarkup(rows)

def category_menu(mode):
    rows = [
        [InlineKeyboardButton("Platformalar", callback_data=f"l:{mode}:plat")],
        [InlineKeyboardButton("Oyunlar", callback_data=f"l:{mode}:game")],
        [InlineKeyboardButton("Ana menyu", callback_data="home")],
    ]
    return f"Seçim: **{MODES[mode]}**\n\nKateqoriyanı seçin:", InlineKeyboardMarkup(rows)

def list_menu(mode, cat):
    title, items = ITEMS[cat]
    buttons = [
        InlineKeyboardButton(name, callback_data=f"f:{mode}:{cat}:{i}")
        for i, name in enumerate(items)
    ]
    rows = chunk(buttons, 2)
    rows.append([
        InlineKeyboardButton("Geri", callback_data=f"a:{mode}"),
        InlineKeyboardButton("Ana menyu", callback_data="home"),
    ])
    return f"**{MODES[mode]}** > **{title}**\n\nSeçim edin:", InlineKeyboardMarkup(rows)

def final_menu(mode, cat, index):
    name = ITEMS[cat][1][index]
    rows = []
    if mode == "al":
        total = count_ads("s", name)
        text = f"**Hesab almaq**\n\nSeçildi: **{name}**\nMövcud satış elanı: **{total}**"
        if total > 0:
            rows.append([InlineKeyboardButton(f"Elanlara bax ({total})", callback_data=f"v:s:{cat}:{index}:0")])
        else:
            text += "\n\nHələlik bu kateqoriyada satış elanı yoxdur."
        rows.append([InlineKeyboardButton("Alış sorğusu yerləşdir", callback_data=f"s:b:{cat}:{index}")])
    else:
        total = count_ads("b", name)
        text = f"**Hesab satmaq**\n\nSeçildi: **{name}**\nAlıcı sorğusu sayı: **{total}**"
        rows.append([InlineKeyboardButton("Satış elanı yerləşdir", callback_data=f"s:s:{cat}:{index}")])
        if total > 0:
            rows.append([InlineKeyboardButton(f"Alıcı sorğularına bax ({total})", callback_data=f"v:b:{cat}:{index}:0")])

    rows.append([
        InlineKeyboardButton("Geri", callback_data=f"l:{mode}:{cat}"),
        InlineKeyboardButton("Ana menyu", callback_data="home"),
    ])
    return text, InlineKeyboardMarkup(rows)

def view_menu(kind, cat, index, offset):
    name = ITEMS[cat][1][index]
    total = count_ads(kind, name)
    back_mode = "al" if kind == "s" else "sat"
    back_row = [
        InlineKeyboardButton("Geri", callback_data=f"f:{back_mode}:{cat}:{index}"),
        InlineKeyboardButton("Ana menyu", callback_data="home"),
    ]
    if total == 0:
        return f"**{name}**\n\nHələlik heç bir elan tapılmadı.", InlineKeyboardMarkup([back_row])

    offset = max(0, min(offset, total - 1))
    items = get_ads(kind, name, offset, PER_PAGE)
    labels = [q[0] for q in QUESTIONS[name]]
    price_label = "💰 Qiymət" if kind == "s" else "💰 Büdcə"
    person = "👤 Satıcı" if kind == "s" else "👤 Alıcı"
    heading = "🛒 SATIŞ ELANLARI" if kind == "s" else "📢 ALICI SORĞULARI"

    # Başlıq hissəsi daha aydın və səliqəli şəkildə formalaşdırılır
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━",
        f"📌 **{name.upper()}** — {heading}",
        f"📊 Göstərilir: {offset + 1}-{offset + len(items)} / Cəmi: {total}",
        f"━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    for n, (ad_id, username, price, a1, a2, created) in enumerate(items, start=offset + 1):
        msg = f"Salam, {name} elanınız (#{ad_id}) ilə bağlı yazıram. Hələ aktualdırmı?"
        clean_url = f"https://t.me/{username}?text={quote(msg)}"
        
        # Elan kartı - daha səliqəli görünüş
        lines.append(
            f"🔹 **ELAN #{ad_id}**\n"
            f"├ {price_label}: `{price}`\n"
            f"├ 📊 {labels[0]}: {a1}\n"
            f"├ ⚙️ {labels[1]}: {a2}\n"
            f"└ {person}: [@{username}]({clean_url})\n"
            f"───────────────"
        )

    rows = []
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️ Əvvəlki", callback_data=f"v:{kind}:{cat}:{index}:{max(0, offset - PER_PAGE)}"))
    if offset + PER_PAGE < total:
        nav.append(InlineKeyboardButton("Növbəti ➡️", callback_data=f"v:{kind}:{cat}:{index}:{offset + PER_PAGE}"))
    if nav:
        rows.append(nav)
        
    rows.append(back_row)
    return "\n".join(lines), InlineKeyboardMarkup(rows)

def my_menu(user_id):
    items = my_ads(user_id)
    if not items:
        text = "Sizin aktiv elanınız və ya sorğunuz yoxdur."
        rows = []
    else:
        text = "Sizin aktiv elanlarınız və sorğularınız (7 gündən sonra avtomatik silinir):\n\n" + "\n".join(
            f"#{ad_id} | {KIND_NAME[kind]} | {item} | {price}"
            for ad_id, kind, item, price in items
        )
        rows = [[InlineKeyboardButton(f"🗑 Sil: #{ad_id} {item}", callback_data=f"d:{ad_id}")] for ad_id, _, item, _ in items[:20]]
        
    rows.append([InlineKeyboardButton("Ana menyu", callback_data="home")])
    return text, InlineKeyboardMarkup(rows)

# Formanın menyu görünüşünü yaradır
def form_prompt(form):
    item, kind, step = form["item"], form["kind"], form["step"]
    head = f"**{item}** ({KIND_NAME[kind]})\n\n"
    
    if step < 2:
        label, question, options = QUESTIONS[item][step]
        text = f"{head}Mərhələ {step + 1}/3:\n**{question}**"
        
        buttons = [
            [InlineKeyboardButton(opt, callback_data=f"opt:{idx}")]
            for idx, opt in enumerate(options)
        ]
        buttons.append([InlineKeyboardButton("Ləğv et", callback_data="home")])
        return text, InlineKeyboardMarkup(buttons)
    else:
        text = f"{head}Mərhələ 3/3:\n" + ("**Qiyməti yazın** (məs: 25 AZN):" if kind == "s" else "**Büdcənizi yazın** (məs: 30 AZN):")
        cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Ləğv et", callback_data="home")]])
        return text, cancel_btn

# ------------------------- HANDLERLƏR -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("form", None)
    text, markup = main_menu()
    await update.message.reply_text(text, reply_markup=markup)

async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    kind = parts[0]

    if kind == "home":
        context.user_data.pop("form", None)
        text, markup = main_menu()
    elif kind == "a":
        text, markup = category_menu(parts[1])
    elif kind == "l":
        text, markup = list_menu(parts[1], parts[2])
    elif kind == "f":
        text, markup = final_menu(parts[1], parts[2], int(parts[3]))
    elif kind == "v":
        text, markup = view_menu(parts[1], parts[2], int(parts[3]), int(parts[4]))
    elif kind == "m":
        text, markup = my_menu(query.from_user.id)
    elif kind == "d":
        delete_ad(int(parts[1]), query.from_user.id)
        text, markup = my_menu(query.from_user.id)
    elif kind == "s":
        if not query.from_user.username:
            await query.answer(
                "Əlaqə saxlanılması üçün Telegram @username mütləqdir. "
                "Zəhmət olmasa Telegram Settings-də username təyin edin.",
                show_alert=True,
            )
            return
        ad_kind, cat, index = parts[1], parts[2], int(parts[3])
        form = {
            "kind": ad_kind,
            "cat": cat,
            "item": ITEMS[cat][1][index],
            "step": 0,
            "answers": [],
        }
        context.user_data["form"] = form
        text, markup = form_prompt(form)
    elif kind == "opt":
        form = context.user_data.get("form")
        if not form:
            text, markup = main_menu()
            await query.edit_message_text(text, reply_markup=markup)
            return

        opt_idx = int(parts[1])
        item = form["item"]
        step = form["step"]
        
        selected_option = QUESTIONS[item][step][2][opt_idx]
        form["answers"].append(selected_option)
        form["step"] += 1

        text, markup = form_prompt(form)
    else:
        return

    await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    form = context.user_data.get("form")
    if not form:
        text, markup = main_menu()
        await update.message.reply_text(text, reply_markup=markup)
        return

    if form["step"] < 2:
        await update.message.reply_text("Zəhmət olmasa cavabı yuxarıdakı **düymələrdən** seçin.", parse_mode="Markdown")
        return

    value = update.message.text.strip()

    if len(value) > 50:
        await update.message.reply_text("Çox uzundur. Qısa yazın (max 50 simvol).")
        return

    user = update.effective_user
    if not user.username:
        await update.message.reply_text("Username tapılmadı. Zəhmət olmasa ayarlarınızda username təyin edin.")
        context.user_data.pop("form", None)
        return

    # Məlumatları bazaya əlavə et
    add_ad(form["kind"], user.id, user.username, form["cat"], form["item"], value, form["answers"])
    context.user_data.pop("form", None)

    labels = [q[0] for q in QUESTIONS[form["item"]]]
    price_label = "Qiymət" if form["kind"] == "s" else "Büdcə"
    person = "Satıcı" if form["kind"] == "s" else "Alıcı"
    
    summary = (
        f"**{KIND_NAME[form['kind']]} yerləşdirildi!**\n\n"
        f"Kanal/Oyun: **{form['item']}**\n"
        f"{price_label}: **{value}**\n"
        f"{labels[0]}: {form['answers'][0]}\n"
        f"{labels[1]}: {form['answers'][1]}\n"
        f"{person}: @{user.username}\n\n"
        f"ℹ️ *Elanınız 7 gün ərzində aktiv qalacaq.*"
    )
    
    rows = [
        [InlineKeyboardButton("Elanlarım", callback_data="m")],
        [InlineKeyboardButton("Ana menyu", callback_data="home")],
    ]
    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

def main():
    init_db()
    clean_old_ads()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    print("Bot uğurla başladıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
