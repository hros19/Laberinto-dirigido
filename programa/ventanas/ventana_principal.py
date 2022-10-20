# Módulos de terceros
import tkinter as tk
import time
from PIL import Image, ImageTk, ImageSequence

# Módulos propios
import modelos.reproductor as AudioManager

class VentanaPrincipal:
    PATH_FONDO_ANIMADO = "./programa/multimedia/fondo_animado.gif"
    PATH_IMG_AUDIO_ON = "./programa/multimedia/audio_encendido.png"
    PATH_IMG_AUDIO_OFF = "./programa/multimedia/audio_apagado.png"
    
    def __init__(self):
        # Iniciar la musica
        AudioManager.reproducir_musica()
        
        # Propiedades de la ventana
        self.ventana = tk.Tk()
        self.ventana.title('Laberinto')
        self.ventana.geometry('900x900')
        self.ventana.resizable(False, False)
        
        # Background animado - gif
        self.gif_label = tk.Label(self.ventana, bg = 'black')
        self.gif_label.place(x = 0, y = 0)
        
        # Imagen de audio
        self.IMG_AUDIO_ON = tk.PhotoImage(file = self.PATH_IMG_AUDIO_ON).subsample(7, 6)
        self.IMG_AUDIO_OFF = tk.PhotoImage(file = self.PATH_IMG_AUDIO_OFF).subsample(7, 6)
        
        # Botón de pausa
        self.btn_musica = tk.Button(
            self.ventana, 
            text = 'Pausar',
            width = 120,
            height = 100,
            image = self.IMG_AUDIO_ON,
            command = lambda: self.alternar_musica(),
            bg = 'light blue',
            highlightcolor = 'white',
            relief = tk.GROOVE,
            compound = tk.TOP
        )
        self.btn_musica.place(x = 25, y = 25)
        
        self.animar_background()
    
    def animar_background(self):
        gif_media = Image.open(self.PATH_FONDO_ANIMADO)
        
        for frame in ImageSequence.Iterator(gif_media):
            frame = frame.resize((900, 900))
            frame_nuevo = ImageTk.PhotoImage(frame)
            self.gif_label.configure(image = frame_nuevo)
            self.ventana.update()
            time.sleep(0.05)
        self.ventana.after(0, self.animar_background())
        
    def alternar_musica(self):
        # Se alterna la música y se cambia el texto e imagen del botón
        if (AudioManager.musica_encendida):
            AudioManager.pausar_musica()
            self.btn_musica.configure(
                text = 'Reproducir',
                image = self.IMG_AUDIO_OFF,
                command = lambda: self.alternar_musica(),
                compound = tk.TOP
            )
            AudioManager.musica_encendida = False
            
        else:
            AudioManager.continuar_musica()
            self.btn_musica.configure(
                text = 'Pausar',
                image = self.IMG_AUDIO_ON,
                compound = tk.TOP
            )
            AudioManager.musica_encendida = True
