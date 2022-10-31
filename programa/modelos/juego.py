'''
Módulo: juego.py
Clase: Juego
Descripción: Clase principal para la gestión del juego de laberinto
Autor: Hansol Antay Rostrán
Fecha de creación: 27 de octubre, 2022
'''
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from modelos.dao_partidas_json import DaoPartidasJson
from modelos.consultor import Consultor
import ventanas.ventana_config as vc

class Juego:
  """Clase juego para el laberinto
  """
  def __init__(self, nombre_usuario, ruta_matriz):
    self.nombre_usuario = nombre_usuario
    self.ruta_matriz = ruta_matriz
    
    self.ventana = tk.Tk()
    self.ventana.title('Juego')
    self.ventana.resizable(False, False)
    self.ventana.geometry('{}x{}+{}+{}'.format(
      1000, 700,
      self.ventana.winfo_screenwidth() // 2 - 1000 // 2,
      self.ventana.winfo_screenheight() // 2 - 700 // 2 - 50
    ))
    self.ventana.bind('<KeyPress>', self.mover)
    
    self.estado = "Jugando"
    self.movimientos = []
    self.cant_sugerencias = 0
    
    # Frame para la ventana
    self.frame = tk.Frame(self.ventana, bg = 'light sky blue')
    self.frame.place(
      x = 0, y = 0, width = 1000, height = 700
    )
    
    # Frame para la matriz
    self.frame_matriz = tk.Frame(self.frame, bg = 'RoyalBlue2')
    
    # Botones
    self.btn_abandono = tk.Button(
      self.frame,
      width=20,
      height=2,
      text="Reiniciar",
      font=('Arial', 15, 'bold'),
      bg='red',
      fg='white',
      command=lambda: self.abandonar()
    )
    self.btn_abandono.place(
      x = 708, y = 150
    )
    
    self.btn_verificar = tk.Button(
      self.frame,
      width=20,
      height=2,
      text="Verificar",
      font=('Arial', 15, 'bold'),
      bg='dark blue',
      fg='white',
      command=lambda: self.verificar_posicion_actual()
    )
    self.btn_verificar.place(
      x = 708, y = 250
    )
    
    self.btn_sugerencia = tk.Button(
      self.frame,
      width=20,
      height=2,
      text="Pedir Sugerencia",
      font=('Arial', 15, 'bold'),
      bg='dark blue',
      fg='white',
      command=lambda: self.mostrar_sugerencias()
    )
    self.btn_sugerencia.place(
      x = 708, y = 350
    )
    
    self.btn_mostrar_solucion = tk.Button(
      self.frame,
      width=20,
      height=2,
      text="Mostrar Solución",
      font=('Arial', 15, 'bold'),
      bg='dark blue',
      fg='white',
      command=lambda: self.mostrar_solucion_gui()
    )
    self.btn_mostrar_solucion.place(
      x = 708, y = 450
    )
    
    self.cargar_matriz_y_solucion()
    self.mostrar_laberinto_gui()
    self.mostrar_cronometro_gui()
    
    self.ventana.mainloop()

  def mostrar_sugerencias(self):
    """Muestra las sugerencias de la posición actual y las muestra en el laberinto
    """
    sugerencias = self.cprolog.pedir_sugerencia(self.pos_actual)
    
    if sugerencias == []:
      messagebox.showinfo(
        "No hay sugerencias",
        "No hay sugerencias disponibles"
      )
    else:
      self.mostrar_sugerencias_gui(sugerencias)
  
  def mostrar_sugerencias_gui(self, sugerencias):
    """Muestra la lista de sugerencia (tuplas) en el laberinto

    Args:
        sugerencias (list<tuple>): lista de posición (x, y) de las sugerencias
    """
    
    if self.cant_sugerencias < 10:
      for posicion in sugerencias:
        i = posicion[0] * self.cant_col + posicion[1]
        self.btns_matriz[i][2].config(bg='pink')
        self.cant_sugerencias += 1
    else:
      messagebox.showinfo(
        "No hay sugerencias",
        "Ya no puede pedir más sugerencias"
      )
  
  def abandonar(self):
    """Efectua un abandono del juego, se reinicia con la misma matriz
    """
    
    dao = DaoPartidasJson()
    self.estado = "Abandonado"
    partida = {
      "jugador": self.nombre_usuario,
      "matriz": self.ruta_matriz,
      "estado": self.estado,
      "movimientos": self.movimientos,
      "tiempo": self.cronometro['text'],
      "cantSugerencias": self.cant_sugerencias,
      "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    
    partidas = dao.obtener_partidas()
    partidas.append(partida)
    dao.guardar_partidas(partidas)
    
    self.cprolog.cerrar_consultor()
    
    # Se destruye la ventana actual luego de crear un nuevo juego con los mismos parametros
    self.cronometro.after_cancel(self.actualizar_cronometro)
    self.ventana.destroy()
    self.nuevo_juego(self.nombre_usuario, self.ruta_matriz)
  
  def nuevo_juego(self, nombre_usuario, ruta_matriz):
    """Crea un nuevo juego con los parametros dados

    Args:
        nombre_usuario (string): nombre del usuario
        ruta_matriz (string): ruta de la matriz
    """
    Juego(nombre_usuario, ruta_matriz)
  
  def verificar_posicion_actual(self):
    """Verifica si la posicion actual es parte de la solucion
    """
    
    if self.cprolog.es_parte_solucion(self.pos_actual):
      messagebox.showinfo(
        "Es parte de la solución",
        "La posición actual es parte de la solución"
      )
    else:
      messagebox.showinfo(
        "No es parte de la solución",
        "La posición actual no es parte de la solución"
      )
  
  def mostrar_cronometro_gui(self):
    """Muestra el cronometro en la ventana e inicia el cronometro
    """
    
    self.cronometro = tk.Label(
      self.frame,
      text='00:00:00',
      font=('Arial', 20, 'bold'),
      bg='white',
      fg='black'
    )
    self.cronometro.place(
      x = 800, y = 50
    )
    self.iniciar_cronometro()
  
  def iniciar_cronometro(self):
    """Inicializa el cronometro y lo actualiza cada segundo
    """
    self.segundos = 0
    self.minutos = 0
    self.horas = 0
    self.cronometro.after(1000, self.actualizar_cronometro)
  
  def actualizar_cronometro(self):
    """Actualiza el cronometro cada segundo
    """
    if self.estado == "Jugando":
      self.segundos += 1
      if (self.segundos == 60):
        self.segundos = 0
        self.minutos += 1
      if (self.minutos == 60):
        self.minutos = 0
        self.horas += 1
      self.cronometro.config(
        text='{0:02d}:{1:02d}:{2:02d}'.format(self.horas, self.minutos, self.segundos)
      )
      self.cronometro.after(1000, self.actualizar_cronometro)
  
  def cargar_matriz_y_solucion(self):
    """Carga la matriz y la solución desde prolog
    """
    self.cprolog = Consultor()
    self.matriz = self.cprolog.definir_valores_iniciales(self.ruta_matriz)
    self.cprolog.solucionar()
    self.solucion = self.cprolog.get_camino_solucion()
    
    self.cant_fil = len(self.matriz)
    self.cant_col = len(self.matriz[0])
  
  def mostrar_laberinto_gui(self):
    """Se muestra el laberinto en la ventana
    """
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
      in_=self.frame, anchor='c', relx=.35, rely=.5
    )
  
  def mostrar_solucion_gui(self):
    """Se muestra la solución en la ventana y se guarda la partida
    """
    for fil in range (0, self.cant_fil):
      for col in range (0, self.cant_col):
        if ((fil, col) in self.solucion and 
            self.matriz[fil][col] != 'i' and
            self.matriz[fil][col] != 'f'):
          self.btns_matriz[fil * self.cant_col + col][2].config(
            bg='light goldenrod'
          )
    self.mostrar_posiciones_limitantes_gui()
    self.estado = "AutoSolucionado"
    self.registrar_partida()
    
    self.cprolog.cerrar_consultor()
    
    self.cronometro.after_cancel(self.actualizar_cronometro)
    
    messagebox.showinfo(
      "AutoSolucionado",
      "El laberinto se ha resuelto automáticamente, presione OK para volver al menú de configuración"
    )
    self.ventana.after(
      1050,
      self.ventana.destroy()
    )
    vc.VentanaConfig()
  
  def mostrar_posiciones_limitantes_gui(self):
    """Se muestra las posiciones limitantes en la ventana
    """
    json_posiciones = self.cprolog.pthread.query('posicion_borrada(X)')
    for obj in json_posiciones:
      pos = (int(obj['X']['args'][0]), int(obj['X']['args'][1]))
      self.btns_matriz[pos[0] * self.cant_col + pos[1]][2].config(
        bg='red'
      )
  
  def mover(self, event):
    """Captura el evento de tecla presionada y realiza el movimiento

    Args:
        event (any): Evento de tecla presionada
    """
    posicion_destino = (-1, -1)
    if event.keysym == 'Up':
      # Verificar que no se salga del laberinto
      if self.pos_actual[0] - 1 >= 0:
        posicion_destino = (self.pos_actual[0] - 1, self.pos_actual[1])
    elif event.keysym == 'Down':
      if self.pos_actual[0] + 1 < self.cant_fil:
        posicion_destino = (self.pos_actual[0] + 1, self.pos_actual[1])
    elif event.keysym == 'Left':
      if self.pos_actual[1] - 1 >= 0:
        posicion_destino = (self.pos_actual[0], self.pos_actual[1] - 1)
    elif event.keysym == 'Right':
      if self.pos_actual[1] + 1 < self.cant_col:
        posicion_destino = (self.pos_actual[0], self.pos_actual[1] + 1)
    
    if (self.cprolog.es_movimiento_valido(self.pos_actual, posicion_destino)):
      # Pintando posición anterior
      if (self.pos_actual != self.pos_ini):
        self.btns_matriz[self.pos_actual[0] * self.cant_col + self.pos_actual[1]][2].config(
          bg='PaleGreen1'
        )
      # Pintando nueva posición
      self.btns_matriz[posicion_destino[0] * self.cant_col + posicion_destino[1]][2].config(
        bg='green4'
      )
      self.movimientos.append(posicion_destino)
      self.pos_actual = posicion_destino
      if (posicion_destino == self.pos_fin):
        messagebox.showinfo(
          'Mensaje', '¡Felicidades, has completado el laberinto!'
        )
        self.estado = "Exitoso"
        self.registrar_partida()
        self.cprolog.cerrar_consultor()
        
        self.ventana.after(
          1050,
          self.ventana.destroy()
        )
        vc.VentanaConfig()
        
  def registrar_partida(self):
    """Registra la partida en el archivo
    """
    
    dao = DaoPartidasJson()
    
    partida = {
      "jugador": self.nombre_usuario,
      "matriz": self.ruta_matriz,
      "estado": self.estado,
      "movimientos": self.movimientos,
      "tiempo": self.cronometro['text'],
      "cantSugerencias": self.cant_sugerencias,
      "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    
    partidas = dao.obtener_partidas()
    partidas.append(partida)
    dao.guardar_partidas(partidas)
    
    