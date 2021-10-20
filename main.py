from time import process_time, time
from iqoptionapi.stable_api import IQ_Option
import configparser
import telebot
from pathlib import Path


class Bot():
    def __init__(self) -> None:
        pass

    def arquivo(self, documento):
        filename = f"{documento}"
        fileObj = Path(filename)

        if fileObj.is_file():
            file = configparser.ConfigParser()
            file.read(documento)
            return {'email': file.get('DADOS', 'email'), 'senha': file.get('DADOS', 'senha'),
                    'stop_win': file.get('OPERACOES', 'stop_win'), 'stop_loss': file.get('OPERACOES', 'stop_loss'),
                    'gale': file.get('OPERACOES', 'gale'), 'timeframe': file.get('OPERACOES', 'timeframe'),
                    'telegram': file.get('TELEGRAM', 'ativar'), 'token': file.get('TELEGRAM', 'token'),
                    'noticias': file.get('INDICADORES', 'noticias'), 'tendencia': file.get('INDICADORES', 'tendencia'),
                    'ativo': file.get('OPERACOES', 'ativo')}
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
        self.iq_bot.start_candles_stream(ativo, timeframe, 100)
        candles = self.iq_bot.get_realtime_candles(ativo, timeframe)
        self.iq_bot.stop_candles_stream(ativo, timeframe)


if __name__ == "__main__":
    bot = Bot()
    b = bot.arquivo('dados.txt')
    print(b['timeframe'])
    if b and bot.check_arquivo(b) and bot.conectar(b['email'], b['senha']):
        print(bot.lista_candle(b['ativo'], b['timeframe']))
