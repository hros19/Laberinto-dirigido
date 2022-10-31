'''
Módulo: consultor.py
Clase: Consultor
Descripción: maneja la comunicación con el motor de inferencia Prolog
Autor: Hansol Antay Rostrán
Fecha de creación: 27 de octubre, 2022
'''
from swiplserver import PrologMQI
import os

class Consultor:
  """Permite gestionar llamadas a queries de la base de conocimiento en Prolog
  """
  
  def __init__(self):
    """Constructor principal sin parámetros
    """
    
    self.mqi = PrologMQI()
    self.pthread = self.mqi.create_thread()
    self.set_directorio()
  
  def cerrar_consultor(self):
    """Cierra la conexión con Prolog
    """
    
    self.pthread.halt_server()
    self.mqi.stop()
    
  def set_directorio(self):
    """Define el directorio de trabajo de Prolog
    """
    
    ruta = (
      os.getcwd().replace('\\', '/') +
      "/programa/"
    )
    self.pthread.query(
      'cd("{}")'.format(ruta)
    )

    self.cargar_base_de_conocimiento()
    
  def cargar_base_de_conocimiento(self):
    """Carga la base de conocimiento en Prolog
    """
    
    self.pthread.query(
      'consult("logica.pl")'
    )
    
  def definir_valores_iniciales(self, path):
    """Define la matriz, las posiciones iniciales y finales de la matriz

    Args:
        path (string): La ruta de la matriz para cargar

    Returns:
        list<list>: La matriz con valores decodificados
    """
    
    matriz = self.cargar_matriz(path)
    self.set_posiciones_inic(matriz)
    return matriz
    
  def cargar_matriz(self, path):
    """Carga la matriz desde prolog, se decodifica y se define en la base de conocimiento

    Args:
        path (string): Ruta del archivo con la matriz

    Returns:
        list<list>: Matriz con los valores correctos
    """
    
    # Se carga la matriz desde prolog, pero los valores están en ASCII (numéricos)
    mat_cod = self.pthread.query(
      "phrase_from_file(lines(Ls), {})".format(
        '"' + path + '"'
      )
    )[0]['Ls'] # Matriz codificada (ASCII)
    
    # Se decodifica la matriz, convirtiendo los valores ASCII a caracteres
    mat_dec = [] # Matriz decodificada
    for fila in mat_cod:
      fila_dec = []
      for valor in fila:
        fila_dec.append(chr(valor))
      mat_dec.append(fila_dec)
      
    self.pthread.query(
      'asserta(matriz({}))'.format(mat_dec)
    )
    return mat_dec
  
  def set_posiciones_inic(self, matriz):
    """Define las posiciones iniciales de paredes, de inicio y de fin de la matriz
    y las guarda en la base de conocimiento
    """
    
    posiciones = []
    for i in range(0, len(matriz)):
      for j in range(0, len(matriz[0])):
        if (matriz[i][j] == 'x'):
          posiciones.append((i, j))
          self.pthread.query(
            'assertz(pared({}))'.format((i, j))
          )
        elif (matriz[i][j] == 'i'):
          self.pthread.query(
            'assertz(posicion_inicial({}))'.format((i, j))
          )
          self.pthread.query(
            'assertz(posicion_actual({}))'.format((i, j))
          )
        elif (matriz[i][j] == 'f'):
          self.pthread.query(
            'assertz(posicion_final({}))'.format((i, j))
          )
        else:
          continue
        
  # ========== [ Consultas ] ==========
    
  def get_posiciones_paredes(self):
    """Obtiene las posiciones de las paredes del laberinto

    Returns:
        list<tuple>: Lista de tuplas con las posiciones de las paredes
    """
    
    paredes_json = self.pthread.query(
      'pared(X)'
    )
    
    lista_paredes = []
    for json in paredes_json:
      tupla = (
        int(json['X']['args'][0]),
        int(json['X']['args'][1])
      )
      lista_paredes.append(tupla)
    return lista_paredes 
    
  def get_posicion_inicial(self):
    """Obtiene la posición inicial del laberinto en forma de tupla

    Returns:
        tuple: posicion inicial del laberinto
    """
    pos_json = self.pthread.query(
      'posicion_inicial(X)'
    )[0]['X']
    
    return (
      int(pos_json['args'][0]),
      int(pos_json['args'][1])
    )
    
  def get_posicion_final(self):
    """Regresa la posición final del laberinto en forma de tupla

    Returns:
        tuple: posicion final o meta del laberinto
    """
    
    pos_json = self.pthread.query(
      'posicion_final(X)'
    )[0]['X']
    
    return (
      int(pos_json['args'][0]),
      int(pos_json['args'][1])
    )
    
  def get_cruces_pendientes(self):
    """Retorna la lista de cruces pendientes que quedan por visitar

    Returns:
        list<tuple>: lista con las posiciones de los cruces pendientes
    """
    
    cruces_json = self.pthread.query(
      'obtener_cruces_pendientes(X)'
    )[0]['X']
    
    lista_cruces_pendientes = []
    for json in cruces_json:
      cruce = (
        int(json['args'][0]),
        int(json['args'][1])
      )
      lista_cruces_pendientes.append(cruce)
    
    
    return lista_cruces_pendientes
    
  def get_valor_posicion(self, posicion):
    """Obtiene el valor de la posición indicada

    Args:
        posicion (tuple): Posicion a consultar

    Returns:
        string: Valor de la posición
    """
    
    valor_json = self.pthread.query(
      'obtener_valor_posicion({}, X)'.format(posicion)
    )[0]['X']
    
    return chr(valor_json)
  # ========== [ Logica (Solucion) ] ==========
  
  def solucionar(self):
    """Función principal que resuelve el laberinto desde prolog
    
    Returns:
        boolean: True si se encontró una solución, False si no
        
    Nota: retorna False si el laberinto actual no tiene solución
    """
    self.pthread.query("run") # Movs desde posición inicial
    self.pthread.query("terminar_laberinto")
    
    if (bool(self.pthread.query('llego_a_posicion_final'))):
      self.pthread.query("determinar_camino_solucion")
      self.pthread.query("guardar_camino_solucion")
      self.pthread.query("determinar_cruces_pendientes")
      
      lista_cruces_pendientes = self.get_cruces_pendientes()
      self.encontrar_otros_caminos(lista_cruces_pendientes)
      return True
    else:
      return False
  
  def encontrar_otros_caminos(self, lista_cruces):
    """Recibe una lista de posiciones que son cruces (c) en la matriz
    que quedan pendientes por recorrer de forma completa.

    Args:
        lista_cruces (list<tuple>): lista de cruces a recorrer
    """
    
    for cruce in lista_cruces:
      self.pthread.query('reiniciar_base_de_conocimiento')
      self.pthread.query(
        'jugar_desde({})'.format(cruce)
      )
      self.pthread.query('terminar_laberinto')
      if (bool(self.pthread.query('llego_a_posicion_final'))):
        self.pthread.query("determinar_camino_solucion")
        self.pthread.query("guardar_camino_solucion")
      continue
  
  def get_camino_solucion(self):
    """Retorna el camino solución en forma de lista de tuplas

    Returns:
        list<tuple>: lista de tuplas con las posiciones del camino solución
    """
    
    camino_json = self.pthread.query(
      'obtener_camino_solucion(X)'
    )[0]['X']
    
    lista_camino = []
    for json in camino_json:
      tupla = (
        int(json['args'][0]),
        int(json['args'][1])
      )
      lista_camino.append(tupla)
    return lista_camino
  
  def es_parte_solucion(self, posicion):
    """Consulta si la posición indicada es parte del camino solución

    Args:
        posicion (tuple): Posicion a consultar

    Returns:
        bool: True si es parte del camino solución, False si no
    """
    
    return bool(self.pthread.query(
      'es_parte_solucion({})'.format(posicion)
    ))
    
  def pedir_sugerencia(self, posicion):
    """Solicita una sugerencia de movimiento de una posición en específico.

    Args:
        posicion (tuple): Posicion a consultar la ayuda

    Returns:
        list<tuple>: Lista de tuplas con las posiciones sugeridas
        []: si no hay sugerencias
    """
    
    sugerencia_json = self.pthread.query(
      'obtener_ayuda({}, X)'.format(posicion)
    )
    
    if (bool(sugerencia_json) == False):
      return []
    
    sugerencias = []
    for sug in sugerencia_json:
      sugerencias += [(   
        int(sug['X']['args'][0]),
        int(sug['X']['args'][1])
      )]
    
    return sugerencias
    
  def es_movimiento_valido(self, posicion_inicial, posicion_destino):
    """Verifica que una posicion destino sea un movimiento valido de una posicion inicial

    Args:
        posicion_inicial (tuple): Posicion inicial de la matriz
        posicion_destino (tuple): Posicion destino de la matriz
    
    Returns:
        bool: True, si la posicion destino es un movimiento valido y directo de la posicion inicial
    """
    return bool(
      self.pthread.query(
      'es_movimiento_valido({}, {})'.format(posicion_inicial, posicion_destino)
      )
    )
  