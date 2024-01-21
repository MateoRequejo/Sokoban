import soko
import hola
import gamelib
from cola import Cola
from pila import Pila

ACCIONES = {"NORTE" : (0,-1), "SUR" : (0, 1), "ESTE" : (1, 0), "OESTE" : (-1,0), "REINICIAR" : 1, "SALIR" : -1,
"DESHACER" : 2, "REHACER" : -2, "PISTAS" : 3}

#imagenes
PARED = "img/wall.gif"
PISO = "img/ground.gif"
OBJETIVO = "img/goal.gif"
CAJA = "img/box.gif"
JUGADOR = "img/player.gif"

NIVEL_MAXIMO = 146

#pixeles de las imagenes
PIXELES = 64

def ajustar_descripcion(descripcion):
    """Ajusta la descripcion en caso de que no sea una grilla de dimensiones perfectas"""

    ajustada = []

    #el largo de la grilla será el largo de la fila mas larga
    largo_grilla = 0
    for fila in descripcion:
        if len(fila) > largo_grilla:
            largo_grilla = len(fila)
    
    #recorre la descripcion y si una fila no cumple con el largo de la grilla, le agrega espacios hasta cumplir
    for fila in descripcion:
        if len(fila) != largo_grilla:
            diferencia = largo_grilla - len(fila)
            fila += " " * diferencia
            ajustada.append(fila)
        else:
            ajustada.append(fila)
    return ajustada

def crear_descripcion_niveles(archivo_niveles):
    """Devuelve un diccionario con las descripciones de los niveles (Ajustadas, en caso de que las
    dimensiones no sean perfectas)"""
    descripciones = {}
    with open(archivo_niveles) as archivo:
        for linea in archivo:
            if linea:  #Si la linea no está vacía
                linea = linea.rstrip().split()
                if len(linea) == 2:   # formato "Level X"
                    _, nivel = linea
                    nivel = int(nivel)
                    descripciones[nivel] = []
                    linea = next(archivo).rstrip()
                    if "#" not in linea:    #Saltea la linea del titulo del nivel, en caso de que haya
                        linea = next(archivo).rstrip()
                    while linea:   #mientras la linea no esté vacía, la agrega a la descripcion
                        descripciones[nivel].append(linea)
                        try:
                            linea = next(archivo).rstrip()
                        except StopIteration:  #Atrapa la excepcion al llegar al final del archivo
                            break

                        #ajusta la descripcion en caso de que la dimension de la grilla no sea perfecta
                        descripcion_ajustada = ajustar_descripcion(descripciones[nivel])
                        descripciones[nivel] = descripcion_ajustada
    return descripciones

def dimensiones_ancho_y_alto(juego):
    """Devuelve el ancho y el alto de la ventana dependiendo el tamaño del nivel, y las dimensiones
    de la grilla (filas y columnas)"""
    
    columnas, filas = soko.dimensiones(juego)

    alto_ventana = filas * PIXELES
    ancho_ventana = columnas * PIXELES

    return alto_ventana, ancho_ventana, filas, columnas

def juego_crear(descripciones, nivel):
    """Crea la grilla del juego"""
    descripcion = descripciones[nivel]
    juego = soko.crear_grilla(descripcion)
    return juego

def definir_imagen(juego, fila, columna):
    """dependiendo qué hay en la celda ingresada, devuelve una lista con las imagenes que correspondan"""
    resultado = []
    if soko.hay_caja(juego, columna, fila):
        resultado.append(CAJA)
    if soko.hay_jugador(juego, columna, fila):
        resultado.append(JUGADOR)
    if soko.hay_objetivo(juego, columna, fila):
        resultado.append(OBJETIVO)
    if soko.hay_pared(juego, columna, fila):
        resultado.append(PARED)
    return resultado

def juego_mostrar(juego, ancho_y_alto_celdas, dimensiones, pistas):
    """Actualizar la ventana
    Recibe el juego, una tupla de el ancho y alto de las celdas, y una tupla
    con las filas y las columnas. Recibe la pila de pistas y muestra si hay pistas disponibles"""

    ancho_celda, alto_celda = ancho_y_alto_celdas
    filas, columnas = dimensiones

    pixeles_x = -64
    pixeles_y = 0

    #dibuja el piso en toda la ventana
    for i in range(columnas):
        pixeles_x += 64
        pixeles_y = 0
        for j in range(filas+1):
            gamelib.draw_image(PISO, 0 + pixeles_x, 0 + pixeles_y)
            pixeles_y += 64
            
    #dibuja los demás elementos y objetos de la grilla:
    for i in range(len(juego)):
        for j in range(len(juego[0])):
            x = (j * ancho_celda)
            y = (i * alto_celda)
            imagenes = definir_imagen(juego, i, j)
            for imagen in imagenes:
                gamelib.draw_image(imagen, x, y)
    
    if not pistas.esta_vacia():
        #Si hay pistas disponibles, lo muestra en pantalla
        gamelib.draw_text("Pista disponible", 70,30)

def diccionario_teclas():
    """Crea un diccionario donde las claves las teclas y los valores los movimientos que realizan.
    Si hay teclas que no realizan movimientos especificos dentro del sokoban, se le asignan
    valores especificos, como 1, -1, etc."""
    movimientos = {}
    teclas_y_acciones = {}

    with open("teclas.txt") as archivo:
        for linea in archivo:
            if linea != "\n":
                tecla, _, accion = linea.rstrip().split()
                teclas_y_acciones[tecla] = accion
    for accion, movimiento in ACCIONES.items():
        for tecla, accion2 in teclas_y_acciones.items():
            if accion2 == accion:
                movimientos[tecla] = movimiento
    return movimientos

def deshacer_y_rehacer(juego, movimiento, pila_movimientos, movimientos_deshechos, pistas):
    """Recibe la grilla, el tipo de movimiento a realizar, y las pilas de movimientos, movimientos deshechos y
    pistas. Devuelve la grilla actualizada según el movimiento realizado, y las tres pilas
    actualizadas"""

    if movimiento == 2:
        #se presionó DESHACER
        if pila_movimientos.esta_vacia():
            #no hay movimientos para deshacer
            return juego, pila_movimientos, movimientos_deshechos, pistas
        else:
            #Se presionó algo que no es el botón de pistas. Se vacía la pila
            pistas = Pila()
            nuevo_juego = pila_movimientos.desapilar()
            movimientos_deshechos.apilar(juego)
            return nuevo_juego, pila_movimientos, movimientos_deshechos, pistas

    if movimiento == -2:
        #se presionó REHACER
        if movimientos_deshechos.esta_vacia():
            #no hay movimientos para rehacer
            return juego, pila_movimientos, movimientos_deshechos, pistas
        else:
            nuevo_juego = movimientos_deshechos.desapilar()
            pila_movimientos.apilar(juego)
            return nuevo_juego, pila_movimientos, movimientos_deshechos, pistas

def representacion_inmutable(estado):
    """Devuelve una representacion inmutable de un estado: Una cadena"""
    resultado = ""
    for i in range(len(estado)):
        for j in range(len(estado[0])):
            resultado += estado[i][j]
    return resultado

def buscar_solucion(estado_inicial):
    """Busca la solucion de un nivel dado su estado actual. Devuelve una pila con las acciones
    a realizar. Si no hay solución, devuelve -1"""
    visitados = set()
    solucion_encontrada, acciones = backtrack(estado_inicial, visitados)
    #Como el backtrack es recursivo, se agregan primero a la lista los ultimos movimientos a hacer. Se debe invertir la lista:
    if not acciones:
        return -1
    return acciones

def backtrack(estado, visitados):
    """Busca el conjunto de acciones que solucionan un nivel"""
    inmutable = representacion_inmutable(estado)
    visitados.add(inmutable)
    if soko.juego_ganado(estado):
        #se encontró la solucion
        return True, Pila()
    acciones_posibles = soko.movimientos_posibles(estado)
    for accion in acciones_posibles:
        nuevo_estado = soko.mover(estado, accion)
        nuevo_inmutable = representacion_inmutable(nuevo_estado)
        if nuevo_inmutable in visitados:
            continue
        solucion_encontrada, acciones = backtrack(nuevo_estado, visitados)
        if solucion_encontrada:
            acciones.apilar(accion)
            return True, acciones
    return False, None

def juego_actualizar(juego, tecla, movimientos, pilas):
    """Actualizar el estado del juego.
    Recibe el estado del mismo, la tecla presionada, un diccionario de movimientos y una tupla
    con las pilas de movimientos, movimientos deshechos y pistas.
    Devuelve el juego actualizado (1 o -1 si se presionó salir o reiniciar), y las tres pilas actualizadas"""

    pila_movimientos = pilas[0]
    movimientos_deshechos = pilas[1]
    pistas = pilas[2]

    movimiento = ""
    for accion in movimientos:
        if tecla == accion:
            movimiento = movimientos[tecla]

    #Si el movimiento no está definido, devuelve el estado del juego sin modificaciones
    if not movimiento:
        return juego, pila_movimientos, movimientos_deshechos, pistas
    
    #Actualiza el estado del juego
    if movimiento == 1 or movimiento == -1:
        #se presionó SALIR o REINICIAR. Las pilas y colas se vacían
        pila_movimientos = Pila()
        movimientos_deshechos = Pila()
        pistas = Pila()
        return movimiento, pila_movimientos, movimientos_deshechos, pistas
    
    if movimiento == 2 or movimiento == -2:
        #se presionó DESHACER o REHACER
        return deshacer_y_rehacer(juego, movimiento, pila_movimientos, movimientos_deshechos, pistas)

    if movimiento == 3:
        #Se presionó PISTAS
        if pistas.esta_vacia():
            #No hay pistas disponibles. Busca la solución al nivel
            pistas = buscar_solucion(juego)
            if pistas == -1:
                #El nivel no tiene solución
                pistas = Pila()
                return juego, pila_movimientos, movimientos_deshechos, pistas
            return juego, pila_movimientos, movimientos_deshechos, pistas
        else:
            #Desapila un movimiento y lo realiza
            movimiento = pistas.desapilar()
            return realizar_movimiento(juego, movimiento, pila_movimientos, movimientos_deshechos, pistas)

    else:
        #se realizó un movimiento
        pistas = Pila()
        return realizar_movimiento(juego, movimiento, pila_movimientos, movimientos_deshechos, pistas)

def realizar_movimiento(juego, movimiento, pila_movimientos, movimientos_deshechos, pistas):
    """Realiza un movimiento. Devuelve el estado del juego actualizado"""
    nuevo_juego = soko.mover(juego, movimiento)
    if nuevo_juego == juego:
        #Se realizó un movimiento inválido. El juego queda igual. No hay movimientos para deshacer o rehacer
        return nuevo_juego, pila_movimientos, movimientos_deshechos, pistas
    else:
        #Se realizó un movimiento válido
        movimientos_deshechos = Pila()
        pila_movimientos.apilar(juego)
        return nuevo_juego, pila_movimientos, movimientos_deshechos, pistas

def main():
    # Inicializar el estado del juego
    hola.saludar()
    nivel = 1
    try:
        descripciones = crear_descripcion_niveles("niveles.txt")
        movimientos = diccionario_teclas()
    except FileNotFoundError:
        print("Archivo no encontrado. Cerrando programa")
        return

    while nivel <= NIVEL_MAXIMO:
        gamelib.title(f"Sokoban - Nivel {nivel}")
            
        #crea la grilla del nivel
        juego = juego_crear(descripciones, nivel)
        estado_inicial = juego

        alto_ventana , ancho_ventana, filas, columnas = dimensiones_ancho_y_alto(juego)
            
        #define el ancho y alto de las celdas
        ancho_celda = ancho_ventana // columnas
        alto_celda = alto_ventana // filas

        #crea pilas vacías para el deshacer, rehacer y pistas
        pila_movimientos = Pila()
        movimientos_deshechos = Pila()
        pistas = Pila()

        gamelib.resize(ancho_ventana, alto_ventana)

        while gamelib.is_alive():

            # Dibujar la pantalla
            gamelib.draw_begin()
            juego_mostrar(juego, (ancho_celda, alto_celda), (filas, columnas), pistas)
            gamelib.draw_end()

            #Si un nivel está ganado, muestra un mensaje y pasa al siguiente
            if soko.juego_ganado(juego):
                    gamelib.say("Nivel Completado")
                    nivel += 1
                    break

            ev = gamelib.wait(gamelib.EventType.KeyPress)
            if not ev:
                break

            tecla = ev.key
            #Actualizar el estado del juego, según la `tecla` presionada
            juego, pila_movimientos, movimientos_deshechos, pistas = juego_actualizar(juego, tecla, movimientos, (pila_movimientos, movimientos_deshechos, pistas))

            if juego == 1:
                #reinicia el nivel, tomando la descripcion inicial del mismo
                juego = estado_inicial

            if juego == -1:
                #Se presionó Escape. Sale del juego
                break

        if juego == -1:
                break

    #si se completó el ultimo nivel, el juego está ganado
    if nivel > NIVEL_MAXIMO:
        #muestra un mensaje
        gamelib.say("¡Juego Ganado! :D")

gamelib.init(main)