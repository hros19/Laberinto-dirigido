'''
Módulo: dao_partidas_json.py
Clase: DaoPartidasJson
Descripción: Clase que permite gestionar la persistencia de partidas en formato JSON de partidas
Referencia utilizada: https://simplejson.readthedocs.io/en/latest/
'''

import simplejson

class DaoPartidasJson:
  """Dao correspondiente de las partidas jugadas en formato JSON
  """
  
  def __init__(self):
    self.path = './programa/partidas.json'
    
  def partidas_a_json_str(self, partidas):
    """Convierte una lista de partidas a un string en formato JSON.
       El objetivo de esta función es transformar la lista de tuplas
       en una lista de strings para que el JSON pueda ser leído
       de forma más fácil.

    Args:
        partidas (list<Object>): Lista de partidas

    Returns:
        list<Object>: las partidas con un formato correcto para JSON
    """
    
    movimientos_str = []
    for partida in partidas:
      movimientos = partida['movimientos']
      for mov in movimientos:
        tupla_str = ("({}, {})".format(mov[0], mov[1]))
        movimientos_str.append(tupla_str)
      partida['movimientos'] = movimientos_str
      movimientos_str = []
    return simplejson.dumps(partidas, indent=2)
  
  def json_a_partidas(self, partidas):
    """Obtiene una lista de partidas obtenidas de un archivo JSON
       y convierte la lista de strings en una lista de tuplas con las
       posición de los movimientos.
       
    Args:
        partidas (list<Object>): Lista de partidas
    
    Returns:
        list<Object>: Lista de partidas con los movimientos en tuplas
    """
    
    movimientos_tuplas = []
    for partida in partidas:
      movimientos = partida['movimientos']
      for mov in movimientos:
        mov = mov.replace('(', '')
        mov = mov.replace(')', '')
        mov = mov.split(',')
        mov = (int(mov[0]), int(mov[1]))
        movimientos_tuplas.append(mov)
      partida['movimientos'] = movimientos_tuplas
      movimientos_tuplas = []
    return partidas
  
  def obtener_partidas(self):
    """Obtiene las partidas guardadas en el archivo JSON
    
    Returns:
        list<Object>: Lista de partidas
    """
    
    with open(self.path, 'r') as file:
      partidas_json = simplejson.loads(file.read())
      return self.json_a_partidas(partidas_json)
  
  def guardar_partidas(self, partidas):
    """Guarda las partidas en el archivo JSON

    Args:
        partidas (list<Object>): lista de partidas a guardar
    """
    
    with open(self.path, 'w') as file:
      file.write(self.partidas_a_json_str(partidas))

    