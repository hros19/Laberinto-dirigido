
/** <module> Resolución de laberintos dirigidos desde archivos .txt
 * 
 * Módulo que alberga la parte lógica encargada de la resolución de laberintos que son
 * leídos desde archivos .txt. El módulo se encarga de leer el archivo, crear el laberinto
 * y resolverlo. Los resultados son pasados a la interfaz gráfica para su visualización e
 * interacción.
 * Instituto Tecnológico de Costa Rica
 * Escuela de Ingeniería en Computación
 * Lenguajes de Programación
 * II Semestre, año 2022
 * Profesor: Allan Rodríguez Dávila
 * Autor: Hansol Antay Rostrán
 * Carné: 2020319635
 */

 use_module(library(pio)).

% :: Manejo de archivos y definición de la matriz :: %

% Read file and return a list of lists with pio
lines([])           --> call(eos), !.
lines([Line|Lines]) --> line(Line), lines(Lines).

eos([], []).

line([])     --> ( "\n" ; call(eos) ), !.
line([L|Ls]) --> [L], line(Ls).

% :: Predicados para definición de reglas :: %

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

agregar_cruce_pendiente((X, Y)) :- asserta(cruce_pendiente((X, Y))).
agregar_cruces_pendientes([]).
agregar_cruces_pendientes([Cruce|Resto]) :- agregar_cruce_pendiente(Cruce), agregar_cruces_pendientes(Resto).

% Agregar posiciones visitadas (para que no se vuelvan a visitar)
agregar_posicion_visitada((X, Y)) :-
    posicion_visitada((X, Y)) -> true;
    asserta(posicion_visitada((X, Y))).

% Obtiene el valor de una posición en la matriz
obtener_valor_posicion((X, Y), Valor) :-
    matriz(Matrix),
    nth0(X, Matrix, Row),
    nth0(Y, Row, Valor).

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

obtener_movimientos((X, Y), MovimientosRes) :-
    obtener_valor_posicion((X, Y), Valor),
    obtener_movimientos_de_valor(Valor, Movimientos),
    obtener_movimientos_aux((X, Y), Movimientos, MovimientosRes).

obtener_movimientos_aux(_, [], []).
obtener_movimientos_aux((X, Y), [Movimiento|Resto], MovimientosRes) :-
    obtener_nueva_posicion((X, Y), Movimiento, (X1, Y1)),
    posicion_viable((X1, Y1)) ->
        obtener_movimientos_aux((X, Y), Resto, RestoMovimientos),
        MovimientosRes = [Movimiento|RestoMovimientos];
        obtener_movimientos_aux((X, Y), Resto, MovimientosRes).

posicion_viable((X, Y)) :-
    posicion_final((X, Y)) -> true;
    posicion_actual((X, Y)) -> false;
    pared((X, Y)) -> false;
    obtener_valor_posicion((X, Y), Valor),
    Valor \= x.

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

% Consulta si una posicion es perteneciente a la solucion final.
pertenece_a_solucion((X, Y)) :-
    obtener_camino_solucion(Camino),
    member((X, Y), Camino).

% Tomará un cruce de la lista de cruces y lo procesará hasta que no tenga más movimientos posibles.
mover_desde_cruce :-
    cruces_disponibles(CrucesDisponibles),
    member((Xc, Yc), CrucesDisponibles),
    obtener_movimientos_posibles((Xc, Yc), MovimientosPosibles),
    member(Movimiento, MovimientosPosibles),
    obtener_nueva_posicion((Xc, Yc), Movimiento, (Xf, Yf)),
    agregar_posicion_visitada((Xf, Yf)),
    solucionar((Xf, Yf)).

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

% A cada cruce visitada almacenarla como una cruce pendiente, no agregar si ya se encuentra en la lista.
determinar_cruces_pendientes :-
    retract(cruce_pendiente((-1,-1))),
    cruces_visitadas(CrucesVisitadas),
    member((X, Y), CrucesVisitadas),
    not(cruce_pendiente((X, Y))),
    asserta(cruce_pendiente((X, Y))),
    determinar_cruces_pendientes.

% Obtener los movimientos de un cruce pendiente, son los movimientos que no son celda_sin_solucion,
% ni pared, ni parte de la solución.
obtener_movimientos_cruce_pendiente((X, Y), MovimientosPosibles) :-
    obtener_movimientos_posibles((X, Y), MovimientosPosibles),
    findall(Movimiento, (member(Movimiento, MovimientosPosibles), obtener_nueva_posicion((X, Y), Movimiento, (Xf, Yf)), not(celda_sin_solucion((Xf, Yf))), not(camino_solucion((Xf, Yf)))), MovimientosPosibles).

obtener_cruces_pendientes(CrucesPendientes) :-
    findall((X, Y), cruce_pendiente((X, Y)), CrucesPendientes).

% Mientras haya cruces pendientes, moverse desde un cruce pendiente
% luego de moverse desde un cruce pendiente, se debe eliminar el cruce pendiente de la lista de cruces pendientes
mover_desde_cruce_pendiente :-
    obtener_cruces_pendientes(CrucesPendientes),
    CrucesPendientes = [] -> true;
    reiniciar_base_de_conocimiento,
    member((Xc, Yc), CrucesPendientes),
    retract(cruce_pendiente((Xc, Yc))),
    jugar_desde((Xc, Yc)).

% Imprimir las cruces pendientes
cp(CrucesPendientes) :-
    findall((X, Y), cruce_pendiente((X, Y)), CrucesPendientes),
    write(CrucesPendientes).

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

% Borra los elementos duplicados de una lista.
borrar_duplicados([], []).
borrar_duplicados([X|Xs], Ys) :-
    member(X, Xs), !,
    borrar_duplicados(Xs, Ys).

borrar_duplicados([X|Xs], [X|Ys]) :-
    borrar_duplicados(Xs, Ys).

obtener_camino_solucion(CaminoSolcion) :-
    findall((X, Y), camino_solucion((X, Y)), CaminoAux),
    borrar_duplicados(CaminoAux, CaminoSolcion).

reiniciar_base_de_conocimiento :-
    retractall(posicion_visitada(_)),
    retractall(posicion_borrada(_)),
    retractall(posicion_inicial(_)),
    retractall(posicion_visitada(_)),
    retractall(posicion_borrada(_)),
    retractall(posicion_sig_a_procesar(_)).

jugar_desde((X, Y)) :-
    definir_posicion_actual((X, Y)),
    definir_posicion_inicial((X, Y)),
    asserta(posicion_visitada((X, Y))),
    asserta(sig_a_procesar([])),
    solucionar((X, Y)).

run :-
    posicion_inicial((X, Y)),
    asserta(posicion_visitada((X, Y))),
    asserta(sig_a_procesar([])),
    asserta(cruce_pendiente((-1,-1))),
    asserta(celda_sin_solucion((-1,-1))),
    solucionar((X, Y)).

% Pregunta si una tupla es parte de la solucion.
es_parte_solucion((X, Y)) :-
    obtener_camino_solucion(Camino),
    member((X, Y), Camino).

% Recibe una posición, verifica los movimientos posibles
% y retorna el movimiento que sea parte del camino de solución
obtener_ayuda((X,Y), (Xa, Ya)) :- 
    obtener_movimientos((X,Y), Movimientos),
    member(Mov, Movimientos),
    obtener_nueva_posicion((X,Y), Mov, (Xa, Ya)),
    es_parte_solucion((Xa, Ya)).

% Recibe una posición actual, y una posición objetivo.
% Retorna true si la posición objetivo es un movimiento válido de la posición actual.
es_movimiento_valido((X, Y), (Xs, Ys)) :-
    obtener_movimientos((X,Y), Movimientos),
    member(Mov, Movimientos),
    obtener_nueva_posicion((X,Y), Mov, (Xn, Yn)),
    Xn = Xs,
    Yn = Ys.
