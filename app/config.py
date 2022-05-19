'''
Config file for ccxt
'''

import logging

PROD = False
LOG = logging.getLogger('alert')
# telegram channel name to send signal
TG_CHANNEL_NAME = 'https://t.me/kokangyuhu'  # use invite link
RSI = 14
EMA_FAST = 34
EMA_SLOW = 168
