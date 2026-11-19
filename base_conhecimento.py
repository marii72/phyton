"""Classe BaseConhecimento: lê o JSON, lista categorias e busca por pontuação."""

import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

# Pesos e limites da busca (explicados no README)
PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
TAMANHO_MIN_PALAVRA_TITULO = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3

# Campo -> tipo esperado (todos obrigatórios)
CAMPOS = {
    "id": int,
    "categoria": str,
    "titulo": str,
    "palavras_chave": list,
    "resposta": str,
    "documentos": list,
    "onde": str,
    "fonte": str,
    "verificado_em": str,
}


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação; devolve com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def confianca(pontos):
    """Converte pontos em nível de confiança (None se abaixo do mínimo)."""
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    """Conjunto de todas as orientações (composição de objetos Orientacao)."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava o programa."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: base de conhecimento não encontrada em '{self.caminho}'.")
            return False
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"Aviso: o arquivo '{self.caminho}' está corrompido.")
            return False
        except OSError as erro:
            print(f"Aviso: não foi possível abrir a base ({erro}).")
            return False

        if not isinstance(dados, list):
            print("Aviso: a base deve ser uma lista de orientações.")
            return False

        for numero, registro in enumerate(dados, start=1):
            if self._registro_valido(registro):
                self.orientacoes.append(Orientacao(**registro))
            else:
                print(f"Aviso: registro {numero} ignorado (campos ausentes ou inválidos).")
        return len(self.orientacoes) > 0

    @staticmethod
    def _registro_valido(registro):
        if not isinstance(registro, dict):
            return False
        if set(registro.keys()) != set(CAMPOS.keys()):
            return False
        for campo, tipo in CAMPOS.items():
            valor = registro[campo]
            if not isinstance(valor, tipo) or isinstance(valor, bool):
                return False
        if not all(isinstance(p, str) for p in registro["palavras_chave"]):
            return False
        if not all(isinstance(d, str) for d in registro["documentos"]):
            return False
        return True

    def categorias(self):
        """Lista de categorias, sem repetir, na ordem em que aparecem."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta_normalizada, orientacao):
        """+3 por palavra-chave na pergunta; +1 por palavra (4+ letras) no título."""
        pontos = 0
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        palavras_titulo = normalizar(orientacao.titulo).split()
        palavras_pergunta = set(pergunta_normalizada.split())
        for palavra in palavras_pergunta:
            if len(palavra) >= TAMANHO_MIN_PALAVRA_TITULO and palavra in palavras_titulo:
                pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor."""
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
