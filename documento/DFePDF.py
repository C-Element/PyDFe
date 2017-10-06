from math import fmod

from fpdf import FPDF

DIREITA = 2
ESQUERDA = 0
SUPERIOR = 1


def strtr(texto: str, de: str, para: str) -> str:
    tradutor = dict(zip(list(de), list(para)))
    texto_lista = list(texto)
    i = 0
    while i < len(texto_lista):
        l = texto_lista[i]
        if l in tradutor.keys():
            texto_lista[i] = tradutor[l]
        i += 1
    return ''.join(texto_lista)


class FontePDF(object):
    def __init__(self, nome='Times', tamanho=8, estilo=''):
        self.estilo = estilo
        self.nome = nome
        self.tamanho = tamanho


class DFePDF(FPDF):
    def __init__(self, margens: list = (7, 7, 7)):
        super().__init__()
        self.margens = margens  # Superior, Direita, Inferior, Esquerda
        self.x = self.margens[ESQUERDA]  # self.x e self.y onde iniciará a 'desenhar' na página
        self.y = self.margens[SUPERIOR]
        self.altura_max = 297 - self.margens[SUPERIOR]
        self.largura_max = 210 - self.margens[ESQUERDA]  # Iremos trabalhar a principio apenas com A4 em porta retrato
        self.set_margins(*self.margens)
        self.alias_nb_pages()

        self.conjunto_abc = ''  # conjunto de caracteres legiveis em 128
        self.conjunto_a = ''  # grupo A do conjunto de de caracteres legiveis
        self.conjunto_b = ''  # grupo B do conjunto de caracteres legiveis
        self.conjunto_c = ''  # grupo C do conjunto de caracteres legiveis
        self.conjunto_de = dict(A='', B='', C='')  # converter de
        self.conjunto_para = dict(A='', B='', C='')  # converter para
        self.conjunto_inicio = dict(A=103, B=104, C=105)  # Caracteres de seleção do grupo 128
        self.conjunto_troca = dict(A=101, B=100, C=99)  # Caracteres de troca de grupo
        self.tabela_128 = [[2, 1, 2, 2, 2, 2],  # 0 : [ ]
                           [2, 2, 2, 1, 2, 2],  # 1 : [!]
                           [2, 2, 2, 2, 2, 1],  # 2 : ["]
                           [1, 2, 1, 2, 2, 3],  # 3 : [#]
                           [1, 2, 1, 3, 2, 2],  # 4 : [$]
                           [1, 3, 1, 2, 2, 2],  # 5 : [%]
                           [1, 2, 2, 2, 1, 3],  # 6 : [&]
                           [1, 2, 2, 3, 1, 2],  # 7 : [']
                           [1, 3, 2, 2, 1, 2],  # 8 : [(]
                           [2, 2, 1, 2, 1, 3],  # 9 : [)]
                           [2, 2, 1, 3, 1, 2],  # 10 : [*]
                           [2, 3, 1, 2, 1, 2],  # 11 : [+]
                           [1, 1, 2, 2, 3, 2],  # 12 : [,]
                           [1, 2, 2, 1, 3, 2],  # 13 : [-]
                           [1, 2, 2, 2, 3, 1],  # 14 : [.]
                           [1, 1, 3, 2, 2, 2],  # 15 : [/]
                           [1, 2, 3, 1, 2, 2],  # 16 : [0]
                           [1, 2, 3, 2, 2, 1],  # 17 : [1]
                           [2, 2, 3, 2, 1, 1],  # 18 : [2]
                           [2, 2, 1, 1, 3, 2],  # 19 : [3]
                           [2, 2, 1, 2, 3, 1],  # 20 : [4]
                           [2, 1, 3, 2, 1, 2],  # 21 : [5]
                           [2, 2, 3, 1, 1, 2],  # 22 : [6]
                           [3, 1, 2, 1, 3, 1],  # 23 : [7]
                           [3, 1, 1, 2, 2, 2],  # 24 : [8]
                           [3, 2, 1, 1, 2, 2],  # 25 : [9]
                           [3, 2, 1, 2, 2, 1],  # 26 : [:]
                           [3, 1, 2, 2, 1, 2],  # 27 : [;]
                           [3, 2, 2, 1, 1, 2],  # 28 : [<]
                           [3, 2, 2, 2, 1, 1],  # 29 : [=]
                           [2, 1, 2, 1, 2, 3],  # 30 : [>]
                           [2, 1, 2, 3, 2, 1],  # 31 : [?]
                           [2, 3, 2, 1, 2, 1],  # 32 : [@]
                           [1, 1, 1, 3, 2, 3],  # 33 : [A]
                           [1, 3, 1, 1, 2, 3],  # 34 : [B]
                           [1, 3, 1, 3, 2, 1],  # 35 : [C]
                           [1, 1, 2, 3, 1, 3],  # 36 : [D]
                           [1, 3, 2, 1, 1, 3],  # 37 : [E]
                           [1, 3, 2, 3, 1, 1],  # 38 : [F]
                           [2, 1, 1, 3, 1, 3],  # 39 : [G]
                           [2, 3, 1, 1, 1, 3],  # 40 : [H]
                           [2, 3, 1, 3, 1, 1],  # 41 : [I]
                           [1, 1, 2, 1, 3, 3],  # 42 : [J]
                           [1, 1, 2, 3, 3, 1],  # 43 : [K]
                           [1, 3, 2, 1, 3, 1],  # 44 : [L]
                           [1, 1, 3, 1, 2, 3],  # 45 : [M]
                           [1, 1, 3, 3, 2, 1],  # 46 : [N]
                           [1, 3, 3, 1, 2, 1],  # 47 : [O]
                           [3, 1, 3, 1, 2, 1],  # 48 : [P]
                           [2, 1, 1, 3, 3, 1],  # 49 : [Q]
                           [2, 3, 1, 1, 3, 1],  # 50 : [R]
                           [2, 1, 3, 1, 1, 3],  # 51 : [S]
                           [2, 1, 3, 3, 1, 1],  # 52 : [T]
                           [2, 1, 3, 1, 3, 1],  # 53 : [U]
                           [3, 1, 1, 1, 2, 3],  # 54 : [V]
                           [3, 1, 1, 3, 2, 1],  # 55 : [W]
                           [3, 3, 1, 1, 2, 1],  # 56 : [X]
                           [3, 1, 2, 1, 1, 3],  # 57 : [Y]
                           [3, 1, 2, 3, 1, 1],  # 58 : [Z]
                           [3, 3, 2, 1, 1, 1],  # 59 : [[]
                           [3, 1, 4, 1, 1, 1],  # 60 : [\]
                           [2, 2, 1, 4, 1, 1],  # 61 : []]
                           [4, 3, 1, 1, 1, 1],  # 62 : [^]
                           [1, 1, 1, 2, 2, 4],  # 63 : [_]
                           [1, 1, 1, 4, 2, 2],  # 64 : [`]
                           [1, 2, 1, 1, 2, 4],  # 65 : [a]
                           [1, 2, 1, 4, 2, 1],  # 66 : [b]
                           [1, 4, 1, 1, 2, 2],  # 67 : [c]
                           [1, 4, 1, 2, 2, 1],  # 68 : [d]
                           [1, 1, 2, 2, 1, 4],  # 69 : [e]
                           [1, 1, 2, 4, 1, 2],  # 70 : [f]
                           [1, 2, 2, 1, 1, 4],  # 71 : [g]
                           [1, 2, 2, 4, 1, 1],  # 72 : [h]
                           [1, 4, 2, 1, 1, 2],  # 73 : [i]
                           [1, 4, 2, 2, 1, 1],  # 74 : [j]
                           [2, 4, 1, 2, 1, 1],  # 75 : [k]
                           [2, 2, 1, 1, 1, 4],  # 76 : [l]
                           [4, 1, 3, 1, 1, 1],  # 77 : [m]
                           [2, 4, 1, 1, 1, 2],  # 78 : [n]
                           [1, 3, 4, 1, 1, 1],  # 79 : [o]
                           [1, 1, 1, 2, 4, 2],  # 80 : [p]
                           [1, 2, 1, 1, 4, 2],  # 81 : [q]
                           [1, 2, 1, 2, 4, 1],  # 82 : [r]
                           [1, 1, 4, 2, 1, 2],  # 83 : [s]
                           [1, 2, 4, 1, 1, 2],  # 84 : [t]
                           [1, 2, 4, 2, 1, 1],  # 85 : [u]
                           [4, 1, 1, 2, 1, 2],  # 86 : [v]
                           [4, 2, 1, 1, 1, 2],  # 87 : [w]
                           [4, 2, 1, 2, 1, 1],  # 88 : [x]
                           [2, 1, 2, 1, 4, 1],  # 89 : [y]
                           [2, 1, 4, 1, 2, 1],  # 90 : [z]
                           [4, 1, 2, 1, 2, 1],  # 91 : [{]
                           [1, 1, 1, 1, 4, 3],  # 92 : [|]
                           [1, 1, 1, 3, 4, 1],  # 93 : [}]
                           [1, 3, 1, 1, 4, 1],  # 94 : [~]
                           [1, 1, 4, 1, 1, 3],  # 95 : [DEL]
                           [1, 1, 4, 3, 1, 1],  # 96 : [FNC3]
                           [4, 1, 1, 1, 1, 3],  # 97 : [FNC2]
                           [4, 1, 1, 3, 1, 1],  # 98 : [SHIFT]
                           [1, 1, 3, 1, 4, 1],  # 99 : [Cswap]
                           [1, 1, 4, 1, 3, 1],  # 100 : [Bswap]
                           [3, 1, 1, 1, 4, 1],  # 101 : [Aswap]
                           [4, 1, 1, 1, 3, 1],  # 102 : [FNC1]
                           [2, 1, 1, 4, 1, 2],  # 103 : [Astart]
                           [2, 1, 1, 2, 1, 4],  # 104 : [Bstart]
                           [2, 1, 1, 2, 3, 2],  # 105 : [Cstart]
                           [2, 3, 3, 1, 1, 1],  # 106 : [STOP]
                           [2, 1]]  # 107 : [END BAR]
        i = 32
        self.conjunto_c = '0123456789'
        while i <= 95:  # conjunto de caracteres
            self.conjunto_abc += chr(i)
            i += 1
        self.conjunto_a = self.conjunto_abc
        self.conjunto_b = self.conjunto_abc
        i = 0
        while i <= 31:
            self.conjunto_abc += chr(i)
            self.conjunto_a += chr(i)
            i += 1
        i = 96
        while i <= 126:
            self.conjunto_abc += chr(i)
            self.conjunto_b += chr(i)
            i += 1
        i = 0
        while i < 107:
            if i < 96:
                self.conjunto_de['A'] += chr(i)
                self.conjunto_de['B'] += chr(i + 32)
                self.conjunto_para['A'] += chr((i + 64) if i < 32 else (i - 32))
                self.conjunto_para['B'] += chr(i)
            else:
                self.conjunto_de['A'] += chr(i + 104)
                self.conjunto_de['B'] += chr(i + 104)
                self.conjunto_para['A'] += chr(i)
                self.conjunto_para['B'] += chr(i)
            i += 1

    def header(self):
        self.cabecalho()

    def cabecalho(self):
        pass

    def retangulo(self, x: int, y: int, l: int, a: int) -> [int, int]:
        self.rect(x, y, l, a)
        return [x + l, y + a]

    # Quebra o texto para caber na caixa
    def quebra_texto(self, texto: str, largura_max: int) -> [str, int]:
        texto = texto.strip()
        if texto == '':
            return texto, 0
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
                       borda: bool = True, forcar: bool = False, altura_max: int = 0, deslocamento_v: int = 0):
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

    def codigo_barras_128(self, x: int, y: int, codigo: str, l: int, a: int):
        guia_a = ''
        guia_b = ''
        guia_c = ''
        i = 0
        while i < len(codigo):
            agora = codigo[i]
            guia_a += 'O' if agora in self.conjunto_a else 'N'
            guia_b += 'O' if agora in self.conjunto_b else 'N'
            guia_c += 'O' if agora in self.conjunto_c else 'N'
            i += 1
        s_codigo_pequeno = 'OOOO'
        i_codigo_pequeno = 4
        codificado = ''
        while codigo > '':
            i = guia_c.find(s_codigo_pequeno)
            if i >= 0:
                guia_a = guia_a[:i] + 'N' + guia_a[i:]
                guia_b = guia_b[:i] + 'N' + guia_b[i:]
            if guia_c[:i_codigo_pequeno] == s_codigo_pequeno:
                codificado += chr(self.conjunto_troca['C'] if codificado > '' else self.conjunto_inicio['C'])
                feito = guia_c.find('N')
                if feito < 0:
                    feito = len(guia_c)
                if fmod(feito, 2) == 1:
                    feito -= 1
                i = 0
                while i < feito:
                    codificado += chr(int(codigo[i:i + 2]))
                    i += 2
                grupo = 'C'
            else:
                feito_a = guia_a.find('N')
                if feito_a < 0:
                    feito_a = len(guia_a)
                feito_b = guia_b.find('N')
                if feito_b < 0:
                    feito_b = len(guia_b)
                if feito_a < feito_b:
                    feito = feito_b
                    grupo = 'B'
                else:
                    feito = feito_a
                    grupo = 'A'
                codificado += chr(self.conjunto_troca[grupo] if codificado > '' else self.conjunto_inicio[grupo])
                codificado += strtr(codigo[0: feito], self.conjunto_de[grupo], self.conjunto_para[grupo])
            codigo = codigo[feito:]
            guia_a = guia_a[feito:]
            guia_b = guia_b[feito:]
            guia_c = guia_c[feito:]
        checagem = ord(codificado[0])
        i = 0
        while i < len(codificado):
            checagem += (ord(codificado[i]) * i)
            i += 1
        checagem %= 103
        codificado += chr(checagem) + chr(106) + chr(107)
        modulo = l / ((len(codificado) * 11) - 8)
        i = 0
        while i < len(codificado):
            coordenadas = self.tabela_128[ord(codificado[i])]
            j = 0
            while j < len(coordenadas):
                self.rect(x, y, coordenadas[j] * modulo, a, "F")
                x += (coordenadas[j] + coordenadas[j+1]) * modulo
                j += 2
            i += 1
