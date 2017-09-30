from fpdf import FPDF

SUPERIOR = 0
DIREITA = 1
ESQUERDA = 2


class FontePDF(object):
    def __init__(self, nome='Times', tamanho=8, estilo=''):
        self.estilo = estilo
        self.nome = nome
        self.tamanho = tamanho


class DFePDF(FPDF):
    def __init__(self, margens: list = (3, 3, 3)):
        super().__init__()
        self.margens = margens  # Superior, Direita, Inferior, Esquerda
        self.x = 1  # self.x e self.y onde iniciará a 'desenhar' na página
        self.y = 1
        self.max_altura = 297 - self.margens[SUPERIOR] + self.y
        self.max_largura = 210 - self.margens[ESQUERDA] - self.margens[DIREITA] + self.x  # Iremos trabalhar a principio apenas com A4 em porta retrato

        self.set_margins(*self.margens)

        self.alias_nb_pages()

    def retangulo(self, x: int, y: int, l: int, a: int) -> [int, int]:
        self.rect(x, y, l, a)
        return [x + l, y + a]

    # Quebra o texto para caber na caixa
    def quebra_texto(self, texto: str, largura_max: int) -> [str, int]:
        texto = texto.strip()
        if texto == '':
            return 0
        espaco = self.get_string_width(' ')
        linhas = texto.split('\n')
        texto = ''
        contador = 0
        for linha in linhas:
            palavras = linha.split(' ')
            largura = 0
            for palavra in palavras:
                largura_palavra = self.get_string_width(palavra)
                if largura_palavra > largura_max:
                    # Palavra muito longa, iremos cortar ela
                    for letra in palavra:
                        letra_l = self.get_string_width(letra)
                        if largura + letra_l <= largura_max:
                            largura += letra_l
                            texto += letra
                        else:
                            largura = letra_l
                            texto = f'{texto.rstrip()}\n{letra}'
                            contador += 1
                elif largura + largura_palavra <= largura_max:
                    largura += largura_palavra + espaco
                    texto += f'{palavra} '
                else:
                    largura = largura_palavra + espaco
                    texto = f'{texto.rstrip()}\n{palavra} '
                    contador += 1
            texto = f'{texto.rstrip()}\n'
            contador += 1
        return texto.rstrip(), contador

    # Cria uma caixa de texto com ou sem bordas. Esta função perimite o alinhamento horizontal
    # ou vertical do texto dentro da caixa.
    def caixa_de_texto(self, x: int, y: int, l: int, a: int, texto: str = '', fonte: FontePDF = FontePDF(), alinhamento_v: str = 'T', alinhamento_h: str = 'L',
                       borda: bool = True, forcar: bool = True, altura_max: int = 0, deslocamento_v: int = 0):
        y_ant = y
        y1 = 0
        x1 = 0
        resetou = False
        self.set_font(fonte.nome, fonte.estilo, fonte.tamanho)
        if l < 0:
            return y
        texto = texto.strip()
        if borda:
            self.rect(x, y, l, a)
        incremento_y = self.font_size  # tamanho da fonte na unidade definida
        if not forcar:
            texto, n = self.quebra_texto(texto, l)  # verificar se o texto cabe no espaço
        else:
            n = 1
        # calcular a altura do conjunto de texto
        altura_texto = incremento_y * n
        # separar o texto em linhas
        linhas = texto.split('\n')
        # verificar o alinhamento vertical
        if alinhamento_v == 'T':
            # alinhado ao topo
            y1 = y + incremento_y
        elif alinhamento_v == 'C':
            # alinhado ao centro
            y1 = y + incremento_y + ((a - altura_texto) / 2)
        elif alinhamento_v == 'B':
            # alinhado a base
            y1 = (y + a) - 0.5

        # para cada linha
        for line in linhas:
            # verificar o comprimento da frase
            texto = line.strip()
            comp = self.get_string_width(texto)
            if forcar:
                novo_tamanho = fonte.tamanho
                while comp > l:
                    # estabelecer novo fonte
                    novo_tamanho -= 1
                    self.set_font(fonte.nome, fonte.estilo, novo_tamanho)
                    comp = self.get_string_width(texto)

            # ajustar ao alinhamento horizontal
            if alinhamento_h == 'L':
                x1 = x + 0.5
            elif alinhamento_h == 'C':
                x1 = x + ((l - comp) / 2)
            elif alinhamento_h == 'R':
                x1 = x + l - (comp + 0.5)
            # escrever o texto
            if deslocamento_v > 0:
                if y1 > (y_ant + deslocamento_v):
                    if not resetou:
                        y1 = y_ant
                        resetou = True
            self.text(x1, y1, texto)
            # incrementar para escrever o proximo
            y1 += incremento_y
            if altura_max > 0 and y1 > (y + (altura_max - 1)):
                break
        return (y1 - y) - incremento_y
