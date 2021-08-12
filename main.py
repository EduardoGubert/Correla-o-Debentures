import datetime

import wget
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt


def get_filename(t):
    """
        - t     : datetime.date
        returno : String com o nome do arquivo da AMBIMA
    """
    return '%s.txt' % t.strftime("%y%m%d")

def download(t):
    """
      Faz download dos txts
    """

    url_ms = 'https://www.anbima.com.br/informacoes/merc-sec/arqs/'
    url_db= 'https://www.anbima.com.br/informacoes/merc-sec-debentures/arqs/'

    time.sleep(2)
    response1 = requests.get(url_ms + "ms" + get_filename(t))
    print(t, 'response', response1.status_code)

    if response1.status_code == 200:
        with open("ms" + get_filename(t), 'wb') as fp:
            fp.write(response1.content)


    time.sleep(2)
    response2 = requests.get(url_db + "db" + get_filename(t))
    print(t, 'response', response2.status_code)

    if response2.status_code == 200:
        with open("db" + get_filename(t), 'wb') as fp:
            fp.write(response2.content)

    return response1.status_code, response2.status_code


def df_ntnb(t):

    date_cols = ['Data Referencia', 'Data Base/Emissao', 'Data Vencimento']
    arquivo = "ms" + get_filename(t)
    df = pd.read_csv(arquivo, encoding='iso 8859-1', engine='python', sep='@', skiprows=2, decimal=',',
                     parse_dates=date_cols)
    ntn_b = df[df['Titulo'] == 'NTN-B'][['Data Vencimento', 'Tx. Indicativas']]
    ntn_b = ntn_b.set_index('Data Vencimento')

    return ntn_b

def df_db(t):
    arquivo = "db" + get_filename(t)
    with open(arquivo) as db:
        txt = db.read()
        new_db = txt.replace('Repac./  Venc.', 'Data Vencimento')

    with open(arquivo, 'w') as db:
        db.write(new_db)
    date_cols = ['Data Vencimento', 'Referência NTN-B']

    df_debenture = pd.read_csv(arquivo, encoding='iso 8859-1', engine='python', sep='@', skiprows=2, decimal=',',
                       parse_dates=date_cols)

    return df_debenture

def escolhe_debenture(t):
    DB = df_db(t)
    debenture = input("Código debenture: ")
    DB = df_db(t)
    DB = DB[DB['Código'] == debenture][['Data Vencimento', 'Taxa Indicativa']]
    DB = DB.set_index('Data Vencimento')
    return DB

def interpola_df(t):
    DB = escolhe_debenture(t)

    ntnb = df_ntnb(t)


    df_concat = pd.concat([ntnb, DB])


    df_ordenado = df_concat.sort_values(by='Data Vencimento')


    df_interpolado = df_ordenado.interpolate()
    ntnb_interpolada = df_interpolado[['Tx. Indicativas']]


    return ntnb_interpolada

def plota_grafico(t):
    DB = escolhe_debenture(t)
    NTN_B = interpola_df(t)

    plt.plot(DB, 'ro')
    plt.plot(NTN_B, 'go')
    plt.plot(NTN_B)
    plt.ylabel('Tx. Indicativas')
    plt.xlabel('Data Vencimento')
    plt.show()


t = datetime.datetime.now()
if t.weekday() == 6 or t.weekday() == 0:
    if t.weekday() == 0:
        t = t - datetime.timedelta(days=3)

    else:
        t = t - datetime.timedelta(days=2)

else:
    t = t - datetime.timedelta(days=1)

resultado = download(t)
print(resultado)

#df_ntnb(t) funciona - 1
#df_db(t) funciona - 2
#escolhe_debenture(t) - 3
#interpola_df(t) - 4

plota_grafico(t)