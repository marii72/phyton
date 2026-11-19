"""Classe Assistente: atendimento, histórico, indicadores e exportação CSV."""

import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import confianca, LIMITE_MEDIA
from orientacao import AVISO

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos"]


class Assistente:
    """Quem conversa com o cidadão. Tem uma BaseConhecimento (composição)."""

    def __init__(self, nome, base, pasta_dados="data"):
        self.nome = nome
        self.base = base
        self.pasta_dados = pasta_dados
        self.caminho_historico = os.path.join(pasta_dados, "historico.json")
        self.caminho_notas = os.path.join(pasta_dados, "notas.json")
        self.caminho_csv = os.path.join(pasta_dados, "atendimentos.csv")
        self.historico = self._carregar_lista(self.caminho_historico)
        self.notas = self._carregar_lista(self.caminho_notas)

    # ------------------------------------------------------------------
    # Arquivos
    # ------------------------------------------------------------------
    def _carregar_lista(self, caminho):
        """Lê uma lista JSON. Se faltar ou estiver corrompida, começa vazia."""
        if not os.path.exists(caminho):
            return []
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list):
                raise ValueError("formato inesperado")
            return dados
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, OSError):
            print(f"Aviso: '{caminho}' está corrompido. Começando com a lista vazia.")
            try:
                os.replace(caminho, caminho + ".corrompido")
            except OSError:
                pass
            return []

    def _salvar_json(self, caminho, dados):
        try:
            os.makedirs(self.pasta_dados, exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"Aviso: não foi possível salvar '{caminho}' ({erro}).")

    # ------------------------------------------------------------------
    # Entrada de dados (nunca encerram o programa)
    # ------------------------------------------------------------------
    @staticmethod
    def ler_opcao(prompt, maximo):
        """Pede um número de 0 a maximo, repetindo até ser válido."""
        while True:
            texto = input(prompt).strip()
            if texto == "":
                print("Resposta vazia. Digite um número.")
                continue
            try:
                numero = int(texto)
            except ValueError:
                print("Digite apenas números.")
                continue
            if 0 <= numero <= maximo:
                return numero
            print(f"Opção fora da faixa. Escolha de 0 a {maximo}.")

    @staticmethod
    def ler_sn(prompt):
        """Pede s ou n; devolve True para 's'."""
        while True:
            texto = input(prompt).strip().lower()
            if texto in ("s", "n"):
                return texto == "s"
            print("Responda apenas com s ou n.")

    @staticmethod
    def tem_dado_pessoal(texto):
        """8 ou mais dígitos (CPF, telefone...) ou @ (e-mail)."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return digitos >= 8 or "@" in texto

    # ------------------------------------------------------------------
    # Registro
    # ------------------------------------------------------------------
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
        }
        self.historico.append(atendimento)
        self._salvar_json(self.caminho_historico, self.historico)

    # ------------------------------------------------------------------
    # Atendimento por pergunta
    # ------------------------------------------------------------------
    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        encontrou = False
        ajudou = False
        id_orientacao = None
        ultima_pergunta = ""

        while True:
            texto = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                break
            if texto == "":
                print("Resposta vazia. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if self.tem_dado_pessoal(texto):
                # Não conta tentativa e NÃO é registrada.
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue
            if not any(letra.isalpha() for letra in texto):
                print("Escreva sua dúvida com palavras, por favor.")
                continue

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)

            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                encontrou = False
                id_orientacao = None
                self._nao_encontrei()
                continue

            pontos, melhor = resultados[0]
            encontrou = True
            id_orientacao = melhor.id
            print(f"\nConfiança da resposta: {confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            alternativas = [(p, o) for p, o in resultados[1:3] if p >= LIMITE_MEDIA]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, outra in alternativas:
                    print(f"[{confianca(p)} - {p} pontos]", end="")
                    outra.exibir_resumo()

            ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if ajudou:
                break
            print("Tente reescrever a dúvida com outras palavras ou digite 0 para voltar.")

        if tentativas > 0:
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", ultima_pergunta, id_orientacao,
                           encontrou, ajudou, tentativas, tempo)

    def _nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras (por exemplo, o nome do documento ou do serviço)")
        print("ou use a navegação por categorias:")
        for categoria in self.base.categorias():
            print(f"  - {categoria}")

    # ------------------------------------------------------------------
    # Navegação por categorias
    # ------------------------------------------------------------------
    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("\nA base de conhecimento está vazia.")
            return
        while True:
            print("\n=== Categorias ===")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")
            opcao = self.ler_opcao("Escolha uma categoria: ", len(categorias))
            if opcao == 0:
                return
            self._navegar_categoria(categorias[opcao - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            inicio = time.time()
            print(f"\n=== {categoria} ===")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"{numero}. {orientacao.titulo}")
            print("0. Voltar")
            opcao = self.ler_opcao("Escolha uma orientação: ", len(orientacoes))
            if opcao == 0:
                return
            escolhida = orientacoes[opcao - 1]
            escolhida.exibir()
            ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", escolhida.titulo, escolhida.id,
                           True, ajudou, 1, tempo)

    # ------------------------------------------------------------------
    # Indicadores
    # ------------------------------------------------------------------
    def indicadores(self):
        """Calcula, exibe e devolve os indicadores."""
        total = len(self.historico)
        print("\n=== Indicadores ===")
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return {}

        encontrados = [a for a in self.historico if a["encontrou"]]
        ajudados = [a for a in self.historico if a["ajudou"]]
        pct_encontrou = len(encontrados) / total * 100
        pct_ajudou = len(ajudados) / total * 100
        tempo_medio = (sum(a["tempo_segundos"] for a in encontrados) / len(encontrados)
                       if encontrados else 0.0)
        tentativas_medias = sum(a["tentativas"] for a in self.historico) / total
        facilidade = sum(self.notas) / len(self.notas) if self.notas else None

        sem_solucao = []
        for atendimento in self.historico:
            if not atendimento["ajudou"] and atendimento["pergunta"] not in sem_solucao:
                sem_solucao.append(atendimento["pergunta"])

        print(f"Atendimentos registrados:   {total}")
        print(f"Resposta encontrada (%):    {pct_encontrou:.1f}")
        print(f"Taxa de acerto: ajudou (%): {pct_ajudou:.1f}")
        print(f"Tempo médio para encontrar: {tempo_medio:.1f} s")
        print(f"Tentativas por atendimento: {tentativas_medias:.1f}")
        if facilidade is None:
            print("Facilidade de uso (1 a 5):  sem notas ainda")
        else:
            print(f"Facilidade de uso (1 a 5):  {facilidade:.1f} ({len(self.notas)} notas)")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")

        return {
            "total": total,
            "resposta_encontrada_pct": round(pct_encontrou, 1),
            "ajudou_pct": round(pct_ajudou, 1),
            "tempo_medio_s": round(tempo_medio, 1),
            "tentativas_por_atendimento": round(tentativas_medias, 1),
            "facilidade_media": None if facilidade is None else round(facilidade, 1),
            "duvidas_sem_solucao": sem_solucao,
        }

    # ------------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------------
    def exportar_csv(self):
        if not self.historico:
            print("\nNão há atendimentos para exportar ainda.")
            return
        try:
            os.makedirs(self.pasta_dados, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow({campo: atendimento.get(campo, "")
                                       for campo in CAMPOS_CSV})
            print(f"\nArquivo exportado: {self.caminho_csv} "
                  f"({len(self.historico)} atendimentos).")
        except OSError as erro:
            print(f"Aviso: não foi possível exportar o CSV ({erro}).")

    # ------------------------------------------------------------------
    # Menu principal
    # ------------------------------------------------------------------
    def pedir_nota(self):
        print("\nAntes de sair: de 1 (muito difícil) a 5 (muito fácil),")
        print("como foi usar o assistente? (0 para pular)")
        nota = self.ler_opcao("Sua nota: ", 5)
        if nota == 0:
            return
        self.notas.append(nota)
        self._salvar_json(self.caminho_notas, self.notas)

    def menu(self):
        print(f"\n=== {self.nome} ===")
        print("Orientações com base em fontes verificadas, para quem vive em áreas de risco de enchentes e quer ajudar.")
        print("Não pedimos nome, CPF, telefone ou e-mail.")
        print(f"Aviso: {AVISO}")
        while True:
            print("\n--- Menu ---")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos para CSV")
            print("0. Sair")
            opcao = self.ler_opcao("Escolha: ", 4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.pedir_nota()
                print("\nObrigado por usar o Citizen Assist AI!")
                return
