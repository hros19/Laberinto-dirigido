import pygame

MUSICA_PATH = "./programa/multimedia/musica_fondo.mp3"
pygame.mixer.init()

musica_encendida = True

def reproducir_musica():
    pygame.mixer.music.load(MUSICA_PATH)
    pygame.mixer.music.play(-1)
        
def pausar_musica():
    pygame.mixer.music.pause()
    
def continuar_musica():
    pygame.mixer.music.unpause()