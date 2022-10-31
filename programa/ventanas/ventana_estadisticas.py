import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import ventanas.ventana_principal as vp

from modelos.dao_partidas_json import DaoPartidasJson
from ventanas.ventana_repeticion import VentanaRepeticion
class VentanaEstadisticas:
  """Ventana para mostrar estadísticas de juego
  """
  
  def __init__(self):
    self.ventana = tk.Tk()
    self.ventana.title('Estadísticas')
    self.ventana.resizable(False, False)
    self.ventana.eval('tk::PlaceWindow . center')
    self.ventana.geometry('{}x{}+{}+{}'.format(
      900, 650,
      self.ventana.winfo_screenwidth() // 2 - 900 // 2,
      self.ventana.winfo_screenheight() // 2 - 650 // 2 - 50
    ))
    
    # Frame principal
    self.frame = tk.Frame(self.ventana, bg = 'black')
    self.frame.place(
      x = 0, y = 0, width = 900, height = 650
    )
    
    self.frame_tree = tk.Frame(self.frame, bg = 'black')
    self.frame_tree.place(
      x = 0, y = 0, width = 900, height = 475
    )
    
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
    self.btn_volver.place(x = 270, y = 550)
    
    #Botón para mostrar repeticion
    self.btn_volver = tk.Button(
      self.frame,
      bg='blue',
      fg='white',
      width=18,
      font=('Arial', 15),
      text='Mostrar Repeticion',
      command=lambda: self.mostrar_repeticion()
    )
    self.btn_volver.place(x = 480, y = 550)
    
    # Create Treeview with 7 columns and scrollbars
    self.tree = ttk.Treeview(
      self.frame_tree,
      columns=(1,2,3,4,5,6,7),
      show="headings",
      height="20",
    )
    self.tree.place(x = 0, y = 50)

    self.vsb = ttk.Scrollbar(
      self.frame_tree,
      orient="vertical",
      command=self.tree.yview,
    )
    
    self.tree.configure(yscrollcommand=self.vsb.set)
    
    self.tree.bind("<Button-1>", self.onClick)

    self.vsb.pack(side='right', fill='y')

    # Define column headings
    self.tree.heading(1, text="Usuario")
    self.tree.heading(2, text="Matriz")
    self.tree.heading(3, text="Estado")
    self.tree.heading(4, text="Tiempo")
    self.tree.heading(5, text="Movimientos")
    self.tree.heading(6, text="Sugerencias")
    self.tree.heading(7, text="Fecha")

    # Define column widths
    self.tree.column(1, width=140, anchor='center')
    self.tree.column(2, width=170, anchor='center')
    self.tree.column(3, width=100, anchor='center')
    self.tree.column(4, width=110, anchor='center')
    self.tree.column(5, width=100, anchor='center')
    self.tree.column(6, width=100, anchor='center')
    self.tree.column(7, width=162, anchor='center')

    dao_partidas = DaoPartidasJson()
    # Insert data
    partidas = dao_partidas.obtener_partidas()
    
    for partida in partidas:
      self.tree.insert(
        "",
        "end",
        values=(
          partida['jugador'],
          partida['matriz'],
          partida['estado'],
          partida['tiempo'],
          len(partida['movimientos']),
          partida['cantSugerencias'],
          partida['fecha']
        )
      )
    self.ventana.mainloop()
  
  def mostrar_repeticion(self):
    if (self.tree.focus() != ''):
      # Se pasa el valor a entero
      fil = int(self.tree.focus().split('I')[1], 16) - 1
      
      dao = DaoPartidasJson()
      partidas = dao.obtener_partidas()
      self.ventana.quit()
      self.ventana.destroy()
      vtn_repeticion = VentanaRepeticion(partidas[fil])
    else:
      messagebox.showinfo(
        "Error",
        "Debe seleccionar una partida para mostrar la repeticion"
      )
  
  def volver_vtn_principal(self):
    self.ventana.quit()
    self.ventana.destroy()
    vtn = vp.VentanaPrincipal()
  
  def onClick(self, event):
    if self.tree.identify_region(event.x, event.y) == "separator":
      return "break"
    