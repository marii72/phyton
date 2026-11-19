"""Citizen Assist AI - ponto de entrada. Execute com: python main.py"""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA, "data")


def main():
    base = BaseConhecimento(os.path.join(PASTA_DADOS, "base_conhecimento.json"))
    base.carregar()  # lê o JSON e cria os objetos Orientacao

    assistente = Assistente("Citizen Assist AI", base, PASTA_DADOS)
    try:
        assistente.menu()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAtendimento encerrado. Até logo!")


if __name__ == "__main__":
    main()
