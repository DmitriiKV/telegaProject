import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import aiohttp

TIMER = 5

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

reply_keyboard = [['/address', '/phone'], ['/site', '/work_time'], ['/set_timer', '/unset']]
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


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule.removal()
    return True


async def set_timer(update, context):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    text = f'Ia vernutcia cherez {TIMER} secunda'
    if job_removed:
        text += ' Stariy zadacha udalen'
    await update.effective_message.reply_text(text)


async def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Taimer otmena!' if job_removed else 'Aktivnaia zadacha netu'
    await update.message.reply_text(text)


async def task(context):
    await context.bot.send_message(context.job.chat_id, f'{TIMER} secund proshel')


async def dialog(update, context):
    await update.message.reply_text(
        """Kakoj-to opros
dlja prerivanija vvedi commandu /stop
Vopros 1: Skolko vam let?
        """
    )
    return 1


async def first_response(update, context):
    context.user_data['local'] = update.message.text
    await update.message.reply_text(
        f"""
Ja ochen rad, chto vam {context.user_data['local']} let
kogda your den rojdenija?
        """
    )
    return 2


async def second_response(update, context):
    context.user_data['data'] = update.message.text
    await update.message.reply_text(
        f"""
        Ura, {context.user_data['data']} - eto moj lubimij den!!!!!
I mne tozhe, kak i vam, {context.user_data['local']} let!!!!!
Do svidanja
Bolshe oprosa ne budet
        """
    )
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text('Vot i pogovorili. Nu i ja togda pojdu')
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('dialog', dialog)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)


def get_ll_spn(toponym):
    if not toponym:
        return (None, None)
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ",".join([toponym_longitude, toponym_lattitude])
    envelope = toponym["boundedBy"]["Envelope"]
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0
    spn = f"{dx},{dy}"
    return ll, spn


async def get_response(geocoder_url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(geocoder_url, params=params) as response:
            return await response.json()


async def geocoder_map(update, context):
    geocoder_url = 'http://geocode-maps.yandex.ru/1.x/'
    response = await get_response(geocoder_url, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": update.message.text
    })
    toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    ll, spn = get_ll_spn(toponym)
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}8&spn={spn}&l=map"
    await context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="Vot ono v vide karty"
    )

async def geocoder_sat(update, context):
    geocoder_url = 'http://geocode-maps.yandex.ru/1.x/'
    response = await get_response(geocoder_url, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": update.message.text
    })
    toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    ll, spn = get_ll_spn(toponym)
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}8&spn={spn}&l=sat"
    await context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="Vot ono v vide sputnika"
    )

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
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("geomap", geocoder_map))
    application.add_handler(CommandHandler("geosat", geocoder_sat))
    application.add_handler(conv_handler)
    # application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
