from datetime import date

_data_dma = '%d/%m/%Y'


def f_dma(data: date):
    return data.strftime(_data_dma)

