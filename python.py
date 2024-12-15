import pyotp
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# Aktifkan logging untuk debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Gantilah dengan token bot Anda yang didapat dari BotFather
TELEGRAM_TOKEN = '7529177610:AAHVekNvZ1hGujgLcZJaaIeopeg-M1K7o00'

# ID pengguna admin yang akan menerima OTP
ADMIN_ID = '6666806820'  # Ganti dengan ID admin Anda

# Membuat dictionary untuk menyimpan nomor dan OTP sementara
otp_data = {}

# Fungsi untuk memulai bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Selamat datang! Kirimkan nomor telepon Anda untuk menerima OTP.'
    )

# Fungsi untuk menangani input nomor telepon
def handle_phone_number(update: Update, context: CallbackContext) -> None:
    phone_number = update.message.text.strip()

    # Validasi nomor telepon (misal hanya menerima angka dengan panjang 10 atau lebih)
    if not phone_number.isdigit() or len(phone_number) < 10:
        update.message.reply_text("Nomor telepon tidak valid. Harap masukkan nomor yang benar.")
        return

    # Membuat secret key berdasarkan nomor telepon
    totp = pyotp.TOTP(pyotp.random_base32())
    
    # Simpan nomor telepon dan OTP yang dihasilkan
    otp_code = totp.now()
    otp_data[phone_number] = otp_code
    
    # Mengirimkan OTP ke penginput (admin) dan nomor yang dimasukkan
    update.message.reply_text(f"OTP untuk nomor {phone_number} adalah: {otp_code}")
    
    # Kirimkan OTP ke admin (penginput)
    context.bot.send_message(ADMIN_ID, f"OTP untuk nomor {phone_number} adalah: {otp_code}")
    
    # Mengirimkan pesan kepada nomor telepon yang diberikan (harus dilakukan manual melalui API lain)
    # NOTE: Telegram API tidak memungkinkan pengiriman langsung ke nomor telepon biasa.
    update.message.reply_text(f"OTP telah dikirimkan ke nomor {phone_number}.")
    
    # Log OTP yang dikirim
    logger.info(f"OTP untuk {phone_number} dikirimkan: {otp_code}")

# Fungsi untuk memverifikasi OTP
def verify_otp(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.strip()
    
    # Memeriksa apakah input adalah OTP yang valid
    phone_number = context.user_data.get('phone_number')
    if not phone_number or phone_number not in otp_data:
        update.message.reply_text("No phone number registered. Please input your phone number first.")
        return
    
    # Periksa OTP yang dimasukkan pengguna
    if user_input == otp_data[phone_number]:
        update.message.reply_text(f"OTP berhasil diverifikasi untuk {phone_number}.")
        del otp_data[phone_number]  # Menghapus OTP yang sudah diverifikasi
    else:
        update.message.reply_text("OTP tidak valid. Silakan coba lagi.")

# Fungsi utama untuk menjalankan bot
def main() -> None:
    # Membuat Updater dan memberikan token
    updater = Updater(TELEGRAM_TOKEN)

    # Mendapatkan dispatcher untuk menambahkan handler
    dispatcher = updater.dispatcher

    # Menambahkan handler untuk command /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Menambahkan handler untuk menerima nomor telepon
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_phone_number))

    # Menambahkan handler untuk memverifikasi OTP
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^\d{6,8}$'), verify_otp))

    # Memulai bot
    updater.start_polling()

    # Menunggu hingga bot berhenti
    updater.idle()

if __name__ == '__main__':
    main()