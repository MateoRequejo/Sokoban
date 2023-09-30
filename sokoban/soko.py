PARED = "#"
CAJA = "$"
JUGADOR = "@"
OBJETIVO = "."
OBJETIVO_MAS_CAJA = "*"
OBJETIVO_MAS_JUGADOR = "+"

def crear_grilla(desc):
    '''Crea una grilla a partir de la descripción del estado inicial.

    La descripción es una lista de cadenas, cada cadena representa una
    fila y cada caracter una celda. Los caracteres pueden ser los siguientes:

    Caracter  Contenido de la celda
    --------  ---------------------
           #  Pared
           $  Caja
           @  Jugador
           .  Objetivo
           *  Objetivo + Caja
           +  Objetivo + Jugador

    Ejemplo:

    >>> crear_grilla([
        '#####',
        '#.$ #',
        '#@  #',
        '#####',
    ])
    '''
    # Devuelve lista de listas de filas
    grilla = []
    for elemento in desc:
        grilla.append(list(elemento))
    return grilla


def dimensiones(grilla):
    '''Devuelve una tupla con la cantidad de columnas y filas de la grilla.'''
    return (len(grilla[0]), len(grilla))


def hay_pared(grilla, c, f):
    '''Devuelve True si hay una pared en la columna y fila (c, f).'''
    return grilla[f][c] == PARED


def hay_objetivo(grilla, c, f):
    '''Devuelve True si hay un objetivo en la columna y fila (c, f).'''
    return grilla[f][c] == OBJETIVO or grilla[f][c] == OBJETIVO_MAS_JUGADOR or grilla[f][c] == OBJETIVO_MAS_CAJA


def hay_caja(grilla, c, f):
    '''Devuelve True si hay una caja en la columna y fila (c, f).'''
    return grilla[f][c] == CAJA or grilla[f][c] == OBJETIVO_MAS_CAJA


def hay_jugador(grilla, c, f):
    '''Devuelve True si el jugador está en la columna y fila (c, f).'''
    return grilla[f][c] == JUGADOR or grilla[f][c] == OBJETIVO_MAS_JUGADOR


def juego_ganado(grilla):
    '''Devuelve True si el juego está ganado.'''

    # Si se encuentra un objetivo, o un objetivo+jugador, el juego no está ganado
    for fila in grilla:
        if OBJETIVO in fila or OBJETIVO_MAS_JUGADOR in fila:
            return False
    return True


def posicion_jugador(grilla):
    """Recibe una grilla y devuelve las coordenadas (columna, fila) del jugador"""

    for f in range(len(grilla)):
        for c in range(len(grilla[0])):
            if grilla[f][c] == JUGADOR or grilla[f][c] == OBJETIVO_MAS_JUGADOR:
                return (c, f)


def es_valido(grilla, direccion):
    """Devuelve True si el movimiento que se quiere efectuar es válido"""
    
    direccion_columnas, direccion_filas = direccion
    columna_jugador, fila_jugador = posicion_jugador(grilla)

    #Si la direccion es norte o sur, solo se mueve en las filas (direccion_columnas = 0)
    #Si la direccion es este u oeste, solo se mueve en las columnas (direccion_filas = 0)

    # El movimiento es valido si la celda vecina al jugador está vacía, o si hay una caja y la celda
    # vecina a la misma está vacía o es un objetivo vacío
    if not hay_pared(grilla, columna_jugador + direccion_columnas, fila_jugador + direccion_filas):
        if not hay_caja(grilla, columna_jugador + direccion_columnas, fila_jugador + direccion_filas):
            return True
        else:
            return grilla[fila_jugador + direccion_filas*2][columna_jugador + direccion_columnas*2] == " " or \
            grilla[fila_jugador + direccion_filas*2][columna_jugador + direccion_columnas*2] == OBJETIVO
    return False

def movimientos_posibles(grilla):
    """Dada una grilla, devuelve una lista de tuplas con los movimientos
    válidos que se pueden realizar"""
    acciones_posibles = [(1,0),(-1,0),(0,1),(0,-1)]
    resultado = []
    for accion in acciones_posibles:
        if es_valido(grilla, accion):
            resultado.append(accion)
    return resultado

def mover(grilla, direccion):
    '''Mueve el jugador en la dirección indicada.

    La dirección es una tupla con el movimiento horizontal y vertical. Dado que
    no se permite el movimiento diagonal, la dirección puede ser una de cuatro
    posibilidades:

    direccion  significado
    ---------  -----------
    (-1, 0)    Oeste
    (1, 0)     Este
    (0, -1)    Norte
    (0, 1)     Sur

    La función debe devolver una grilla representando el estado siguiente al
    movimiento efectuado. La grilla recibida NO se modifica; es decir, en caso
    de que el movimiento sea válido, la función devuelve una nueva grilla.
    '''
    #Clona la grilla ingresada por parámetro
    nueva_grilla = []
    for i in range(len(grilla)):
        nueva_grilla.append(grilla[i].copy())
    
    #Devuelve la grilla sin modificar si no es válido el movimiento
    if not es_valido(nueva_grilla, direccion):
        return nueva_grilla
    
    direccion_columnas, direccion_filas = direccion
    columna_jugador, fila_jugador = posicion_jugador(nueva_grilla)

    # El jugador sí o sí se mueve (Porque pasó la validación de movimiento). Dejará vacía 
    # la celda en la que estaba, o en todo caso, "." si estaba sobre un objetivo ("+")
    if nueva_grilla[fila_jugador][columna_jugador] == OBJETIVO_MAS_JUGADOR:
            nueva_grilla[fila_jugador][columna_jugador] = OBJETIVO
    else:
            nueva_grilla[fila_jugador][columna_jugador] = " "
    
    #Si en la celda vecina hay caja, analiza qué pasa con las celdas vecinas a la caja:
    if hay_caja(nueva_grilla, columna_jugador + direccion_columnas, fila_jugador + direccion_filas):
        if nueva_grilla [fila_jugador + direccion_filas*2] [columna_jugador + direccion_columnas*2] == OBJETIVO:
            nueva_grilla [fila_jugador + direccion_filas*2] [columna_jugador + direccion_columnas*2] = OBJETIVO_MAS_CAJA
        else:
            nueva_grilla [fila_jugador + direccion_filas*2] [columna_jugador + direccion_columnas*2] = CAJA
    #Si en la celda vecina hay objetivo:
    if hay_objetivo(nueva_grilla, columna_jugador + direccion_columnas, fila_jugador + direccion_filas):
        nueva_grilla [fila_jugador + direccion_filas] [columna_jugador + direccion_columnas] = OBJETIVO_MAS_JUGADOR
    #Si no hay objetivo ni caja:
    else:
        nueva_grilla [fila_jugador + direccion_filas] [columna_jugador + direccion_columnas] = JUGADOR

    return nueva_grilla