import time
from iqoptionapi.stable_api import IQ_Option
import configparser
import telebot
from pathlib import Path
from datetime import datetime


class Bot():
    def __init__(self) -> None:
        pass

    def arquivo(self, documento):
        filename = f"{documento}"
        fileObj = Path(filename)

        if fileObj.is_file():
            file = configparser.ConfigParser()
            file.read(documento)
            dicionario = {'email': file.get('DADOS', 'email'), 'senha': file.get('DADOS', 'senha'),
                          'stop_win': file.get('OPERACOES', 'stop_win'), 'stop_loss': file.get('OPERACOES', 'stop_loss'),
                          'gale': file.get('OPERACOES', 'gale'), 'timeframe': file.get('OPERACOES', 'timeframe'),
                          'telegram': file.get('TELEGRAM', 'ativar'), 'token': file.get('TELEGRAM', 'token'),
                          'noticias': file.get('INDICADORES', 'noticias'), 'tendencia': file.get('INDICADORES', 'tendencia'),
                          'ativo': file.get('OPERACOES', 'ativo')}
            dicionario['ativo'] = dicionario['ativo'].split(',')
            return dicionario
        else:
            file = open(documento, 'w+')
            arquivo = """
[DADOS]
email = seu@email.com
senha = sua senha

[OPERACOES]
stop_win = 10.00
stop_loss = 5.00
gale = 2

[TELEGRAM]
ativar = sim
token = https://help.huggy.io/telegram-bot/como-configurar-o-telegram-bot

[INDICADORES]
noticias = sim
tendencia = sim
"""
            file.write(arquivo)
            file.close()
            return False

    def conectar(self, email, senha):
        self.iq_bot = IQ_Option(email, senha)
        if self.iq_bot.connect():
            print(f"Conectado...\n")
            return True
        else:
            return False

    def check_arquivo(self, arquivo):
        if len(arquivo) == 11:
            validade = True
            for k, v in arquivo.items():
                if v:
                    pass
                else:
                    print(
                        f"O Campo '{k}' esta sem informacao, corrija e tente novamente...")
                    validade = False
            return validade
        else:
            print(f"Campos faltantes, exclua o arquivo dados.txt e tente novamente...")
            return False

    def enviar_notificacao(self, mensagem, chave):
        CHAVE_API = chave
        bot = telebot.AsyncTeleBot(CHAVE_API)
        bot.send_message(mensagem)

    def lista_candle(self, ativo, timeframe):
        ativo, timeframe = ativo.upper(), int(timeframe) * 60
        self.iq_bot.start_candles_stream(ativo, timeframe, 5)
        candles = self.iq_bot.get_realtime_candles(ativo, timeframe)
        self.iq_bot.stop_candles_stream(ativo, timeframe)
        candles = dict(candles)
        count = 5
        lista = {}
        for k, v in candles.items():
            print(v)
            lista.update({count: v})
            count -= 1
        return lista

    def lista_ativos_online(self, check):
        ativos = self.iq_bot.get_all_open_time()
        if ativos['digital'][check]['open']:
            print(f"{check} esta ativo na digital")
            return True, 'digital'
        elif ativos['turbo'][check]['open']:
            print(f"{check} esta ativo na binaria")
            return True, 'turbo'
        else:
            print(f"{check} esta inativo")
            return False

    def lista_profit(self, ativo, modo, profit_min, timeframe):
        timeframe = int(timeframe)
        if modo == 'turbo':
            profit = self.iq_bot.get_all_profit()
            if float(profit) > float(profit_min):
                return True
            else:
                return False

        elif modo == 'digital':
            self.iq_bot.subscribe_strike_list(ativo, timeframe)
            while True:
                profit = self.iq_bot.get_digital_current_profit(
                    ativo, timeframe)
                time.sleep(1)
                if profit:
                    break
            self.iq_bot.unsubscribe_strike_list(ativo, timeframe)
            if float(profit) > float(profit_min):
                return True
            else:
                return False

    def compra_binary(self, valor, ativo, tempo):
        tempo = int(tempo)
        check, id = self.iq_bot.buy(valor, ativo, 'call', tempo)
        if check:
            print(
                f"Comprado em {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}, expiracao em {tempo} minutos")
        else:
            print(
                f"Falha na entrada de compra do {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

    def venda_binary(self, valor, ativo, tempo):
        tempo = int(tempo)
        check, id = self.iq_bot.buy(valor, ativo, 'put', tempo)
        if check:
            print(
                f"Vendido em {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}, expiracao em {tempo} minutos")
            return id
        else:
            print(
                f"Falha na entrada de venda do {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            return False

    def compra_digital(self, valor, ativo, tempo):
        tempo = int(tempo)
        check, id = self.iq_bot.buy_digital_spot(ativo, valor, 'call', tempo)
        if check:
            print(
                f"Comprado em {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}, expiracao em {tempo} minutos")
            return id
        else:
            print(
                f"Falha na entrada de compra do {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            return False

    def venda_digital(self, valor, ativo, tempo):
        tempo = int(tempo)
        check, id = self.iq_bot.buy_digital_spot(ativo, valor, 'put', tempo)
        if check:
            print(
                f"Vendido em {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}, expiracao em {tempo} minutos")
            return id
        else:
            print(
                f"Falha na entrada de venda do {ativo} as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            return False

    def check_win(self, id, modo, entrada):
        if modo == 'digital':
            check, win = self.iq_bot.check_win_digital_v2(id)
            if check:
                if win < 0:
                    print(f"Loss -R$ {entrada}")
                    return True
                else:
                    print(f"Win +R$ {win}")
                    return True
            else:
                return False
        elif modo == 'turbo':
            check, win = self.iq_bot.check_win_v3(id)
            if check:
                if win < 0:
                    print(f"Loss -R$ {entrada}")
                    check = False
                    return True
                else:
                    print(f"Win +R$ {win}")
                    check = False
                    return True
            else:
                return False

    def padrao_engolfo(self, lista):
        print(lista[2])
        if lista[2]['open'] > lista[2]['close'] and lista[3]['open'] < lista[3]['close'] and lista[4]['open'] < lista[4]['close']:
            if abs(lista[2]['open'] - lista[2]['close']) < abs(lista[3]['open'] - lista[3]['close']):
                if lista[1]['close'] > lista[2]['close']:
                    return 'put'

        elif lista[2]['open'] < lista[2]['close'] and lista[3]['open'] > lista[3]['close'] and lista[4]['open'] > lista[4]['close']:
            if abs(lista[2]['open'] - lista[2]['close']) < abs(lista[3]['open'] - lista[3]['close']):
                if lista[1]['close'] > lista[2]['close']:
                    return 'call'
        else:
            return False


if __name__ == "__main__":
    bot = Bot()
    b = bot.arquivo('dados.txt')
    if b and bot.check_arquivo(b) and bot.conectar(b['email'], b['senha']):
        entradas = {}
        while True:
            for ativo in b['ativo']:
                check, modo = bot.lista_ativos_online(ativo)
                profit = bot.lista_profit(ativo, modo, 90, b['timeframe'])
                if profit:
                    if check:
                        engolfe = bot.padrao_engolfo(
                            bot.lista_candle(ativo, b['timeframe']))
                        if engolfe:
                            if ativo not in entradas:
                                if engolfe == 'call':
                                    if modo == 'digital':
                                        s = bot.compra_digital(
                                            2, ativo, b['timeframe'])
                                        entradas.update({ativo: s})
                                    elif modo == 'turbo':
                                        s = bot.compra_binary(
                                            2, ativo, b['timeframe'])
                                        entradas.update({ativo: s})
                                elif engolfe == 'put':
                                    if modo == 'digital':
                                        s = bot.venda_digital(
                                            2, ativo, b['timeframe'])
                                        entradas.update({ativo: s})
                                    elif modo == 'turbo':
                                        s = bot.venda_binary(
                                            2, ativo, b['timeframe'])
                                        entradas.update({ativo: s})
                            else:
                                if bot.check_win(entradas['ativo'], modo, 2):
                                    del entradas[ativo]
                        else:
                            print('Buscando')
