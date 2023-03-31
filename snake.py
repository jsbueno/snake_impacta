#!/usr/bin/env python
# -*- coding: utf-8 -*-

#SNAKE - jogo clássico em python, implementação pedagógica
#Copyright (C) 2008  <João S. O. Bueno>, <Roberto Fagá>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


#Authors: Roberto Fagá (Portuguese),
# João S. O. Bueno (translation to Python)

from array import array
import sys

#sequencia ANSIpara limpar o terminal e posicionar o ursor no inicio:
#FIXME: isso não funciona pro padrão no windows -
#para os testes, deve-se achar um jeito "barato" de limpar
#o terminal de texto.
HOME_ANSI = "\x1b[2J\x1b[0;0H"
#J. Exceções para tornar mais simples saber quando a cobra morreu
class CobraMorreu(Exception):
    pass

class CobraBateuEmSiMesma(CobraMorreu):
    pass

class CobraBateuNaParede(CobraMorreu):
    pass


#R. Usar uma matriz grande

LARGURA, ALTURA = GRANDE = (30, 30)

#R. Cada valor da matriz dessa forma é um valor numérico, por exemplo,
#R. e o número remete ao código da imagem e o objeto correspondente.
#R. Ex: de 1 a 3 é a cobra (cabeça, corpo ou calda),

VAZIO = 0
COBRA_CABECA = 1
COBRA_CORPO = 2
COBRA_CAUDA = 3

#R. 5 é a maçã,
MACA = 5

#R. 8 é  parede, algo assim.
# Faça sempre com constantes nesse caso.

PAREDE = 8



#R. (pode ser lista dentro de lista mesmo) em
#R. que cada ponto pode ser parede, item a pegar ou parte da cobra.


class Mapa(object):
    from array import array
    def __init__(self, largura=LARGURA, altura=ALTURA):
        self.largura, self.altura = largura, altura
        self.data = array("B", [VAZIO  for i in xrange(largura * altura)])

    def __getitem__(self, indice):
        return self.data[indice[0] + indice[1] * self.largura]

    def __setitem__(self, indice, content):
        if indice is None:
            return
        try:
            self.data[indice[0] + indice[1] * self.largura] = content
        except IndexError:
            pass

    def linha_h(self, linha, x1, x2):
        for x  in range(x1, x2):
            self[x, linha] = PAREDE
    def linha_v(self, coluna, y1, y2):
        for y  in range(y1, y2):
            self[coluna, y] = PAREDE
    def retangulo(self, x1, y1, x2, y2):
        self.linha_h(y1, x1, x2 - 1)
        self.linha_h(y2 - 1, x1, x2 - 1)
        self.linha_v(x1, y1, y2- 1)
        self.linha_v(x2 - 1, y1, y2 - 1)
        self[x2 - 1, y2 - 1] = PAREDE

    def desenha(self):
        """Imprime mapa no terminal para testes -
           deve ser overrided numa sub-classe para
           implementacção gráfica
        """

        dic_figuras = {PAREDE:"+", COBRA_CORPO:"*", COBRA_CABECA:"@", COBRA_CAUDA:".", VAZIO:" "}
        sys.stdout.write(HOME_ANSI)
        for y in range(self.altura):
            for x in range(self.altura):
                sys.stdout.write(dic_figuras[self[x,y]] + " ")
            sys.stdout.write("\n")

itens_mortais = (PAREDE, COBRA_CABECA, COBRA_CORPO, COBRA_CAUDA)

#R. Para o
# movimento da cobra aqui é bem simples, vc simplesmente armazena a
# direção em uma variável +1 a -1 na horizontal e na vertical. Dessa
# forma, se o usuário pressionar "direita" por exemplo, essas
# variáveis assumem valor horizontal +1 e vertical 0.

class Cobra(list):
    def __init__(self, posicao, direcao, velocidade, comprimento, mapa = None):
        """J. posicao => tupla de coordenadas da cobra no mapa
            direcao -> tupla com a direcao x e y de movimento da cobra -
                       cada componente podendo ser 1, 0 ou -1
            velocidade -> numero de interacoes do laço principal entre
                         as atualizações da  posição da cobra
        """
        list.__init__(self)
        self.posicao = posicao
        self.direcao = direcao
        self.velocidade = velocidade
        x, y = tuple(posicao)
        for pedaco in range(comprimento):
            self.append((x,y))
            #j. o corpo se extende na direção contrária ao movimento
            x -=  direcao[0]
            y -=  direcao[1]
        self.cabeca = 0
        self.aumentando = 0
        self.pos_rastro = None
        if mapa:
            self.mapeia(mapa)
        self.contador = 0
        self.chama_maca = None

    def atualiza(self):
        self.contador += 1
        if not self.contador % self.velocidade:
            self.mover()

    #J. definimos os metodos de acesso aos itens, de modo que
    # o acesso a coordenadas do corpo da cobra seja normalizado
    # em relação a cabeça. (i.e. cobra[0] sempre vai retornar
    # as coordenadas da cabeça)
    def __getitem__(self, posicao):
        return list.__getitem__(self, (self.cabeca + posicao) % len(self))
        #J. O divertido é que só isso funciona inclusive para itens negativos.
        # cobra[-1] vai retornar as coordenadas da cauda

    def __setitem__(self, posicao, valor):
        list.__setitem__(self, (self.cabeca + posicao) % len(self), valor)

    def __iter__(self):
        def cobraIter(cobra):
            indice = 0
            while True:
                if indice == len(cobra):
                    raise StopIteration
                indice += 1
                yield cobra[indice - 1]
        return cobraIter(self)

    def insert(self, posicao, valor):
        list.insert(self, (self.cabeca + posicao) % len(self), valor)

    #R. A cada refresh
    # de tela a posição da cobra é então incrementada, fazendo com que
    # cada casa dela desloque para a casa que estava a parte anterior da
    # cobra e a cabeça na direção nova. Vc pode armazenar em um vetor a
    # cobra, sendo que cada casa do vetor é a posição atual da matriz,
    # assim pode ficar mais fácil de dar o refresh.
    def mover(self):
        x, y = self[0]
        x += self.direcao[0]
        y += self.direcao[1]

        #J. Se a cobra está em fase de crescimento, aumentar o vetor
        if self.aumentando > 0:
            self.esta_aumentando = True
            self.insert(0, None)
            self.aumentando -= 1
        else:
            self.esta_aumentando = False
            self.cabeca -= 1
            if self.cabeca < 0:
                self.cabeca = len(self) - 1

            self.pos_rastro = self[0]
        self[0] = None
        self.testa_morte_so((x,y))
        self.testa_maca((x,y))
        self[0] = (x,y)
        if hasattr(self, "mapa"):
            self.atualiza_mapa()


    #R. O teste de colisão é
    # muito simples, é só testar se no refresh, a cabeça foi para uma
    # casa já ocupada ou não.
    def testa_morte_so(self, pos):
        if pos in self:
            raise CobraBateuEmSiMesma("bum")

    def testa_morte_mapa(self, pos):
        if self.mapa[pos] == PAREDE:
            raise CobraBateuNaParede("Poft!")
        elif self.mapa[pos] in itens_mortais:
                raise CobraMorreu("argh")

    def testa_maca(self, pos):
        if self.mapa[pos] == MACA:
            self.chama_maca(pos)

    def mapeia(self, mapa):
        """J. Aplica a cobra num mapa limpo, e associa este mapa
           à instancia da cobra
        """
        self.mapa = mapa
        dic_parte = {0: COBRA_CABECA, len(self) -1: COBRA_CAUDA}
        for i, pedaco in enumerate(self):
            self.testa_morte_mapa(pedaco)
            self.mapa[pedaco] = dic_parte.get(i, COBRA_CORPO)

    def atualiza_mapa(self):
        self.testa_morte_mapa(self[0])
        if not self.esta_aumentando: #self.pos_rastro is not None :
            self.mapa[self.pos_rastro] = VAZIO
            self.mapa[self[-1]] = COBRA_CAUDA
        self.mapa[self[0]] = COBRA_CABECA
        self.mapa[self[1]] = COBRA_CORPO
        #if self.esta_aumentando:
        #    self.mapa[self[2]] = COBRA_CORPO
            #self.mapa[self[-2]] = COBRA_CORPO

def mapa_0(classe_mapas=Mapa,  *args, **kwargs):
    mapa = classe_mapas(*args, **kwargs)
    mapa.retangulo(0, 0, mapa.largura, mapa.altura)
    return mapa

if __name__ == "__main__":
    from time import sleep

    mapa = mapa_0()
    #mapa.linha_h(5, 10, 20)
    cobra = Cobra((4,3), (1,0), 6, 4, mapa)

    mapa.desenha()
    t = 0.1
    for i in range(60):
        cobra.mover()
        mapa.desenha()
        sleep(t)
        if i == 10:
            cobra.direcao=(0,1)
        elif i == 20:
            cobra.aumentando = 3
        elif i == 30:
            cobra.direcao=(-1,0)
            cobra.aumentando += 4
        elif i == 37:
            cobra.direcao=(0, -1)
        elif i == 48:
            cobra.direcao = (1,0)


# Você pode até fazer efeito de animação, colocando o incremento de
# -0.25 a +0.25 por exemplo, e só aceitando o controle e testando
# colisão de 4 em 4 quadros. A maçã faz crescer a cobra, é só
# aumentar o vetor da cobra, apagar a maçã e randomizar uma nova em
# algum lugar do mapa desocupado (pode ser por tentativa e erro
# mesmo).
# Depois esses mapas, sem a cobra e a maçã, podem ser armazenados em
# arquivos com cPickle mesmo, que armazena variáveis Python. Aí vc só
# lê a matriz do mapa e coloca a cobra e a maçã.
