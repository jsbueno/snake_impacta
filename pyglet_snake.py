#!/usr/bin/env python
# -*- coding: utf-8 -*-

#SNAKE - jogo clássico em python, implementação pedagógica
#Copyright (C) 2008  <João S. O. Bueno>

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


#Authors:  João S. O. Bueno (translation to Python)

import pyglet
from copy import copy
from random import randrange

import snake
from snake import PAREDE, VAZIO, COBRA_CORPO, COBRA_CABECA, COBRA_CAUDA, MACA

class GletMapa(snake.Mapa):
    def __init__(self, janela, largura, altura):
        self.janela = janela
        snake.Mapa.__init__(self, largura, altura)
        self.larg_celula = janela.width // self.largura
        self.alt_celula = janela.height // self.altura
        self.carrega_imagens()
        self.mapa_anterior = snake.Mapa(largura,altura)
        self.counter = 0
    def carrega_imagens(self):
        #l = lambda nome: pyglet.sprite.Sprite(pyglet.image.load(nome))
        l = pyglet.image.load
        self.imagens = {PAREDE: l("parede.png"),
                        VAZIO: l("quadrado_preto.png"),
                        COBRA_CORPO: l("esfera_1.png"),
                        COBRA_CABECA: l("esfera_2.png"),
                        COBRA_CAUDA: l("esfera_1.png"),
                        MACA: l("esfera_2.png")
                       }
        #for imagem in self.imagens.values():
            #imagem.scale = self.larg_celula / float(imagem.width)
            #print imagem.scale

    #def coord_mapa_pra_janela(self, (x, y)):
    #    return (x / float(mapa.largura) * janela.width,
    #            y / float(mapa.altura) * janela.height)
    def mantem_mapa_anterior(self):
        self.mapa_anterior.data = copy(self.data)

    def desenha(self):
        for y in range(self.altura):
            for x in range(self.largura):
                if self.counter != 0 and self[x, y] == self.mapa_anterior[x, y]:
                    continue
                imagem = self.imagens[self[x,y]]
                #print imagem,imagem.width, x, y
                i_x = x * self.larg_celula
                i_y = self.janela.height - ( (y +1 ) * self.alt_celula)
                imagem.blit(i_x, i_y)
        self.mantem_mapa_anterior()
        self.counter += 1

class Game(pyglet.window.Window):
    def __init__(self, largura, altura, *args, **kwargs):
        pyglet.window.Window.__init__(self, largura, altura, *args, **kwargs)
        self.carrega_sons()
        self.inicializa_jogo()

    def inicializa_jogo(self):
        pyglet.clock.unschedule(self.atualiza)
        self.mapa = snake.mapa_0(GletMapa, self, 40, 30)
        self.cobra = snake.Cobra((5,2), (1,0), 2, 4, self.mapa)
        self.cobra.chama_maca = self.comeu_maca
        self.pontos = 0
        self.jogo_acabou = False
        self.nova_maca()
        self.contador = 0
        pyglet.clock.schedule_interval(self.atualiza, 1/20.0)

    def carrega_sons(self):

        self.sons = {"maca_aparece": "pop.wav",
                     "comeu_maca": "KDE_Beep_Bottles.wav",
                     "morreu": "KDE_Critical_Error.wav"}
        for evento, arquivo in self.sons.items():
            self.sons[evento] = pyglet.resource.media(arquivo, streaming=False)


    def atualiza(self, relogio):
        self.contador += 1
        if not self.jogo_acabou:
            try:
                self.cobra.atualiza()
            except snake.CobraMorreu, morreu:
                self.jogo_acabou = True
                self.sons["morreu"].play()
                self.placar = pyglet.text.Label("%d pontos!" % self.pontos,
                                      font_name = "Sans",
                                      font_size = 80,
                                      x = self.width // 2,
                                      y = self.height // 2,
                                      anchor_x = "center",
                                      anchor_y = "center")
        else:
            self.placar.color=(255, 255, 10 * self.contador % 255, 255)
            self.placar.draw()

    def on_draw(self, *args):
        #self.clear()
        self.mapa.desenha()

    def on_key_press(self, simbolo, modificador):
        key = pyglet.window.key
        cobra = self.cobra
        if simbolo == key.RIGHT:
            cobra.direcao = (1,0)
        elif simbolo == key.LEFT:
            cobra.direcao = (-1,0)
        elif simbolo == key.DOWN:
            cobra.direcao = (0,1)
        elif simbolo == key.UP:
            cobra.direcao = (0,-1)
        if simbolo == key.ESCAPE:
            self.close()
        if self.jogo_acabou and simbolo == key.SPACE:
            self.inicializa_jogo()

    def comeu_maca(self, pos):
        self.sons["comeu_maca"].play()
        self.pontos += 1
        pyglet.clock.schedule_once(self.nova_maca, 1)
        #self.nova_maca()
        self.cobra.aumentando += 4

    def nova_maca(self, relogio = 0):
        pos = (0,0)
        while (self.mapa[pos] != VAZIO):
            pos = (randrange(self.mapa.largura),
                   randrange (self.mapa.altura))
        self.sons["maca_aparece"].play()
        self.mapa[pos] = MACA

game = Game(800,600)
pyglet.app.run()