class Token:
    def __init__(self, linha, coluna, lexema, tipo):
        self.linha = linha
        self.coluna = coluna
        self.lexema = lexema
        self.tipo = tipo


class ErroSintatico(Exception):
    pass


class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[self.posicao] if self.tokens else Token(0, 0, "", "")
        self.quantidade_erros = 0
        self.erros_semanticos = 0
        self.simbolos = {}

    def inserir_simbolo(self, nome, tipo):
        if nome in self.simbolos:
            self.erro_semantico(f"Variavel '{nome}' ja declarada")
        else:
            self.simbolos[nome] = tipo

    def buscar_simbolo(self, nome):
        if nome not in self.simbolos:
            self.erro_semantico(f"Variavel '{nome}' nao declarada")
            return 'desconhecido'
        return self.simbolos[nome]

    def erro_semantico(self, msg):
        self.erros_semanticos += 1
        print(f"[Erro Semantico] Linha {self.token_atual.linha}: {msg}.")

    def checar_tipos(self, t1, t2):
        if t1 == 'desconhecido' or t2 == 'desconhecido' or t1 == t2:
            return t1
        if (t1 == 'float' and t2 == 'int') or (t1 == 'boolean' and t2 == 'int'):
            return t1
        self.erro_semantico(f"Tipos incompativeis ('{t1}' e '{t2}')")
        return 'desconhecido'

    def proximo_token(self):
        self.posicao += 1
        if self.posicao < len(self.tokens):
            self.token_atual = self.tokens[self.posicao]
        else:
            self.token_atual = Token(0, 0, "EOF", "EOF")

    def consumir_token(self, esperado, comparar_por_tipo=False):
        condicao = (self.token_atual.tipo == esperado) if comparar_por_tipo else (self.token_atual.lexema == esperado)
        if condicao:
            self.proximo_token()
        else:
            self.quantidade_erros += 1
            print(
                f"[Erro Sintatico] Linha {self.token_atual.linha}, Coluna {self.token_atual.coluna}: esperado '{esperado}', encontrado '{self.token_atual.lexema}'.")
            raise ErroSintatico()

    def modo_panico(self):
        print(" -> [Modo Panico] Pulando tokens ate o proximo ';'")
        while self.token_atual.lexema != ';' and self.token_atual.tipo != 'EOF':
            self.proximo_token()
        if self.token_atual.lexema == ';':
            self.proximo_token()

    def programa(self):
        self.lista_comandos()
        if self.token_atual.tipo != 'EOF':
            print(f"[Erro] Lixo no fim do arquivo: '{self.token_atual.lexema}'")
            self.quantidade_erros += 1

        total_erros = self.quantidade_erros + self.erros_semanticos
        if total_erros == 0:
            print("\nSUCESSO: Nenhuma falha sintatica ou semantica encontrada.")
        else:
            print(
                f"\nFINALIZADO: Analise concluida com {self.quantidade_erros} erro(s) sintatico(s) e {self.erros_semanticos} erro(s) semantico(s).")

    def lista_comandos(self):
        primeiros = ['int', 'float', 'char', 'boolean', 'if', 'while']
        if self.token_atual.lexema in primeiros or self.token_atual.tipo == 'IDENTIFICADOR':
            self.comando()
            self.lista_comandos()

    def comando(self):
        try:
            if self.token_atual.lexema in ['int', 'float', 'char', 'boolean']:
                self.declaracao()
            elif self.token_atual.tipo == 'IDENTIFICADOR':
                self.atribuicao()
            elif self.token_atual.lexema == 'if':
                self.condicional()
            elif self.token_atual.lexema == 'while':
                self.repeticao()
            else:
                self.consumir_token("comando valido")
        except ErroSintatico:
            self.modo_panico()

    def declaracao(self):
        tipo_var = self.token_atual.lexema
        self.consumir_token(tipo_var)
        nome_var = self.token_atual.lexema
        self.consumir_token('IDENTIFICADOR', True)
        self.inserir_simbolo(nome_var, tipo_var)
        self.resto_declaracao(tipo_var)
        self.consumir_token(';')

    def resto_declaracao(self, tipo_var):
        if self.token_atual.lexema == '=':
            self.consumir_token('=')
            tipo_expr = self.expressao()
            self.checar_tipos(tipo_var, tipo_expr)
            self.mais_declaracoes(tipo_var)
        else:
            self.mais_declaracoes(tipo_var)

    def mais_declaracoes(self, tipo_var):
        if self.token_atual.lexema == ',':
            self.consumir_token(',')
            nome_var = self.token_atual.lexema
            self.consumir_token('IDENTIFICADOR', True)
            self.inserir_simbolo(nome_var, tipo_var)
            self.resto_declaracao(tipo_var)

    def atribuicao(self):
        nome_var = self.token_atual.lexema
        tipo_var = self.buscar_simbolo(nome_var)
        self.consumir_token('IDENTIFICADOR', True)
        self.consumir_token('=')
        tipo_expr = self.expressao()
        self.checar_tipos(tipo_var, tipo_expr)
        self.consumir_token(';')

    def condicional(self):
        self.consumir_token('if')
        self.consumir_token('(')
        self.expressao()
        self.consumir_token(')')
        self.bloco_comandos()
        if self.token_atual.lexema == 'else':
            self.consumir_token('else')
            self.bloco_comandos()

    def repeticao(self):
        self.consumir_token('while')
        self.consumir_token('(')
        self.expressao()
        self.consumir_token(')')
        self.bloco_comandos()

    def bloco_comandos(self):
        self.consumir_token('{')
        self.lista_comandos()
        self.consumir_token('}')

    def expressao(self):
        tipo_esq = self.termo()
        return self.expressao_linha(tipo_esq)

    def expressao_linha(self, tipo_esq):
        if self.token_atual.lexema in ['==', '!=', '<=', '>=', '<', '>', '&&', '||']:
            self.consumir_token(self.token_atual.lexema)
            tipo_dir = self.termo()
            self.checar_tipos(tipo_esq, tipo_dir)
            tipo_atual = 'boolean'
            return self.expressao_linha(tipo_atual)
        return tipo_esq

    def termo(self):
        tipo_esq = self.fator()
        return self.termo_linha(tipo_esq)

    def termo_linha(self, tipo_esq):
        if self.token_atual.lexema in ['+', '-']:
            self.consumir_token(self.token_atual.lexema)
            tipo_dir = self.fator()
            tipo_atual = self.checar_tipos(tipo_esq, tipo_dir)
            return self.termo_linha(tipo_atual)
        return tipo_esq

    def fator(self):
        tipo_esq = self.multiplicacao()
        return self.multiplicacao_linha(tipo_esq)

    def multiplicacao_linha(self, tipo_esq):
        if self.token_atual.lexema in ['*', '/', '%']:
            self.consumir_token(self.token_atual.lexema)
            tipo_dir = self.multiplicacao()
            tipo_atual = self.checar_tipos(tipo_esq, tipo_dir)
            return self.multiplicacao_linha(tipo_atual)
        return tipo_esq

    def multiplicacao(self):
        if self.token_atual.lexema == '(':
            self.consumir_token('(')
            tipo = self.expressao()
            self.consumir_token(')')
            return tipo
        elif self.token_atual.lexema == '!':
            self.consumir_token('!')
            self.multiplicacao()
            return 'boolean'
        elif self.token_atual.tipo == 'IDENTIFICADOR':
            tipo = self.buscar_simbolo(self.token_atual.lexema)
            self.consumir_token('IDENTIFICADOR', True)
            return tipo
        elif self.token_atual.tipo == 'LITERAL':
            lex = self.token_atual.lexema
            tipo = 'int'
            if '.' in lex:
                tipo = 'float'
            elif lex.startswith('"') or lex.startswith("'"):
                tipo = 'char'
            self.consumir_token('LITERAL', True)
            return tipo
        else:
            self.consumir_token("expressao")
            return 'desconhecido'


def carregar_tokens(arquivo):
    lista_tokens = []
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha_texto in f.readlines()[2:]:
                if not linha_texto.strip():
                    continue
                linha = int(linha_texto[0:7].strip())
                coluna = int(linha_texto[9:16].strip())
                lexema = linha_texto[18:53].strip()
                tipo = linha_texto[55:].strip()
                if tipo != "ERRO_LEXICO":
                    lista_tokens.append(Token(linha, coluna, lexema, tipo))
        return lista_tokens
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} nao encontrado.")
        return []


if __name__ == "__main__":
    lista_tokens = carregar_tokens("tokens.txt")
    if lista_tokens:
        analisador = AnalisadorSintatico(lista_tokens)
        analisador.programa()