import tkinter as tk
from tkinter import messagebox

from modelos.consultor import Consultor
import ventanas.ventana_estadisticas as ve

class VentanaRepeticion:
  
  def __init__(self, partida):
    self.partida = partida
    
    self.ventana = tk.Tk()
    self.ventana.title('Juego')
    self.ventana.resizable(False, False)
    self.ventana.geometry('{}x{}+{}+{}'.format(
      900, 700,
      self.ventana.winfo_screenwidth() // 2 - 900 // 2,
      self.ventana.winfo_screenheight() // 2 - 700 // 2 - 50
    ))
    
    # Frame para la ventana
    self.frame = tk.Frame(self.ventana, bg = 'light sky blue')
    self.frame.place(
      x = 0, y = 0, width = 900, height = 700
    )
    
    # Frame para la matriz
    self.frame_matriz = tk.Frame(self.frame, bg = 'RoyalBlue2')
    
    self.cprolog = Consultor()
    self.matriz = self.cprolog.definir_valores_iniciales(self.partida['matriz'])
    self.cant_fil = len(self.matriz)
    self.cant_col = len(self.matriz[0])
    self.cprolog.cerrar_consultor()
    
    self.mostrar_laberinto_gui()
    self.mostrar_repeticion_gui()
    self.ventana.mainloop()
  
  
  def mostrar_repeticion_gui(self):
    movimientos = self.partida['movimientos']
    
    self.frame_matriz.after(500, self.mover_pieza, 0)
    
  def mover_pieza(self, indice):
    movs = self.partida['movimientos']
    if indice < len(movs):
      self.btns_matriz[movs[indice][0] * self.cant_col + movs[indice][1]][2].config(bg='RoyalBlue2')
      self.frame_matriz.update()
      self.frame_matriz.after(500, self.mover_pieza, indice + 1)
    else:
      messagebox.showinfo('Fin', 'Fin de la partida, presione OK para volver a la ventana de partidas')
      self.ventana.after(
        1050,
        self.ventana.destroy()
      )
      ve.VentanaEstadisticas()
 
      
  
  
  def mostrar_laberinto_gui(self):
    self.btns_matriz = []
    for fil in range (0, self.cant_fil):
      for col in range (0, self.cant_col):
        color_celda = ''
        color_texto = 'white'
        if (self.matriz[fil][col] == 'x'):
          color_celda = 'black'
        elif (self.matriz[fil][col] == 'i'):
          self.pos_ini = (fil, col)
          self.pos_actual = self.pos_ini
          color_celda = 'SteelBlue3'
        elif (self.matriz[fil][col] == 'f'):
          self.pos_fin = (fil, col)
          color_celda = 'green3'
        else:
          color_celda = 'white'
          color_texto = 'black'
        button = tk.Button(
          self.frame_matriz,
          text='{}'.format(self.matriz[fil][col]),
          fg=color_texto,
          bg=color_celda,
          relief='flat',
          font=('Arial', 10, 'bold'),
          width=5,
          height=2
        )
        button.grid(row=fil, column=col, padx=1, pady=1)
        self.btns_matriz.append([fil, col, button])
    
    self.frame_matriz.place(
      in_=self.frame, anchor='c', relx=.5, rely=.5
    )