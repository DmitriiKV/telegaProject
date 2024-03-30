import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

reply_keyboard = [['/address', '/phone'], ['/site', '/work_time']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def echo(update, context):
    await update.message.reply_text(update.message.text)





async def close_keyboard(update, context):
    await update.message.reply_text(
        f'OK', reply_markup=ReplyKeyboardRemove
    )

async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"Hello {user.username}! Ia am Bot", reply_markup=markup
    )


async def help(update, context):
    await update.message.reply_text(
        'Ladna, ia umet pomogat. Ia bot-spravochnik. A bez komand ia prosto povtoriaiu your messages')


async def address(update, context):
    await update.message.reply_text('Kamen ia dam. Adress ia ne dam')


async def phone(update, context):
    await update.message.reply_text('84323425442134')


async def site(update, context):
    await update.message.reply_text('https://github.com/DmitriiKV/telegaProject')


async def work_time(update, context):
    await update.message.reply_text('Vremia raboti: s 5:00 do 5:01')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("address", address))
    application.add_handler(CommandHandler("phone", phone))
    application.add_handler(CommandHandler("site", site))
    application.add_handler(CommandHandler("work_time", work_time))
    application.add_handler(CommandHandler("close", close_keyboard))
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
