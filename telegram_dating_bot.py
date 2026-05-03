"""
💘 Telegram Tanışma Botu
Kullanıcılar bayan profillerini görür, sesli/görüntülü görüşme satın alabilir.
"""

import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import os

# ── Loglama ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── BOT TOKEN ─────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "BURAYA_BOT_TOKEN_YAZ")

# ── Bayan Profilleri ──────────────────────────────────────────────────────────
GIRLS = [
    {
        "id": "elif",
        "name": "Elif",
        "age": 24,
        "city": "İstanbul",
        "bio": "Müzik seven, neşeli ve sıcakkanlı biriyim. 🎵",
        "emoji": "👩‍🦰",
        "photo": None,          # Gerçek foto URL'si eklenebilir
        "voice_price": 50,
        "video_price": 100,
        "online": True,
    },
    {
        "id": "ayse",
        "name": "Ayşe",
        "age": 22,
        "city": "Ankara",
        "bio": "Kitap kurdu, kahve bağımlısı. ☕📚",
        "emoji": "👩‍🦱",
        "photo": None,
        "voice_price": 60,
        "video_price": 120,
        "online": True,
    },
    {
        "id": "merve",
        "name": "Merve",
        "age": 26,
        "city": "İzmir",
        "bio": "Dans etmeyi, gezmek ve eğlenmeyi seviyorum. 💃",
        "emoji": "👱‍♀️",
        "photo": None,
        "voice_price": 75,
        "video_price": 150,
        "online": False,
    },
    {
        "id": "zeynep",
        "name": "Zeynep",
        "age": 23,
        "city": "Bursa",
        "bio": "Doğa yürüyüşleri ve fotoğrafçılık tutkum. 🏞️📸",
        "emoji": "👩‍🦳",
        "photo": None,
        "voice_price": 50,
        "video_price": 90,
        "online": True,
    },
    {
        "id": "selin",
        "name": "Selin",
        "age": 25,
        "city": "Antalya",
        "bio": "Denizi, güneşi ve iyi sohbeti çok severim. 🌊☀️",
        "emoji": "👩",
        "photo": None,
        "voice_price": 80,
        "video_price": 160,
        "online": True,
    },
    {
        "id": "dilan",
        "name": "Dilan",
        "age": 21,
        "city": "Gaziantep",
        "bio": "Yemek yapmayı ve yeni insanlarla tanışmayı seviyorum. 🍽️",
        "emoji": "👩‍🍳",
        "photo": None,
        "voice_price": 45,
        "video_price": 85,
        "online": True,
    },
]

# Kolay erişim için dict
GIRLS_DICT = {g["id"]: g for g in GIRLS}

# ── Yardımcı Fonksiyonlar ─────────────────────────────────────────────────────
def girl_card(girl: dict) -> str:
    """Bayan profil kartını formatlar."""
    status = "🟢 Çevrimiçi" if girl["online"] else "🔴 Çevrimdışı"
    return (
        f"{girl['emoji']} *{girl['name']}* | {girl['age']} yaş | {girl['city']}\n"
        f"_{girl['bio']}_\n\n"
        f"📞 Sesli Görüşme: *{girl['voice_price']} ₺*\n"
        f"🎥 Görüntülü Görüşme: *{girl['video_price']} ₺*\n"
        f"{status}"
    )

def girl_keyboard(girl: dict, index: int, total: int) -> InlineKeyboardMarkup:
    """Profil altındaki butonları oluşturur."""
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Önceki", callback_data=f"profile_{index-1}"))
    if index < total - 1:
        nav_row.append(InlineKeyboardButton("Sonraki ➡️", callback_data=f"profile_{index+1}"))

    action_row = [
        InlineKeyboardButton(
            f"📞 Sesli ({girl['voice_price']}₺)",
            callback_data=f"voice_{girl['id']}"
        ),
        InlineKeyboardButton(
            f"🎥 Görüntülü ({girl['video_price']}₺)",
            callback_data=f"video_{girl['id']}"
        ),
    ]

    keyboard = []
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append(action_row)
    keyboard.append([InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

# ── Komutlar ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot'u başlatır."""
    user = update.effective_user
    welcome = (
        f"💘 *Merhaba {user.first_name}!*\n\n"
        "Tanışma Botu'na hoş geldin! 🌸\n\n"
        "Burada dilediğin bayanla *sesli* veya *görüntülü* görüşme yapabilirsin.\n\n"
        "👇 Aşağıdan bir seçenek seç:"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👩 Bayanları Gör 💫", callback_data="profile_0")],
        [InlineKeyboardButton("🔥 Çevrimiçi Bayanlar", callback_data="online_girls")],
        [InlineKeyboardButton("ℹ️ Nasıl Çalışır?", callback_data="how_it_works")],
    ])
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=keyboard)


async def show_girls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm bayanları listeler."""
    msg = "👩 *Tüm Bayanlarımız:*\n\n"
    for g in GIRLS:
        status = "🟢" if g["online"] else "🔴"
        msg += f"{status} {g['emoji']} *{g['name']}* — {g['age']} yaş, {g['city']}\n"
        msg += f"   📞 {g['voice_price']}₺  |  🎥 {g['video_price']}₺\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👁️ Profilleri Gez", callback_data="profile_0")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")],
    ])
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)


# ── Callback Handler ──────────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── Profil Göster ──
    if data.startswith("profile_"):
        index = int(data.split("_")[1])
        girl = GIRLS[index]
        text = girl_card(girl)
        kb = girl_keyboard(girl, index, len(GIRLS))
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    # ── Sesli Görüşme ──
    elif data.startswith("voice_"):
        girl_id = data.split("_")[1]
        girl = GIRLS_DICT[girl_id]
        if not girl["online"]:
            await query.edit_message_text(
                f"😔 *{girl['name']}* şu an çevrimdışı.\nDaha sonra tekrar dene!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Geri Dön", callback_data=f"profile_{GIRLS.index(girl)}")]
                ])
            )
            return

        text = (
            f"📞 *{girl['name']}* ile Sesli Görüşme\n\n"
            f"💰 Ücret: *{girl['voice_price']} ₺*\n\n"
            f"Ödemeyi tamamlamak için aşağıdaki butona bas:"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 {girl['voice_price']}₺ Öde & Bağlan", callback_data=f"pay_voice_{girl_id}")],
            [InlineKeyboardButton("⬅️ Geri Dön", callback_data=f"profile_{GIRLS.index(girl)}")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # ── Görüntülü Görüşme ──
    elif data.startswith("video_"):
        girl_id = data.split("_")[1]
        girl = GIRLS_DICT[girl_id]
        if not girl["online"]:
            await query.edit_message_text(
                f"😔 *{girl['name']}* şu an çevrimdışı.\nDaha sonra tekrar dene!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Geri Dön", callback_data=f"profile_{GIRLS.index(girl)}")]
                ])
            )
            return

        text = (
            f"🎥 *{girl['name']}* ile Görüntülü Görüşme\n\n"
            f"💰 Ücret: *{girl['video_price']} ₺*\n\n"
            f"Ödemeyi tamamlamak için aşağıdaki butona bas:"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 {girl['video_price']}₺ Öde & Bağlan", callback_data=f"pay_video_{girl_id}")],
            [InlineKeyboardButton("⬅️ Geri Dön", callback_data=f"profile_{GIRLS.index(girl)}")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # ── Ödeme (Demo) ──
    elif data.startswith("pay_voice_"):
        girl_id = data.replace("pay_voice_", "")
        girl = GIRLS_DICT[girl_id]
        text = (
            f"✅ *Ödeme Alındı!*\n\n"
            f"📞 *{girl['name']}* ile sesli görüşme başlıyor...\n\n"
            f"🔗 Görüşme Linki: `https://call.example.com/{girl_id}/voice`\n\n"
            f"⚠️ Bu demo bir bot, gerçek ödeme entegrasyonu (Stripe, Papara vb.) eklenebilir."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")],
            [InlineKeyboardButton("👩 Diğer Bayanlara Bak", callback_data="profile_0")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    elif data.startswith("pay_video_"):
        girl_id = data.replace("pay_video_", "")
        girl = GIRLS_DICT[girl_id]
        text = (
            f"✅ *Ödeme Alındı!*\n\n"
            f"🎥 *{girl['name']}* ile görüntülü görüşme başlıyor...\n\n"
            f"🔗 Görüşme Linki: `https://call.example.com/{girl_id}/video`\n\n"
            f"⚠️ Bu demo bir bot, gerçek ödeme entegrasyonu (Stripe, Papara vb.) eklenebilir."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")],
            [InlineKeyboardButton("👩 Diğer Bayanlara Bak", callback_data="profile_0")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # ── Çevrimiçi Bayanlar ──
    elif data == "online_girls":
        online = [g for g in GIRLS if g["online"]]
        text = "🟢 *Şu An Çevrimiçi Bayanlar:*\n\n"
        for g in online:
            text += f"{g['emoji']} *{g['name']}* — {g['age']} yaş, {g['city']}\n"
            text += f"   📞 {g['voice_price']}₺  |  🎥 {g['video_price']}₺\n\n"

        buttons = [[InlineKeyboardButton(
            f"{g['emoji']} {g['name']}", callback_data=f"profile_{GIRLS.index(g)}"
        )] for g in online]
        buttons.append([InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")])
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ── Nasıl Çalışır ──
    elif data == "how_it_works":
        text = (
            "ℹ️ *Nasıl Çalışır?*\n\n"
            "1️⃣ *Bayan Seç* — Profilleri gez, beğendiğini seç\n"
            "2️⃣ *Görüşme Türü Seç* — Sesli (📞) veya Görüntülü (🎥)\n"
            "3️⃣ *Ödeme Yap* — Güvenli ödeme ile ücreti öde\n"
            "4️⃣ *Bağlan!* — Anında görüşme linkine eriş\n\n"
            "💳 *Desteklenen Ödemeler:* Kredi Kartı, Papara, Kripto\n"
            "🔒 *Gizlilik:* Tüm görüşmeler şifreli ve gizlidir.\n"
            "⏰ *Destek:* 7/24 canlı destek mevcut."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👩 Bayanları Gör", callback_data="profile_0")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # ── Ana Menü ──
    elif data == "main_menu":
        user = update.effective_user
        welcome = (
            f"💘 *Ana Menü*\n\n"
            f"Merhaba {user.first_name}! Ne yapmak istersin?"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👩 Bayanları Gez 💫", callback_data="profile_0")],
            [InlineKeyboardButton("🔥 Çevrimiçi Bayanlar", callback_data="online_girls")],
            [InlineKeyboardButton("ℹ️ Nasıl Çalışır?", callback_data="how_it_works")],
        ])
        await query.edit_message_text(welcome, parse_mode="Markdown", reply_markup=keyboard)


# ── Bilinmeyen Mesajlar ───────────────────────────────────────────────────────
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Ana Menüye Dön", callback_data="main_menu")]
    ])
    await update.message.reply_text(
        "Anlamadım 😊 /start yazarak başlayabilirsin!",
        reply_markup=keyboard
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if BOT_TOKEN == "BURAYA_BOT_TOKEN_YAZ":
        print("❌ Lütfen BOT_TOKEN değişkenini ayarla!")
        print("   export TELEGRAM_BOT_TOKEN='your-token-here'")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bayanlar", show_girls))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("🤖 Bot başlatıldı! Ctrl+C ile durdur.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
