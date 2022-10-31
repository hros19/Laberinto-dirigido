# Módulos de terceros
import tkinter as tk
import os
import time
from PIL import Image, ImageTk, ImageSequence
from ventanas.ventana_estadisticas import VentanaEstadisticas

# Módulos propios
from ventanas.ventana_config import VentanaConfig

class VentanaPrincipal:
  """Ventana de inicio de la aplicación con el menú principal
  """
  
  PATH_FONDO_ANIMADO = (os.getcwd() + "./programa/multimedia/fondo_animado.gif")
  ventana_activa = True
    
  def __init__(self):
    # Propiedades de la ventana
    self.ventana = tk.Tk()
    self.ventana.title('Laberinto')
    self.ventana.resizable(False, False)
    self.ventana.eval('tk::PlaceWindow . center')
    self.ventana.geometry('{}x{}+{}+{}'.format(
      900, 900,
      self.ventana.winfo_screenwidth() // 2 - 900 // 2,
      self.ventana.winfo_screenheight() // 2 - 900 // 2 - 50
    ))
    
    # Background animado - gif
    self.gif_label = tk.Label(self.ventana, bg = 'black')
    self.gif_label.place(x = 0, y = 0)
    
    # Botón para iniciar el juego
    self.btn_iniciar = tk.Button(
      self.ventana,
      bg='black',
      fg='white',
      width=18,
      font=('Arial', 15),
      text='Jugar',
      command=lambda: self.abrir_ventana_config()
    )
    self.btn_iniciar.place(x = 645, y = 450)
    
    self.btn_estadisticas = tk.Button(
      self.ventana,
      bg='black',
      fg='white',
      width=18,
      font=('Arial', 15),
      text='Partidas',
      command=lambda: self.abrir_ventana_estadisticas()
    )
    self.btn_estadisticas.place(x = 645, y = 500)
    
    # Botón para salir de la aplicación
    self.btn_salir = tk.Button(
      self.ventana,
      bg='red',
      fg='white',
      width=18,
      font=('Arial', 15),
      text='Salir',
      command=lambda: self.cerrar_ventana()
    )
    self.btn_salir.place(x = 645, y = 550)
    
    self.animar_background()
    self.ventana.mainloop()
  
  def abrir_ventana_estadisticas(self):
    self.ventana_activa = False
    self.ventana.quit()
    self.ventana.destroy()
    vent_est = VentanaEstadisticas()
  
  def abrir_ventana_config(self):
    self.ventana_activa = False
    self.ventana.quit()
    self.ventana.destroy()
    vent_config = VentanaConfig()
    
  def cerrar_ventana(self):
    self.ventana_activa = False
    self.ventana.quit()
    self.ventana.destroy()

  def animar_background(self):
    gif_media = Image.open(self.PATH_FONDO_ANIMADO)
    
    for frame in ImageSequence.Iterator(gif_media):
      if (self.ventana_activa):    
        frame = frame.resize((900, 900))
        frame_nuevo = ImageTk.PhotoImage(frame)
        self.gif_label.configure(image = frame_nuevo)
        self.ventana.update()
        time.sleep(0.05)
      else:
        self.ventana.after_cancel(self.animar_background)
        return
    self.ventana.after(1, self.animar_background())
    
    