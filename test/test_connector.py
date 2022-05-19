""" testing for ExchangeConnector """
from app.connector import ExchangeConnector, EmptySymbol
import pytest
import ccxt


def test_connector_exchange():
    """ Handle exchange not supported by ccxt """

    with pytest.raises(ccxt.ExchangeNotAvailable):
        ExchangeConnector('uniswap')  # exchange not supported


def test_connector_exchange2():
    """ Handle exchange typo  """

    with pytest.raises(ccxt.ExchangeNotAvailable):
        ExchangeConnector('biance')  # exchange typo


def test_symbol():
    """ test get symbol list """

    ex = ExchangeConnector('binance')
    assert ex.get_symbol_list() != None


def test_symbol_unsupported():
    """ test get symbol list from unsupported/typo quote"""

    ex = ExchangeConnector('binance')
    with pytest.raises(EmptySymbol):
        ex.get_symbol_list('aslas')


def test_single_ohlcv():
    """ test get single ohlcv data """

    ex = ExchangeConnector('binance')
    # 500 from max limit kline length
    # this set to 500 because api only allowed fetch 500 OHLCV history per call
    assert len(ex.get_ohlcv('BTC/USDT')) == 500


def test_single_ohlcv2():
    """ test symbol typo/unsupported on get_ohlcv """

    ex = ExchangeConnector('binance')
    with pytest.raises(Exception):
        ex.get_ohlcv('IDR/USDT')


def test_bulk_ohlcv():
    """ test get bulk ohlcv data """

    ex = ExchangeConnector('binance', 'future')
    symbol_list = ex.get_symbol_list(quote='BUSD')
    len_symbol = len(symbol_list)
    assert len(ex.data('4h', 'BUSD')) == len_symbol
