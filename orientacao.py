"""Classe Orientacao: representa um registro da base de conhecimento."""

AVISO = "este assistente NÃO é um canal oficial."


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação completa, com fonte, data e aviso."""
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")

    def exibir_resumo(self):
        """Versão curta, usada nas alternativas."""
        print(f"\n- {self.titulo}  [{self.categoria}]")
        print(f"  {self.resposta}")
        print(f"  Fonte: {self.fonte} (verificado em {self.verificado_em})")

    def __repr__(self):
        return f"Orientacao(id={self.id}, titulo={self.titulo!r})"
