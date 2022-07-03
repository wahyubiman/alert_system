""" for handle background task """
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .connector import ExchangeConnector
from .strategy.indicator_alert import IndicatorAlert
from app.config import LOG
from app.notification import send_notif

scheduler = AsyncIOScheduler()


def scanner_1h():
    """ function to run signal and notify to user via telegram """
    LOG.info('Scanning signal from background task running')
    ohlcvs = ExchangeConnector(
        'binance', market_type='future').data('1h', '/USDT')
    calc = IndicatorAlert().calculate(ohlcvs)
    LOG.info('Done scanning')
    if len(calc[0]) != 0 | len(calc[1]) != 0:
        # send telegram notification if has signal
        asyncio.run(send_notif(calc))


def background_task():
    """ start a background task """
    LOG.info('Add job in scheduler')
    # scheduler.add_job(scanner_1h, 'cron', second='0-59/10')
    scheduler.add_job(scanner_1h, 'cron', hour='0-23')  # run every hour
    scheduler.start()  # start the scheduler
    asyncio.get_event_loop().run_forever()
    LOG.info('Success start scheduler')
