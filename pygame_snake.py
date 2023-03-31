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


#Authors:  João S. O. Bueno

import pygame
from copy import copy
from random import randrange

import snake
from snake import PAREDE, VAZIO, COBRA_CORPO, COBRA_CABECA, COBRA_CAUDA, MACA

TELA = None #variável global, mantendo a superficie da Tela do jogo

class GameMapa(snake.Mapa):
    def __init__(self, janela, largura, altura):
        self.janela = janela
        snake.Mapa.__init__(self, largura, altura)
        self.larg_celula = janela.width // self.largura
        self.alt_celula = janela.height // self.altura
        self.carrega_imagens()
        self.mapa_anterior = snake.Mapa(largura,altura)
        self.counter = 0
    def carrega_imagens(self):
        l = pygame.image.load
        self.imagens = {PAREDE: l("parede.png"),
                        VAZIO: l("quadrado_preto.png"),
                        COBRA_CORPO: l("esfera_1.png"),
                        COBRA_CABECA: l("esfera_2.png"),
                        COBRA_CAUDA: l("esfera_1.png"),
                        MACA: l("esfera_2.png")
                       }

    def mantem_mapa_anterior(self):
        self.mapa_anterior.data = copy(self.data)

    def desenha(self):
        for y in range(self.altura):
            for x in range(self.largura):
                if self.counter != 0 and self[x, y] == self.mapa_anterior[x, y]:
                    continue
                imagem = self.imagens[self[x,y]]
                i_x = x * self.larg_celula
                i_y =  y  * self.alt_celula
                TELA.blit(imagem, (i_x, i_y))
        self.mantem_mapa_anterior()
        self.counter += 1

class Game(object):
    def __init__(self, largura, altura, *args, **kwargs):
        global TELA
        TELA = pygame.display.set_mode((largura,altura))
        self.width = self.largura = largura
        self.height = self.altura = altura
        self.carrega_sons()
        self.inicializa_jogo()

    def laco_principal(self):
        while True:
            pygame.time.wait(50)
            eventos = self.agenda.keys()
            while (self.agenda and pygame.time.get_ticks() > min(self.agenda.keys())):
                chave_evento = min(self.agenda.keys())
                self.agenda[chave_evento]()
                del self.agenda[chave_evento]
            pygame.event.pump ()
            eventos = pygame.event.get()
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    self.on_key_press(evento.key)
            self.atualiza()

    def inicializa_jogo(self):
        self.mapa = snake.mapa_0(GameMapa, self, 40, 30)
        self.cobra = snake.Cobra((5,2), (1,0), 2, 4, self.mapa)
        self.cobra.chama_maca = self.comeu_maca
        self.pontos = 0
        self.jogo_acabou = False
        self.nova_maca()
        self.contador = 0
        self.agenda = {}

    def carrega_sons(self):

        self.sons = {"maca_aparece": "pop.wav",
                     "comeu_maca": "KDE_Beep_Bottles.wav",
                     "morreu": "KDE_Critical_Error.wav"}
        class Som(object):
            def __init__(self, arquivo):
                self.som = pygame.mixer.Sound(arquivo)
                self.num_canais = pygame.mixer.get_num_channels()
                self.canais = []
                for i in range(self.num_canais):
                    self.canais.append(pygame.mixer.find_channel(i))
            def play(self):
                ocupado = pygame.mixer.get_busy()
                c = 0
                while True:
                    if not ocupado % 2:
                        break
                    c += 1
                    ocupado >>= 1
                if c < self.num_canais:
                    self.canais[c].play(self.som)

        for evento, arquivo in self.sons.items():
            self.sons[evento] = Som(arquivo)


    def atualiza(self, relogio=0):
        self.contador += 1
        if not self.jogo_acabou:
            try:
                self.cobra.atualiza()
                self.on_draw()
            except snake.CobraMorreu, morreu:
                self.jogo_acabou = True
                self.sons["morreu"].play()
                self.texto_placar = "%d pontos!" % self.pontos
                self.fonte = pygame.font.Font("FreeSans.ttf", 80)


        else:
            cor = (255, 255, 10 * self.contador % 255)
            imagem_placar = self.fonte.render(self.texto_placar, True, cor)
            TELA.blit(imagem_placar,
                      (self.width // 2 - imagem_placar.get_width() //2,
                       self.height // 2 - imagem_placar.get_height() //2))
        pygame.display.flip()

    def on_draw(self, *args):
        #self.clear()
        self.mapa.desenha()

    def on_key_press(self, simbolo, modificador = 0):
        cobra = self.cobra
        if simbolo == pygame.K_RIGHT:
            cobra.direcao = (1,0)
        elif simbolo == pygame.K_LEFT:
            cobra.direcao = (-1,0)
        elif simbolo == pygame.K_DOWN:
            cobra.direcao = (0,1)
        elif simbolo == pygame.K_UP:
            cobra.direcao = (0,-1)
        if simbolo == pygame.K_ESCAPE:
            self.encerrar()
        if self.jogo_acabou and simbolo == pygame.K_SPACE:
            self.inicializa_jogo()


    def comeu_maca(self, pos):
        self.sons["comeu_maca"].play()
        self.pontos += 1
        self.agenda[pygame.time.get_ticks() + 1000] = self.nova_maca
        #self.nova_maca()
        self.cobra.aumentando += 4

    def nova_maca(self, relogio = 0):
        pos = (0,0)
        while (self.mapa[pos] != VAZIO):
            pos = (randrange(self.mapa.largura),
                   randrange (self.mapa.altura))
        self.sons["maca_aparece"].play()
        self.mapa[pos] = MACA

    def encerrar(self):
        pygame.quit()


pygame.init()
game = Game(800,600)
game.laco_principal()