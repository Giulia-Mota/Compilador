class Token:
    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"<{self.tipo}, {self.lexema}, {self.linha}, {self.coluna}>"


class PalavrasReservadas:
    def __init__(self):
        self.reservadas = {
            "int", "float", "char", "boolean", "void", "if",
            "else", "for", "while", "scanf", "println", "main", "return"
        }

    def verificar_tipo(self, lexema, tipo_base):
        if lexema in self.reservadas:
            return "PALAVRA_CHAVE"
        return tipo_base


class AnalisadorLexico:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.tabela = PalavrasReservadas()

    def gerar_tokens(self):
        tokens = []
        tamanho = len(self.codigo)

        while self.pos < tamanho:
            char_atual = self.codigo[self.pos]

            if char_atual in ' \t\r':
                self.pos += 1
                self.coluna += 1
                continue

            if char_atual == '\n':
                self.pos += 1
                self.linha += 1
                self.coluna = 1
                continue

            if self.codigo.startswith('/*', self.pos):
                inicio_linha = self.linha
                inicio_coluna = self.coluna
                buffer_coment = "/*"
                self.pos += 2
                self.coluna += 2
                while self.pos < tamanho and not self.codigo.startswith('*/', self.pos):
                    if self.codigo[self.pos] == '\n':
                        buffer_coment += '\n'
                        self.pos += 1
                        self.linha += 1
                        self.coluna = 1
                    else:
                        buffer_coment += self.codigo[self.pos]
                        self.pos += 1
                        self.coluna += 1
                if self.pos >= tamanho:
                    tokens.append(Token("ERRO_LEXICO", buffer_coment, inicio_linha, inicio_coluna))
                else:
                    self.pos += 2
                    self.coluna += 2
                continue

            if char_atual == '"':
                inicio_linha = self.linha
                inicio_coluna = self.coluna
                temp = '"'
                self.pos += 1
                self.coluna += 1
                while self.pos < tamanho and self.codigo[self.pos] != '"' and self.codigo[self.pos] != '\n':
                    temp += self.codigo[self.pos]
                    self.pos += 1
                    self.coluna += 1
                if self.pos < tamanho and self.codigo[self.pos] == '"':
                    temp += '"'
                    self.pos += 1
                    self.coluna += 1
                    tokens.append(Token("LITERAL", temp, inicio_linha, inicio_coluna))
                else:
                    tokens.append(Token("ERRO_LEXICO", temp, inicio_linha, inicio_coluna))
                continue

            inicio_linha = self.linha
            inicio_coluna = self.coluna
            pivo = self.pos

            if char_atual.isalpha():
                while self.pos < tamanho and self.codigo[self.pos].isalnum():
                    self.pos += 1
                    self.coluna += 1
                lexema = self.codigo[pivo:self.pos]
                categoria = self.tabela.verificar_tipo(lexema, "IDENTIFICADOR")
                tokens.append(Token(categoria, lexema, inicio_linha, inicio_coluna))
                continue

            if char_atual.isdigit():
                while self.pos < tamanho and self.codigo[self.pos].isdigit():
                    self.pos += 1
                    self.coluna += 1
                if self.pos < tamanho and self.codigo[self.pos] == '.':
                    self.pos += 1
                    self.coluna += 1
                    while self.pos < tamanho and self.codigo[self.pos].isdigit():
                        self.pos += 1
                        self.coluna += 1
                lexema = self.codigo[pivo:self.pos]
                tokens.append(Token("LITERAL", lexema, inicio_linha, inicio_coluna))
                continue

            if char_atual in ['=', '!', '<', '>']:
                if self.pos + 1 < tamanho and self.codigo[self.pos + 1] == '=':
                    lexema = self.codigo[self.pos:self.pos + 2]
                    self.pos += 2
                    self.coluna += 2
                else:
                    lexema = char_atual
                    self.pos += 1
                    self.coluna += 1
                tokens.append(Token("OPERADOR", lexema, inicio_linha, inicio_coluna))
                continue

            if char_atual == '&' and self.pos + 1 < tamanho and self.codigo[self.pos + 1] == '&':
                lexema = '&&'
                self.pos += 2
                self.coluna += 2
                tokens.append(Token("OPERADOR", lexema, inicio_linha, inicio_coluna))
                continue

            if char_atual == '|' and self.pos + 1 < tamanho and self.codigo[self.pos + 1] == '|':
                lexema = '||'
                self.pos += 2
                self.coluna += 2
                tokens.append(Token("OPERADOR", lexema, inicio_linha, inicio_coluna))
                continue

            if char_atual in '+-*/%':
                lexema = char_atual
                self.pos += 1
                self.coluna += 1
                tokens.append(Token("OPERADOR", lexema, inicio_linha, inicio_coluna))
                continue

            if char_atual in '(){}[];,':
                lexema = char_atual
                self.pos += 1
                self.coluna += 1
                tokens.append(Token("DELIMITADOR", lexema, inicio_linha, inicio_coluna))
                continue

            lexema = char_atual
            self.pos += 1
            self.coluna += 1
            tokens.append(Token("ERRO_LEXICO", lexema, inicio_linha, inicio_coluna))

        return tokens


def main():
    try:
        with open("teste.txt", 'r', encoding='utf-8') as f:
            conteudo = f.read()
        analisador = AnalisadorLexico(conteudo)
        tokens = analisador.gerar_tokens()
        print(f"\n{'LINHA':<7}  {'COLUNA':<7}  {'TEXTO':<35}  {'CATEGORIA'}")
        print("." * 90)
        for t in tokens:
            lexema_formatado = t.lexema.replace('\n', '\\n')
            print(f"{t.linha:<7}  {t.coluna:<7}  {lexema_formatado:<35}  {t.tipo}")
    except FileNotFoundError:
        print("O arquivo teste.txt nao foi encontrado.")


if __name__ == "__main__":
    main()