import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def echo(update, context):
    await update.message.reply_text(f"Я получил сообщение {update.message.text}")


async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"Hello {user.username}! I am Bot")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
