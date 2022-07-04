""" Telegram Notification """
import asyncio
import time
import os
import pandas as pd
from app.config import LOG
from app.config import TG_CHANNEL_NAME
from telethon import TelegramClient


async def send_notif(signals):
    """ Function to send notification via telegram Bot

    Params:
        signals(list): List of signal generated with format ['pairName - $lasPrice - rsi - LONG/SHORT', etc...]
    Return:
        None  """
    LOG.info('Send notification via Telegram Bot')
    msg_header = """----- Market Structure Break Alert 1H -----

"""
    msg = """"""
    bot = TelegramClient('notify_bot', os.getenv(
        'TELE_API_ID'), os.getenv('TELE_API_HASH'))
    await bot.start(bot_token=os.getenv('TELE_BOT_TOKEN'))
    entity = await bot.get_entity(TG_CHANNEL_NAME)
    msg += msg_header
    if len(signals[0]) != 0:
        msg += f"""MSB High Break :
"""
        for signal in signals[0]:
            msg += "-> {} \n".format(signal)
    if len(signals[1]) != 0:
        msg += f"""MSB Low Break :
"""
        for signal in signals[1]:
            msg += "-> {} \n".format(signal)
    msg += f"""
>>> {str(pd.to_datetime(time.time(), unit='s').tz_localize('UTC').tz_convert('Asia/Jakarta').strftime('%m/%d/%Y %H:%M:%S'))}"""
    await bot.send_message(entity, msg)
    LOG.info('Success send notification via Telegram Bot')
