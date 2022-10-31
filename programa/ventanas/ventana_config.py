import tkinter as tk
import os
from tkinter import ttk, messagebox

import ventanas.ventana_principal as vp
from modelos.juego import Juego

class VentanaConfig:
  """Ventana de configuración previo al juego.
     En esta ventana se podrá elegir el laberinto y el usuario
  """
  
  def __init__(self):
    self.ventana = tk.Tk()
    self.ventana.title('Configuración')
    self.ventana.resizable(False, False)
    self.ventana.geometry('{}x{}+{}+{}'.format(
      700, 500,
      self.ventana.winfo_screenwidth() // 2 - 700 // 2,
      self.ventana.winfo_screenheight() // 2 - 500 // 2 - 50
    ))
    
    # Frame para la ventana
    self.frame = tk.Frame(self.ventana, bg = 'black')
    self.frame.place(
      x = 0, y = 0, width = 700, height = 500
    )
    
    # Label para nombre de usuario
    self.lbl_nombre_usuario = tk.Label(
      self.frame,
      text='Nombre de usuario',
      anchor='w',
      justify='right',
      bg='black',
      fg='white',
      width=18,
      font=('Arial', 15)
    )
    self.lbl_nombre_usuario.place(x = 50, y = 100)
    
    # Entry para el nombre de usuario
    self.ent_nombre_usuario = tk.Entry(
      self.frame,
      width=54,
      bg='white',
      fg='black',
      font=('Arial', 15)
    )
    self.ent_nombre_usuario.place(x = 50, y = 150)
    
    # Label para elegir la matriz
    self.lbl_elegir_matriz = tk.Label(
      self.frame,
      text='Elegir matriz',
      anchor='w',
      justify='right',
      bg='black',
      fg='white',
      width=18,
      font=('Arial', 15)
    )
    self.lbl_elegir_matriz.place(x = 50, y = 200)
    
    # Combo para elegir la matriz
    self.cmb_elegir_matriz = ttk.Combobox(
      self.frame,
      width=52,
      font=('Arial', 15),
      state='readonly',
      values=self.obtener_matrices()
    )
    self.cmb_elegir_matriz.place(x = 50, y = 250)
    
    #Botón para volver a la ventana principal
    self.btn_volver = tk.Button(
      self.frame,
      bg='red',
      fg='white',
      width=18,
      font=('Arial', 15),
      text='Volver',
      command=lambda: self.volver_vtn_principal()
    )
    self.btn_volver.place(x = 50, y = 350)
    
    #Botón para jugar 
    self.btn_jugar = tk.Button(
      self.frame,
      bg='green',
      fg='white',
      width=18,
      font=('Arial', 15),
      text='Jugar',
      command=lambda: self.empezar_juego()
    )
    self.btn_jugar.place(x = 440, y = 350)
    
    self.ventana.mainloop()
  
  def empezar_juego(self):
    """Comienza el juego validando el nombre de usuario y cargando la matriz elegida.
    """
    if (not self.nombre_valido(self.ent_nombre_usuario.get())):
      return
    if (self.cmb_elegir_matriz.get() == ''):
      messagebox.showerror(
        'Error',
        'Debe elegir una matriz'
      )
      return
    
    ruta_matriz = (
      "./matrices/" +
      self.cmb_elegir_matriz.get()
    )
    
    nombre_usuario = self.ent_nombre_usuario.get()
    
    # Se cierra ventana actual
    self.ventana.quit()
    self.ventana.destroy()
    
    juego = Juego(nombre_usuario, ruta_matriz)
    
  def nombre_valido(self, nombre):
    """Valida que un string sea un nombre válido

    Args:
        nombre (string): Nombre cualquiera

    Returns:
        bool: True si tiene mas de 3 caracteres y es alfanumerico, False si no
    """
    if (len(nombre) < 4):
      messagebox.showerror(
        "Error",
        "El nombre debe tener al menos 4 caracteres"
      )
      return False
    if (not nombre.isalpha()):
      messagebox.showerror(
        "Error",
        "El nombre debe ser alfabético"
      )
      return False
    return True
  
  def volver_vtn_principal(self):
    self.ventana.quit()
    self.ventana.destroy()
    vtn = vp.VentanaPrincipal()
  
  def obtener_matrices(self):
    """Obtiene las matrices disponibles en la carpeta matrices
    
    Returns:
        list: Lista con los nombres de las matrices
    """
    matrices = []
    
    ruta = (os.getcwd() + "/programa/matrices/")
    
    for matriz in os.listdir(ruta):
      matrices.append(matriz)
    
    return matrices
    