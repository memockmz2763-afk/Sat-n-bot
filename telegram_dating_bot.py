import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ── CONFIG ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8632605510:AAHDVoziOlhFJZkUmdXKBMDNaGDRztgz4qU")
ADMIN_IDS = [8573319049]

# ── VERİ DOSYALARI ────────────────────────────────────────────────────────────
GIRLS_FILE = "girls.json"
USERS_FILE = "users.json"

# ── VERİ YÖNETİMİ ─────────────────────────────────────────────────────────────
def load_girls():
    if os.path.exists(GIRLS_FILE):
        with open(GIRLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"id": "elif",   "name": "Elif",   "age": 24, "city": "İstanbul", "bio": "Müzik seven, neşeli biriyim 🎵",        "emoji": "👩‍🦰", "photo": None, "voice_price": 50,  "video_price": 100, "online": True},
        {"id": "ayse",   "name": "Ayşe",   "age": 22, "city": "Ankara",   "bio": "Kitap kurdu, kahve bağımlısı ☕📚",      "emoji": "👩‍🦱", "photo": None, "voice_price": 60,  "video_price": 120, "online": True},
        {"id": "merve",  "name": "Merve",  "age": 26, "city": "İzmir",    "bio": "Dans etmeyi ve gezmek seviyorum 💃",    "emoji": "👱‍♀️", "photo": None, "voice_price": 75,  "video_price": 150, "online": False},
        {"id": "zeynep", "name": "Zeynep", "age": 23, "city": "Bursa",    "bio": "Doğa yürüyüşleri ve fotoğrafçılık 📸",  "emoji": "👩‍🦳", "photo": None, "voice_price": 50,  "video_price": 90,  "online": True},
        {"id": "selin",  "name": "Selin",  "age": 25, "city": "Antalya",  "bio": "Denizi ve güneşi çok severim 🌊☀️",    "emoji": "👩",   "photo": None, "voice_price": 80,  "video_price": 160, "online": True},
        {"id": "dilan",  "name": "Dilan",  "age": 21, "city": "Gaziantep","bio": "Yemek yapmayı seviyorum 🍽️",            "emoji": "👩‍🍳", "photo": None, "voice_price": 45,  "video_price": 85,  "online": True},
    ]

def save_girls(girls):
    with open(GIRLS_FILE, "w", encoding="utf-8") as f:
        json.dump(girls, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(user_id: int):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"id": user_id, "balance": 0, "name": ""}
        save_users(users)
    return users[uid]

def update_user(user_id: int, data: dict):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"id": user_id, "balance": 0, "name": ""}
    users[uid].update(data)
    save_users(users)

def is_admin(user_id: int):
    return user_id in ADMIN_IDS

# ── PROFİL KARTI ─────────────────────────────────────────────────────────────
def girl_card_text(girl):
    status = "🟢 Çevrimiçi" if girl["online"] else "🔴 Çevrimdışı"
    return (
        f"{girl['emoji']} *{girl['name']}* | {girl['age']} yaş | {girl['city']}\n"
        f"_{girl['bio']}_\n\n"
        f"📞 Sesli Görüşme: *{girl['voice_price']} ₺*\n"
        f"🎥 Görüntülü Görüşme: *{girl['video_price']} ₺*\n"
        f"{status}"
    )

def girl_keyboard(girl, index, total):
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Önceki", callback_data=f"profile_{index-1}"))
    if index < total - 1:
        nav_row.append(InlineKeyboardButton("Sonraki ➡️", callback_data=f"profile_{index+1}"))
    action_row = [
        InlineKeyboardButton(f"📞 Sesli ({girl['voice_price']}₺)", callback_data=f"voice_{girl['id']}"),
        InlineKeyboardButton(f"🎥 Görüntülü ({girl['video_price']}₺)", callback_data=f"video_{girl['id']}"),
    ]
    keyboard = []
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append(action_row)
    keyboard.append([InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

async def send_girl_profile(update, context, girl, index, total, edit=False):
    """Fotoğraflı veya fotoğrafsız profil gönder"""
    kb = girl_keyboard(girl, index, total)
    text = girl_card_text(girl)

    if edit:
        # Fotoğraflı mesajı edit edemeyiz, yeni gönderiyoruz
        try:
            await update.callback_query.message.delete()
        except:
            pass
        msg = update.callback_query.message
        chat_id = msg.chat_id
        if girl.get("photo"):
            try:
                await context.bot.send_photo(chat_id, photo=girl["photo"], caption=text,
                                             parse_mode="Markdown", reply_markup=kb)
                return
            except:
                pass
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)
    else:
        chat_id = update.effective_chat.id
        if girl.get("photo"):
            try:
                await context.bot.send_photo(chat_id, photo=girl["photo"], caption=text,
                                             parse_mode="Markdown", reply_markup=kb)
                return
            except:
                pass
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

# ── /START ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_users()
    is_new = str(user.id) not in users

    update_user(user.id, {"name": user.first_name, "username": user.username or ""})
    u = get_user(user.id)

    # Admin'e yeni kullanıcı bildirimi
    if is_new:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🔔 *Yeni Kullanıcı Katıldı!*\n\n"
                    f"👤 İsim: {user.first_name}\n"
                    f"🆔 ID: `{user.id}`\n"
                    f"📱 Username: @{user.username or 'yok'}\n"
                    f"👥 Toplam Kullanıcı: {len(users)+1}",
                    parse_mode="Markdown"
                )
            except:
                pass

    text = (
        f"💘 *Merhaba {user.first_name}!*\n\n"
        "Tanışma Botu'na hoş geldin! 🌸\n\n"
        "Dilediğin bayanla *sesli* veya *görüntülü* görüşme yap.\n\n"
        f"💰 Bakiyen: *{u['balance']} ₺*\n\n"
        "👇 Aşağıdan bir seçenek seç:"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👩 Bayanları Gör 💫", callback_data="profile_0")],
        [InlineKeyboardButton("🔥 Çevrimiçi Bayanlar", callback_data="online_girls")],
        [InlineKeyboardButton("💰 Bakiyem", callback_data="my_balance")],
        [InlineKeyboardButton("ℹ️ Nasıl Çalışır?", callback_data="how_it_works")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ── /ADMİN ────────────────────────────────────────────────────────────────────
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Yetkisiz erişim!")
        return
    await show_admin_panel(update.message, context)

async def show_admin_panel(msg, context):
    users = load_users()
    girls = load_girls()
    text = (
        f"🛠 *Admin Paneli*\n\n"
        f"👥 Toplam Kullanıcı: *{len(users)}*\n"
        f"👩 Toplam Bayan: *{len(girls)}*"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👩 Bayan Ekle", callback_data="admin_add_girl"),
         InlineKeyboardButton("🗑 Bayan Sil", callback_data="admin_del_girl")],
        [InlineKeyboardButton("✏️ Fiyat Güncelle", callback_data="admin_price"),
         InlineKeyboardButton("🟢 Çevrimiçi Yap", callback_data="admin_online")],
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💰 Bakiye Ekle", callback_data="admin_add_balance")],
        [InlineKeyboardButton("👥 Kullanıcı Listesi", callback_data="admin_users")],
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ── CALLBACK HANDLER ──────────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    girls = load_girls()
    girls_dict = {g["id"]: g for g in girls}

    # ── Profil Göster ──
    if data.startswith("profile_"):
        index = int(data.split("_")[1])
        if not girls:
            await query.edit_message_text("😔 Henüz bayan eklenmedi!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))
            return
        index = min(index, len(girls)-1)
        girl = girls[index]
        await send_girl_profile(update, context, girl, index, len(girls), edit=True)

    # ── Sesli Görüşme ──
    elif data.startswith("voice_"):
        girl = girls_dict.get(data.split("_")[1])
        if not girl: return
        if not girl["online"]:
            await query.edit_message_text(f"😔 *{girl['name']}* şu an çevrimdışı!", parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data=f"profile_{girls.index(girl)}")]]))
            return
        u = get_user(query.from_user.id)
        if u["balance"] < girl["voice_price"]:
            await query.edit_message_text(
                f"❌ *Yetersiz Bakiye!*\n\n💰 Bakiyen: *{u['balance']}₺*\nGerekli: *{girl['voice_price']}₺*\n\nAdmin ile iletişime geç.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))
            return
        await query.edit_message_text(
            f"📞 *{girl['name']}* ile Sesli Görüşme\n\n💰 Ücret: *{girl['voice_price']} ₺*\n💵 Bakiyen: *{u['balance']} ₺*\n\nOnaylıyor musun?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Onayla & Bağlan", callback_data=f"pay_voice_{girl['id']}")],
                [InlineKeyboardButton("❌ İptal", callback_data=f"profile_{girls.index(girl)}")],
            ]))

    # ── Görüntülü Görüşme ──
    elif data.startswith("video_"):
        girl = girls_dict.get(data.split("_")[1])
        if not girl: return
        if not girl["online"]:
            await query.edit_message_text(f"😔 *{girl['name']}* şu an çevrimdışı!", parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data=f"profile_{girls.index(girl)}")]]))
            return
        u = get_user(query.from_user.id)
        if u["balance"] < girl["video_price"]:
            await query.edit_message_text(
                f"❌ *Yetersiz Bakiye!*\n\n💰 Bakiyen: *{u['balance']}₺*\nGerekli: *{girl['video_price']}₺*\n\nAdmin ile iletişime geç.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))
            return
        await query.edit_message_text(
            f"🎥 *{girl['name']}* ile Görüntülü Görüşme\n\n💰 Ücret: *{girl['video_price']} ₺*\n💵 Bakiyen: *{u['balance']} ₺*\n\nOnaylıyor musun?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Onayla & Bağlan", callback_data=f"pay_video_{girl['id']}")],
                [InlineKeyboardButton("❌ İptal", callback_data=f"profile_{girls.index(girl)}")],
            ]))

    # ── Ödeme: Sesli ──
    elif data.startswith("pay_voice_"):
        girl = girls_dict.get(data.replace("pay_voice_", ""))
        if not girl: return
        u = get_user(query.from_user.id)
        if u["balance"] < girl["voice_price"]:
            await query.edit_message_text("❌ Yetersiz bakiye!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))
            return
        new_balance = u["balance"] - girl["voice_price"]
        update_user(query.from_user.id, {"balance": new_balance})
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(admin_id,
                    f"💸 *Satış!*\n👤 {query.from_user.first_name} (`{query.from_user.id}`)\n"
                    f"👩 {girl['name']} | 📞 Sesli | 💰 {girl['voice_price']}₺", parse_mode="Markdown")
            except: pass
        await query.edit_message_text(
            f"✅ *Bağlantı Kuruldu!*\n\n📞 *{girl['name']}* ile sesli görüşme başlıyor...\n\n"
            f"🔗 Görüşme Linki: `https://call.example.com/{girl['id']}/voice`\n\n"
            f"💰 Kalan bakiye: *{new_balance} ₺*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))

    # ── Ödeme: Görüntülü ──
    elif data.startswith("pay_video_"):
        girl = girls_dict.get(data.replace("pay_video_", ""))
        if not girl: return
        u = get_user(query.from_user.id)
        if u["balance"] < girl["video_price"]:
            await query.edit_message_text("❌ Yetersiz bakiye!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))
            return
        new_balance = u["balance"] - girl["video_price"]
        update_user(query.from_user.id, {"balance": new_balance})
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(admin_id,
                    f"💸 *Satış!*\n👤 {query.from_user.first_name} (`{query.from_user.id}`)\n"
                    f"👩 {girl['name']} | 🎥 Görüntülü | 💰 {girl['video_price']}₺", parse_mode="Markdown")
            except: pass
        await query.edit_message_text(
            f"✅ *Bağlantı Kuruldu!*\n\n🎥 *{girl['name']}* ile görüntülü görüşme başlıyor...\n\n"
            f"🔗 Görüşme Linki: `https://call.example.com/{girl['id']}/video`\n\n"
            f"💰 Kalan bakiye: *{new_balance} ₺*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))

    # ── Çevrimiçi Bayanlar ──
    elif data == "online_girls":
        online = [g for g in girls if g["online"]]
        if not online:
            await query.edit_message_text("😔 Şu an çevrimiçi bayan yok!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))
            return
        text = "🟢 *Çevrimiçi Bayanlar:*\n\n"
        for g in online:
            text += f"{g['emoji']} *{g['name']}* — {g['age']} yaş, {g['city']}\n📞 {g['voice_price']}₺  |  🎥 {g['video_price']}₺\n\n"
        buttons = [[InlineKeyboardButton(f"{g['emoji']} {g['name']}", callback_data=f"profile_{girls.index(g)}")] for g in online]
        buttons.append([InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    # ── Bakiye ──
    elif data == "my_balance":
        u = get_user(query.from_user.id)
        await query.edit_message_text(
            f"💰 *Bakiye Bilgisi*\n\n"
            f"👤 {query.from_user.first_name}\n"
            f"💵 Bakiye: *{u['balance']} ₺*\n\n"
            f"Bakiye yüklemek için admin ile iletişime geç.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))

    # ── Nasıl Çalışır ──
    elif data == "how_it_works":
        await query.edit_message_text(
            "ℹ️ *Nasıl Çalışır?*\n\n"
            "1️⃣ Bayan seç\n"
            "2️⃣ Sesli 📞 veya Görüntülü 🎥 seç\n"
            "3️⃣ Bakiyenden düşülür 💰\n"
            "4️⃣ Anında bağlan! 🔗\n\n"
            "🔒 Tüm görüşmeler gizlidir.\n"
            "💳 Bakiye yüklemek için admin ile iletişime geç.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👩 Bayanları Gör", callback_data="profile_0")],
                [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")],
            ]))

    # ── Admin: Bayan Ekle ──
    elif data == "admin_add_girl":
        if not is_admin(query.from_user.id): return
        context.user_data["action"] = "add_girl_name"
        context.user_data["new_girl"] = {}
        await query.edit_message_text(
            "👩 *Yeni Bayan Ekleme*\n\nAdım 1/7: Bayanın *adını* yaz:",
            parse_mode="Markdown")

    # ── Admin: Bayan Sil ──
    elif data == "admin_del_girl":
        if not is_admin(query.from_user.id): return
        if not girls:
            await query.edit_message_text("Silinecek bayan yok!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="admin_back")]]))
            return
        buttons = [[InlineKeyboardButton(f"🗑 {g['name']}", callback_data=f"del_girl_{g['id']}")] for g in girls]
        buttons.append([InlineKeyboardButton("⬅️ Geri", callback_data="admin_back")])
        await query.edit_message_text("Hangi bayanı silmek istiyorsun?", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("del_girl_"):
        if not is_admin(query.from_user.id): return
        gid = data.replace("del_girl_", "")
        girls = [g for g in girls if g["id"] != gid]
        save_girls(girls)
        await query.edit_message_text("✅ Bayan silindi!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_back")]]))

    # ── Admin: Fiyat ──
    elif data == "admin_price":
        if not is_admin(query.from_user.id): return
        buttons = [[InlineKeyboardButton(
            f"✏️ {g['name']} | 📞{g['voice_price']}₺ 🎥{g['video_price']}₺",
            callback_data=f"price_{g['id']}")] for g in girls]
        buttons.append([InlineKeyboardButton("⬅️ Geri", callback_data="admin_back")])
        await query.edit_message_text("Fiyat güncellenecek bayanı seç:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("price_"):
        if not is_admin(query.from_user.id): return
        gid = data.replace("price_", "")
        context.user_data["action"] = "update_price"
        context.user_data["price_girl_id"] = gid
        girl = girls_dict[gid]
        await query.edit_message_text(
            f"*{girl['name']}* için yeni fiyatları gir:\n\nFormat: `sesli video`\nÖrnek: `60 120`",
            parse_mode="Markdown")

    # ── Admin: Çevrimiçi/Çevrimdışı ──
    elif data == "admin_online":
        if not is_admin(query.from_user.id): return
        buttons = []
        for g in girls:
            status = "🟢" if g["online"] else "🔴"
            buttons.append([InlineKeyboardButton(f"{status} {g['name']}", callback_data=f"toggle_online_{g['id']}")])
        buttons.append([InlineKeyboardButton("⬅️ Geri", callback_data="admin_back")])
        await query.edit_message_text("Durumunu değiştirmek istediğin bayanı seç:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("toggle_online_"):
        if not is_admin(query.from_user.id): return
        gid = data.replace("toggle_online_", "")
        for g in girls:
            if g["id"] == gid:
                g["online"] = not g["online"]
                status = "🟢 Çevrimiçi" if g["online"] else "🔴 Çevrimdışı"
                await query.edit_message_text(f"✅ *{g['name']}* artık {status}!",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_back")]]))
                break
        save_girls(girls)

    # ── Admin: Duyuru ──
    elif data == "admin_broadcast":
        if not is_admin(query.from_user.id): return
        context.user_data["action"] = "broadcast"
        await query.edit_message_text("📢 Tüm kullanıcılara göndermek istediğin mesajı yaz:")

    # ── Admin: Bakiye Ekle ──
    elif data == "admin_add_balance":
        if not is_admin(query.from_user.id): return
        context.user_data["action"] = "add_balance_id"
        await query.edit_message_text("💰 Bakiye eklemek istediğin kullanıcının *ID'sini* yaz:", parse_mode="Markdown")

    # ── Admin: Kullanıcılar ──
    elif data == "admin_users":
        if not is_admin(query.from_user.id): return
        users = load_users()
        text = f"👥 *Kullanıcı Listesi* ({len(users)} kişi)\n\n"
        for uid, u in list(users.items())[:20]:
            text += f"👤 {u.get('name','?')} | 💰 {u.get('balance',0)}₺ | `{uid}`\n"
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="admin_back")]]))

    # ── Admin: Geri ──
    elif data == "admin_back":
        if not is_admin(query.from_user.id): return
        users = load_users()
        await query.edit_message_text(
            f"🛠 *Admin Paneli*\n\n👥 Kullanıcı: *{len(users)}*\n👩 Bayan: *{len(girls)}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👩 Bayan Ekle", callback_data="admin_add_girl"),
                 InlineKeyboardButton("🗑 Bayan Sil", callback_data="admin_del_girl")],
                [InlineKeyboardButton("✏️ Fiyat Güncelle", callback_data="admin_price"),
                 InlineKeyboardButton("🟢 Çevrimiçi Yap", callback_data="admin_online")],
                [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
                [InlineKeyboardButton("💰 Bakiye Ekle", callback_data="admin_add_balance")],
                [InlineKeyboardButton("👥 Kullanıcı Listesi", callback_data="admin_users")],
            ]))

    # ── Ana Menü ──
    elif data == "main_menu":
        u = get_user(query.from_user.id)
        await query.edit_message_text(
            f"💘 *Ana Menü*\n\n💰 Bakiyen: *{u['balance']} ₺*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👩 Bayanları Gez 💫", callback_data="profile_0")],
                [InlineKeyboardButton("🔥 Çevrimiçi Bayanlar", callback_data="online_girls")],
                [InlineKeyboardButton("💰 Bakiyem", callback_data="my_balance")],
                [InlineKeyboardButton("ℹ️ Nasıl Çalışır?", callback_data="how_it_works")],
            ]))

# ── MESAJ HANDLER ─────────────────────────────────────────────────────────────
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    action = context.user_data.get("action")

    # ── Fiyat Güncelle ──
    if action == "update_price" and is_admin(user.id):
        try:
            parts = text.strip().split()
            voice, video = int(parts[0]), int(parts[1])
            gid = context.user_data.pop("price_girl_id")
            context.user_data.pop("action")
            girls = load_girls()
            for g in girls:
                if g["id"] == gid:
                    g["voice_price"] = voice
                    g["video_price"] = video
                    await update.message.reply_text(f"✅ *{g['name']}* fiyatı güncellendi!\n📞 {voice}₺ | 🎥 {video}₺", parse_mode="Markdown")
                    break
            save_girls(girls)
        except:
            await update.message.reply_text("❌ Hatalı format! Örnek: `60 120`", parse_mode="Markdown")
        return

    # ── Duyuru ──
    if action == "broadcast" and is_admin(user.id):
        context.user_data.pop("action")
        users = load_users()
        success = 0
        for uid in users:
            try:
                await context.bot.send_message(int(uid), f"📢 *Duyuru:*\n\n{text}", parse_mode="Markdown")
                success += 1
            except: pass
        await update.message.reply_text(f"✅ Duyuru *{success}/{len(users)}* kullanıcıya gönderildi!", parse_mode="Markdown")
        return

    # ── Bakiye ID ──
    if action == "add_balance_id" and is_admin(user.id):
        context.user_data["action"] = "add_balance_amount"
        context.user_data["balance_uid"] = text.strip()
        await update.message.reply_text(f"💰 Eklenecek miktarı yaz (₺):")
        return

    # ── Bakiye Miktar ──
    if action == "add_balance_amount" and is_admin(user.id):
        context.user_data.pop("action")
        uid = context.user_data.pop("balance_uid")
        try:
            amount = int(text.strip())
            u = get_user(int(uid))
            new_bal = u["balance"] + amount
            update_user(int(uid), {"balance": new_bal})
            await update.message.reply_text(f"✅ `{uid}` kullanıcısına *{amount}₺* eklendi!\nYeni bakiye: *{new_bal}₺*", parse_mode="Markdown")
            try:
                await context.bot.send_message(int(uid),
                    f"💰 *Hesabınıza {amount}₺ yüklendi!*\n\nYeni bakiyeniz: *{new_bal}₺*\n\nİyi eğlenceler! 🌸",
                    parse_mode="Markdown")
            except: pass
        except:
            await update.message.reply_text("❌ Hatalı miktar!")
        return

    # ── Bayan Ekleme Akışı ──
    if action == "add_girl_name" and is_admin(user.id):
        context.user_data["new_girl"]["name"] = text.strip()
        context.user_data["new_girl"]["id"] = text.strip().lower().replace(" ", "_")
        context.user_data["action"] = "add_girl_age"
        await update.message.reply_text("Adım 2/7: *Yaşını* yaz:", parse_mode="Markdown")
        return

    if action == "add_girl_age" and is_admin(user.id):
        try:
            context.user_data["new_girl"]["age"] = int(text.strip())
            context.user_data["action"] = "add_girl_city"
            await update.message.reply_text("Adım 3/7: *Şehrini* yaz:", parse_mode="Markdown")
        except:
            await update.message.reply_text("❌ Sadece sayı yaz! Örnek: 23")
        return

    if action == "add_girl_city" and is_admin(user.id):
        context.user_data["new_girl"]["city"] = text.strip()
        context.user_data["action"] = "add_girl_bio"
        await update.message.reply_text("Adım 4/7: Kısa *biyografisini* yaz:", parse_mode="Markdown")
        return

    if action == "add_girl_bio" and is_admin(user.id):
        context.user_data["new_girl"]["bio"] = text.strip()
        context.user_data["action"] = "add_girl_voice"
        await update.message.reply_text("Adım 5/7: *Sesli görüşme* fiyatını yaz (₺):", parse_mode="Markdown")
        return

    if action == "add_girl_voice" and is_admin(user.id):
        try:
            context.user_data["new_girl"]["voice_price"] = int(text.strip())
            context.user_data["action"] = "add_girl_video"
            await update.message.reply_text("Adım 6/7: *Görüntülü görüşme* fiyatını yaz (₺):", parse_mode="Markdown")
        except:
            await update.message.reply_text("❌ Sadece sayı yaz! Örnek: 50")
        return

    if action == "add_girl_video" and is_admin(user.id):
        try:
            context.user_data["new_girl"]["video_price"] = int(text.strip())
            context.user_data["action"] = "add_girl_photo"
            await update.message.reply_text(
                "Adım 7/7: *Fotoğraf* gönder (Telegram'dan fotoğraf yükle)\n\nYa da fotoğraf yoksa `yok` yaz.",
                parse_mode="Markdown")
        except:
            await update.message.reply_text("❌ Sadece sayı yaz! Örnek: 100")
        return

    if action == "add_girl_photo" and is_admin(user.id):
        # Fotoğraf text olarak "yok" geldiyse
        context.user_data["new_girl"]["photo"] = None
        context.user_data["new_girl"]["emoji"] = "👩"
        context.user_data["new_girl"]["online"] = True
        ng = context.user_data.pop("new_girl")
        context.user_data.pop("action")
        girls = load_girls()
        girls.append(ng)
        save_girls(girls)
        await update.message.reply_text(
            f"✅ *{ng['name']}* eklendi! (Fotoğrafsız)\n📞 {ng['voice_price']}₺ | 🎥 {ng['video_price']}₺\n\nFotoğraf eklemek için bayan profiline fotoğraf gönder.",
            parse_mode="Markdown")
        return

    # Normal kullanıcı
    await update.message.reply_text("Anlamadım 😊 /start yaz!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))

# ── FOTOĞRAF HANDLER ──────────────────────────────────────────────────────────
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    action = context.user_data.get("action")

    if action == "add_girl_photo" and is_admin(user.id):
        photo = update.message.photo[-1]
        file_id = photo.file_id
        context.user_data["new_girl"]["photo"] = file_id
        context.user_data["new_girl"]["emoji"] = "👩"
        context.user_data["new_girl"]["online"] = True
        ng = context.user_data.pop("new_girl")
        context.user_data.pop("action")
        girls = load_girls()
        girls.append(ng)
        save_girls(girls)
        await update.message.reply_text(
            f"✅ *{ng['name']}* fotoğrafıyla eklendi! 🎉\n📞 {ng['voice_price']}₺ | 🎥 {ng['video_price']}₺",
            parse_mode="Markdown")
    else:
        await update.message.reply_text("Anlamadım 😊 /start yaz!")

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("bakiye", lambda u, c: my_balance(u, c)))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("🤖 Bot çalışıyor!")
    app.run_polling(drop_pending_updates=True)

async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"💰 *Bakiye Bilgisi*\n\n💵 Bakiyen: *{u['balance']} ₺*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]]))

if __name__ == "__main__":
    main()
