""" connector for exchange """
import ccxt
import requests
import asyncio
import time
import pandas as pd
import numpy as np
from .config import *


class ExchangeConnector:
    """ Exchange connector """

    def __init__(self, exchange, market_type='spot'):
        """ Constructor for IndicatorAlert

        Params:
            exchange(str): ccxt supported exchange
            market_type(str): type spot or futures that exchange supported on CCXT, default 'spot' 
        Returns:
            () """

        if exchange in ccxt.exchanges:
            self.exchange = getattr(ccxt, exchange)(
                {'options':
                 {'defaultType': market_type}
                 }
            )
        else:
            LOG.error(f'Exchanges {exchange} not supported')
            raise ccxt.ExchangeNotAvailable(
                f'{exchange} exchange not supported by CCXT')

    def get_symbol_list(self, quote='USDT'):
        """ Get supported symbol on exchange defined in constructor

        Params:
            quote(str): quote symbol to fetch, default 'USDT'
        Returns:
            (List): list of symbol """

        try:
            if '/' not in quote:
                quote = '/' + quote
            elif '/' in quote:
                quote = quote
            LOG.info(f'Fetch symbol list')
            self.exchange.load_markets()
            result = [symbol
                      for symbol in self.exchange.symbols if quote in symbol]
            if len(result) == 0:
                raise EmptySymbol
            return result
        except EmptySymbol:
            LOG.error('Symbol list empty')
            raise EmptySymbol
        except Exception as e:
            LOG.error(e)
            raise Exception

    async def _get_ohlcv(self, symbol, timeframe='1h', **kwargs):
        """ For async fetch single pair of OHLCV data then convert it to pandas dataframe format

        Params:
            symbol(str): symbol name to fetch
            timeframe(str): timeframe for fetch OHLCV, default '1h'
            **kwargs
        Returns:
            (DataFrame): pandas dataframe format """

        try:
            if PROD == False:
                LOG.info(f'Fetch OHLCV for {symbol}')
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, timeframe, **kwargs)
            df = pd.DataFrame(
                ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df.fillna(0)
            df.name = symbol
            return df
        except ccxt.BadSymbol as e:
            LOG.exception(e)
            raise ccxt.BadSymbol(f'{symbol} not supported')
        except ccxt.NetworkError as e:
            LOG.exception(e)
            raise ccxt.NetworkError(f'Please check your network connection')
        except requests.exceptions.SSLError:
            LOG.exception('SSL error')
            raise requests.exceptions.SSLError(
                'SSL Error, please check your network properly')
        except Exception as e:
            LOG.exception(e)

    def get_ohlcv(self, symbol, **kwargs):
        """ For fetch single pair of OHLCV then retun pandas dataframe format

        Params:
            symbol(str): symbol name to fetch
            **kwargs
        Returns:
            (DataFrame): pandas dataframe format """

        result = asyncio.run(self._get_ohlcv(symbol, **kwargs))
        return result

    async def _get_data(self, timeframe, quote):
        """ For bulk fecth OHLCV data in async

        Params:
            timeframe(str): timeframe to fetch OHLCV data
            quote(str): quote symbol to fetch
        Returns:
            result """

        LOG.info(
            f'Bulk fetch OHLCV from {self.exchange} {self.exchange.options["defaultType"]} market')
        symbol_list = self.get_symbol_list(quote=quote)
        task = [asyncio.create_task(self._get_ohlcv(symbol, timeframe=timeframe))
                for symbol in symbol_list]
        result = asyncio.gather(*task)
        return result

    def data(self, timeframe, quote):
        """ Bulk OHLCV pandas dataframe data for all symbol returned from get_symbol_list

        Params:
            timeframe(str): timeframe to fetch OHLCV data
            quote(str): quote symbol to fetch
        Return:
            result(List): list of pandas dataframe ohlcv """

        start = time.time()
        result = asyncio.run(self._get_data(timeframe, quote)).result()
        return result


# -------------- Exception -----------------
class ExchangeConnectorException(Exception):
    pass


class EmptySymbol(ExchangeConnectorException):
    def __init__(self):
        super().__init__('return symbol must not be empty, please  check the quote, maybe typo or unsupported quote currency')
