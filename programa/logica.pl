
/** <module> Resolución de laberintos dirigidos desde archivos .txt
 * 
 * Módulo que alberga la parte lógica encargada de la resolución de laberintos que son
 * leídos desde archivos .txt. El módulo se encarga de leer el archivo, crear el laberinto
 * y resolverlo. Los resultados son pasados a la interfaz gráfica para su visualización e
 * interacción.
 * 
 * ------------------------------------------------------------------------------------------------
 * 
 * Instituto Tecnológico de Costa Rica
 * Escuela de Ingeniería en Computación
 * Lenguajes de Programación
 * II Semestre, año 2022
 * Profesor: Allan Rodríguez Dávila
 * 
 * ------------------------------------------------------------------------------------------------
 *
 * Autor: Hansol Antay Rostrán
 * Carné: 2020319635
 *
 */

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% :: Manejo de archivos y definición de la matriz :: %

% -------------------------------------------------------------------------------------------------
% Lectura de archivos
% Source: https://stackoverflow.com/questions/4805601/read-a-file-line-by-line-in-prolog
% -------------------------------------------------------------------------------------------------
leer_archivo(Stream, []) :-
    at_end_of_stream(Stream).

leer_archivo(Stream, [X|L]) :-
    \+ at_end_of_stream(Stream),
    read(Stream, X),
    leer_archivo(Stream, L).

% -------------------------------------------------------------------------------------------------
% archivo_a_matriz(+Archivo, -Matriz)
% Recibe la dirección de memoria y devuelve una matriz
% -------------------------------------------------------------------------------------------------
archivo_a_matriz(Path, Matrix) :-
    open(Path, read, Stream),
    leer_archivo(Stream, Matrix),
    close(Stream).

% -------------------------------------------------------------------------------------------------
% definir_archivo_matriz(+Path)
% Recibe la dirección de memoria y define la matriz que se usará para el laberinto
% -------------------------------------------------------------------------------------------------
definir_archivo_matriz(Path) :-
    archivo_a_matriz(Path, Matrix),
    assert(matriz(Matrix)).
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% :: Predicados para definición de reglas :: %

% Agregar paredes (representadas por 'x' en el archivo .txt)
agregar_pared((X, Y)) :- asserta(pared((X, Y))).

agregar_paredes([]).
agregar_paredes([Pared|Resto]) :- agregar_pared(Pared), agregar_paredes(Resto).

eliminar_paredes([]).
eliminar_paredes([Pared|Resto]) :- retract(pared(Pared)), eliminar_paredes(Resto).

% Determinar camino de solución
agregar_solucion((X, Y)) :- asserta(solucion((X, Y))).

agregar_posicion_borrada((X, Y)) :- assertz(posicion_borrada((X, Y))).

determinar_solucion([]).
determinar_solucion([Solucion|Resto]) :- agregar_solucion(Solucion), determinar_solucion(Resto).

% Definición de posiciones inicio, fin, cruce y ultimo procesado (encontrar solucion).
definir_posicion_actual((X, Y)) :- asserta(posicion_actual((X, Y))).

definir_posicion_inicial((X, Y)) :- asserta(posicion_inicial((X, Y))).

definir_posicion_final((X, Y)) :- asserta(posicion_final((X, Y))).

definir_ultimo_cruce((X, Y)) :- asserta(ultimo_cruce((X, Y))).

definir_sig_a_procesar((X, Y)) :- asserta(sig_a_procesar((X, Y))).

% Agregar cruces (representadas por 'c' en el archivo .txt)
agregar_cruce((X, Y)) :- asserta(cruce((X, Y))).
agregar_cruces([]).
agregar_cruces([Cruce|Resto]) :- agregar_cruce(Cruce), agregar_cruces(Resto).

% Agregar posiciones visitadas (para que no se vuelvan a visitar)
agregar_posicion_visitada((X, Y)) :-
    posicion_visitada((X, Y)) -> true;
    asserta(posicion_visitada((X, Y))).
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% :: Obtención de datos del laberinto :: %

% Obtención de dimensiones del laberinto
obtener_cantidad_filas(Matriz, CantidadFilas) :- length(Matriz, CantidadFilas).

obtener_cantidad_columnas(Matriz, CantidadColumnas) :- 
    nth0(0, Matriz, Fila),
    length(Fila, CantidadColumnas).

obtener_dimensiones_matriz(Dimensiones) :-
    matriz(Matriz),
    obtener_cantidad_filas(Matriz, CantidadFilas),
    obtener_cantidad_columnas(Matriz, CantidadColumnas),
    Dimensiones = (CantidadFilas, CantidadColumnas).

% Calcular posicion de inicio y fin (desde el archivo .txt)
obtener_coordenadas_inicio(Matrix, X, Y) :-
    nth0(Y, Matrix, Row),
    nth0(X, Row, i).

obtener_coordenadas_final(Matrix, X, Y) :-
    nth0(Y, Matrix, Row),
    nth0(X, Row, f).

% Obtiene el valor de una posición en la matriz
obtener_valor_posicion((X, Y), Valor) :-
    matriz(Matrix),
    nth0(X, Matrix, Row),
    nth0(Y, Row, Valor).

% Obtener las posiciones de las paredes de la matriz
posiciones_de_paredes_en_fila([], _, _, []).
posiciones_de_paredes_en_fila([x|Cola], X, Y, [(Y, X)|Restantes]) :-
    X1 is X + 1,
    posiciones_de_paredes_en_fila(Cola, X1, Y, Restantes).

posiciones_de_paredes_en_fila([_|Cola], X, Y, Posiciones) :-
    X1 is X + 1,
    posiciones_de_paredes_en_fila(Cola, X1, Y, Posiciones).

posiciones_de_paredes_en_matriz([], _, []).
posiciones_de_paredes_en_matriz([Fila|Resto], Y, Posiciones) :-
    Y1 is Y + 1,
    posiciones_de_paredes_en_fila(Fila, 0, Y, PosicionesEnFila),
    posiciones_de_paredes_en_matriz(Resto, Y1, RestoPosiciones),
    append(PosicionesEnFila, RestoPosiciones, Posiciones).
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% :: Definición de reglas del laberinto respecto a movimientos :: %

% Movimientos dependiendo del valor de la casilla.
obtener_movimientos_de_valor(i, [arriba, derecha, abajo, izquierda]).
obtener_movimientos_de_valor(c, [arriba, derecha, abajo, izquierda]).
obtener_movimientos_de_valor(u, [arriba]).
obtener_movimientos_de_valor(d, [abajo]).
obtener_movimientos_de_valor(l, [izquierda]).
obtener_movimientos_de_valor(r, [derecha]).
obtener_movimientos_de_valor(_, []).

% Movimiento posibles según movimiento (retornando la nueva posición).
obtener_nueva_posicion((X, Y), arriba, (Xs, Y)) :- Xs is X - 1.
obtener_nueva_posicion((X, Y), abajo, (Xs, Y)) :- Xs is X + 1.
obtener_nueva_posicion((X, Y), izquierda, (X, Ys)) :- Ys is Y - 1.
obtener_nueva_posicion((X, Y), derecha, (X, Ys)) :- Ys is Y + 1.

% Movimiento posibles según posición (retornando los movimientos que sean válidos).
% Se considerarán movimientos válidos aquellos que no sean paredes, ni posiciones visitadas.
obtener_movimientos_posibles((X, Y), MovimientosValidos) :-
    obtener_valor_posicion((X, Y), Valor),
    obtener_movimientos_de_valor(Valor, MovimientosPosibles),
    obtener_movimientos_validos((X, Y), MovimientosPosibles, MovimientosValidos).

obtener_movimientos_validos(_, [], []).
obtener_movimientos_validos((X, Y), [Movimiento|Resto], MovimientosValidos) :-
    obtener_nueva_posicion((X, Y), Movimiento, (X1, Y1)),
    posicion_valida((X1, Y1)) ->
        obtener_movimientos_validos((X, Y), Resto, RestoMovimientosValidos),
        MovimientosValidos = [Movimiento|RestoMovimientosValidos];
        obtener_movimientos_validos((X, Y), Resto, MovimientosValidos).

posicion_valida((X, Y)) :-
    posicion_visitada((X, Y)) -> false;
    posicion_final((X, Y)) -> true;
    posicion_actual((X, Y)) -> false;
    pared((X, Y)) -> false;
    obtener_valor_posicion((X, Y), Valor),
    Valor \= x.

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% :: Parte algoritmica (Resolución del laberinto) :: %

% Intente solucionar una posición dada. La idea principal es iniciar el algoritmo desde acá e
% intente hacer los movimientos posibles para llegar a la posición final. Y si encontró un
% cruce, simplemente lo guarda en la lista de cruces y se detiene.
solucionar((Xi, Yi)) :-
    obtener_valor_posicion((Xi, Yi), Valor),
    Valor = c -> agregar_cruce((Xi, Yi));
    obtener_movimientos_posibles((Xi, Yi), MovimientosPosibles),
    member(Movimiento, MovimientosPosibles),
    obtener_nueva_posicion((Xi, Yi), Movimiento, (Xf, Yf)),
    retractall(posicion_actual(_)),
    asserta(posicion_actual((Xf, Yf))),
    agregar_posicion_visitada((Xf, Yf)),
    (posicion_final((Xf, Yf)) -> true; solucionar((Xf, Yf))).

% El problema de solución es que no sabe que hacer con los cruces, simplemente se detiene en ellos
% por lo que se tuvo que hacer una función que se encargue de solucionar los cruces. La idea es
% procesar cada uno de los cruces almacenados en la lista de cruces y solucionar cada uno de los
% caminos de ese cruce (movimientos posibles de dichos cruces).
cruces_disponibles(CrucesDisponibles) :-
    posiciones_visitadas(PosicionesVisitadas),
    findall((X, Y), (member((X, Y), PosicionesVisitadas), obtener_movimientos_posibles((X, Y), MovimientosPosibles), MovimientosPosibles \= []), CrucesDisponibles).

% Tomará un cruce de la lista de cruces y lo procesará hasta que no tenga más movimientos posibles.
mover_desde_cruce :-
    cruces_disponibles(CrucesDisponibles),
    member((Xc, Yc), CrucesDisponibles),
    obtener_movimientos_posibles((Xc, Yc), MovimientosPosibles),
    member(Movimiento, MovimientosPosibles),
    obtener_nueva_posicion((Xc, Yc), Movimiento, (Xf, Yf)),
    agregar_posicion_visitada((Xf, Yf)),
    solucionar((Xf, Yf)).

% Obtiene la última posición visitada y la retorna.
obtener_ultima_pos_visitada((X, Y)) :-
    posiciones_visitadas(PosicionesVisitadas),
    last(PosicionesVisitadas, (X, Y)).

% Retorna todas las posiciones visitadas en una lista.
posiciones_visitadas(PosicionesVisitadas) :-
    findall((X, Y), posicion_visitada((X, Y)), PosicionesVisitadas).

% Mientras haya cruces disponibles, moverse desde un cruce
terminar_laberinto :-
    cruces_disponibles(CrucesDisponibles),
    CrucesDisponibles = [] -> true;
    mover_desde_cruce,
    terminar_laberinto.

% Pregunta si se llegó a la posición final (Revisando cada tupla de la lista de posiciones visitadas)
llego_a_posicion_final :-
    posiciones_visitadas(PosicionesVisitadas),
    member((X, Y), PosicionesVisitadas),
    posicion_final((X, Y)).

% Inventir lista
invertir_lista([], []).
invertir_lista([X|Resto], ListaInvertida) :-
    invertir_lista(Resto, RestoInvertido),
    append(RestoInvertido, [X], ListaInvertida).

% Retorna la lista de posiciones visitadas invertida
pos_visitadas_inv(PosicionesVisitadasInv) :-
    posiciones_visitadas(PosicionesVisitadas),
    invertir_lista(PosicionesVisitadas, PosicionesVisitadasInv).

% Retorna una lista de todas las celdas con valor 'c' de las posiciones visitadas
cruces_visitadas(CrucesVisitadas) :-
    pos_visitadas_inv(PosicionesVisitadasInv),
    findall((X, Y), (member((X, Y), PosicionesVisitadasInv), obtener_valor_posicion((X, Y), Valor), Valor = c), CrucesVisitadas).

c :-
    cruces_visitadas(CrucesVisitadas),
    write(CrucesVisitadas).

p :-
    pos_visitadas_inv(PosicionesVisitadas),
    write(PosicionesVisitadas).

% Distancia manhattan entre dos puntos
distancia_manhattan((X1, Y1), (X2, Y2), Distancia) :-
    Distancia is abs(X1 - X2) + abs(Y1 - Y2).

% Procesar cada elemento de las posiciones visitadas y obtener la distancia manhattan entre
% cada valor y la posición siguiente. Si la distancia manhattan entre el valor actual y el
% siguiente es 1, entonces se trata de un movimiento válido. Si la distancia manhattan es
% mayor a 1, entonces elimina el valor actual de la lista de posiciones visitadas.
procesar_posiciones_visitadas :-
    pos_visitadas_inv(PosicionesVisitadas),
    procesar_posiciones_visitadas_aux(PosicionesVisitadas).

procesar_posiciones_visitadas_aux([]).
procesar_posiciones_visitadas_aux([_]).
procesar_posiciones_visitadas_aux([(X1, Y1), (X2, Y2)|Resto]) :-
    distancia_manhattan((X1, Y1), (X2, Y2), Distancia),
    Distancia > 1 -> retractall(posicion_visitada((X1, Y1))), definir_sig_a_procesar((X2, Y2)),
                     agregar_posicion_borrada((X1, Y1));
    procesar_posiciones_visitadas_aux([(X2, Y2)|Resto]).

% Retorna true si desde la primera posición visitada se puede llegar a la posición final
% de forma que no existe una distancia manhattan mayor a 1 entre las posiciones.
solucion_valida :-
    pos_visitadas_inv(PosicionesVisitadas),
    posicion_final((Xf, Yf)),
    solucion_valida_aux(PosicionesVisitadas, (Xf, Yf)).

solucion_valida_aux([], _).
solucion_valida_aux([_], _).
solucion_valida_aux([(X1, Y1), (X2, Y2)|Resto], (Xf, Yf)) :-
    distancia_manhattan((X1, Y1), (X2, Y2), Distancia),
    Distancia > 1 -> false;
    (X2 = Xf, Y2 = Yf) -> true;
    solucion_valida_aux([(X2, Y2)|Resto], (Xf, Yf)).

% Retorna true si una posición está en la lista de posiciones visitadas
% y se encuentra antes de la posición final.
posicion_visitada_antes_de_final((X, Y)) :-
    pos_visitadas_inv(PosicionesVisitadas),
    posicion_final((Xf, Yf)),
    posicion_visitada((X, Y)),
    es_anterior_en_lista((X, Y), (Xf, Yf), PosicionesVisitadas).

% Retorna true si el elemento Previo está ante que el limite en la lista.
es_anterior_en_lista(Previo, Limite, Lista) :-
    nth0(IndicePrevio, Lista, Previo),
    nth0(IndiceLimite, Lista, Limite),
    IndicePrevio < IndiceLimite.

% Determina el camino solucion, si es solucion valida retorna true,
% y si no, procesa las posiciones visitadas y vuelve a intentar.
determinar_camino_solucion :-
    solucion_valida -> true;
    procesar_posiciones_visitadas,
    determinar_camino_solucion.

% Guarda cada una de las posiciones visitadas en la lista de camino solución hasta llegar al
% punto final.
guardar_camino_solucion :-
    pos_visitadas_inv(PosicionesVisitadas),
    posicion_final((Xf, Yf)),
    guardar_camino_solucion_aux(PosicionesVisitadas, (Xf, Yf)).

guardar_camino_solucion_aux([], _).
guardar_camino_solucion_aux([(X, Y)|Resto], (Xf, Yf)) :-
    (X = Xf, Y = Yf) -> assertz(camino_solucion((X, Y)));
    assertz(camino_solucion((X, Y))),
    guardar_camino_solucion_aux(Resto, (Xf, Yf)).

obtener_posiciones_borradas(PosicionesBorradas) :-
    findall((X, Y), posicion_borrada((X, Y)), PosicionesBorradas).

% Obtener posiciones que sean posiciones borradas, o que sean posiciones visitadas
% que no sean camino solución.
obtener_pos_no_solucion(PosicionesABorrar) :-
    obtener_posiciones_borradas(PosicionesBorradas),
    posiciones_visitadas(PosicionesVisitadas),
    findall((X, Y), (member((X, Y), PosicionesVisitadas), not(camino_solucion((X, Y)))), PosicionesNoCaminoSolucion),
    append(PosicionesBorradas, PosicionesNoCaminoSolucion, PosicionesABorrar).

z :-
    camino_solucion((X, Y)),
    write((X, Y)), nl,
    fail.

y :-
    posicion_borrada((X, Y)),
    write((X, Y)), nl,
    fail.

x :-
    obtener_pos_no_solucion(Posiciones),
    write(Posiciones), nl,
    fail.

w :-
    pos_visitadas_inv(Posiciones),
    write(Posiciones), nl,
    fail.

reiniciar_base_de_conocimiento :-
    retractall(posicion_visitada(_)),
    retractall(posicion_borrada(_)),
    retractall(camino_solucion(_)),
    retractall(posicion_final(_)),
    retractall(posicion_inicial(_)),
    retractall(pos_visitadas_inv(_)),
    retractall(posiciones_visitadas(_)),
    retractall(posiciones_borradas(_)),
    retractall(posiciones_no_solucion(_)),
    retractall(posicion_sig_a_procesar(_)).

jugar_desde((X, Y)) :-
    matriz(Matriz),
    posiciones_de_paredes_en_matriz(Matriz, 0, Posiciones),
    obtener_coordenadas_final(Matriz, (Xf, Yf)),
    definir_posicion_final((Yf, Xf)),
    definir_posicion_actual((X, Y)),
    definir_posicion_inicial((X, Y)),
    asserta(posicion_visitada((X, Y))),
    asserta(sig_a_procesar([])),
    agregar_paredes(Posiciones),
    solucionar((X, Y)).

% Punto de arranque (previamente se tuvo que haber definido el archivo de matriz).
% definir_archivo_matriz(Path), siendo (Path) la ruta del archivo de matriz (String).
% Posteriormente se llama a terminar_laberinto.
main :-
    definir_archivo_matriz('./matrices/matriz_base.txt'),
    matriz(Matriz),
    posiciones_de_paredes_en_matriz(Matriz, 0, Posiciones),
    obtener_coordenadas_inicio(Matriz, X, Y),
    obtener_coordenadas_final(Matriz, Xf, Yf),
    definir_posicion_actual((Y, X)),
    definir_posicion_inicial((Y, X)),
    definir_posicion_final((Yf, Xf)),
    asserta(posicion_visitada((Y, X))),
    asserta(sig_a_procesar([])),
    agregar_paredes(Posiciones),
    solucionar((Y, X)).