import os
import random
from re import T
import socket
import json
from datetime import date
from string import ascii_uppercase


HOST = "127.0.0.1"
PORT = 65432

dificult = {
    1:{"name":"principiante", "casillas":9, "minas":10},
    2:{"name":"Avanzado", "casillas":16, "minas":40}
}

def define_game():
    """ Selccion de juego a realizar """
    games = {0:"Buscaminas", 1:"Gato Dummy", 2:"Memoria"}
    init_date = date(1995, 12, 16)
    final_date = date(2021, 6, 26)
    delta = final_date - init_date
    return games.get(delta.days % 3)


def create_board(casillas, val):
    """Devuelve una matriz de dimensiones i * j rellena de s"""

    board=[]
    for a in range(casillas):
        board.append([])
        for b in range(casillas):
            board[a].append(val)
    return board


def show_board(board):
    """ Muestra el tablero en consola """

    from string import ascii_uppercase

    print(" ", end="  ")
    for i in range(len(board)):
        print(list(ascii_uppercase)[i], end="  ")
    print("")
    end = ""
    for i,fila in enumerate(board):
        if i >= 9:
            end=" "
        else:
            end="  "
        print(i+1, end=end)
        for elem in fila:
            print(elem, end="  ")
        print()


def put_mines(board, mines, lines):
    num = 0
    minas = []
    while num < mines:
        y = random.randint(0, lines-1)
        x = random.randint(0, lines-1)
        if board[y][x] != 9:
            board[y][x] = 9
            minas.append((y,x))
            num = num + 1
    
    return board, minas


def put_clues(board, lines):
    for y in range(lines):
        for x in range(lines):
            if board[y][x] == 9:
                for i in [-1,0,1]:
                    for j in [-1,0,1]:
                        if 0 <= y+i <= lines-1 and 0 <= x+j <= lines-1:
                            if board[y+i][x+j] != 9:
                                board[y+i][x+j] += 1


    return board


def make_move(hid_board, vis_board ,mark_cells ,move, casillas, y, x):
    h_cor = hid_board[y][x]
    v_cor = vis_board[y][x]
    win = False
    end = False
    
    # Mark
    if move == 1:
        if v_cor == "-":
            vis_board[y][x] = "#"
            mark_cells.append((y,x))

    #UnMArk
    if move == 2:
        if v_cor == "#":
            vis_board[y][x] = "-"
            mark_cells.remove((y,x)) 

    # View
    if move == 0:
        if hid_board[y][x] == 9:
            vis_board[y][x] = "@"
            end = True

        elif hid_board[y][x] != 0:
            vis_board[y][x] = hid_board[y][x]

        elif hid_board[y][x] == 0:
            vis_board[y][x] = 0
            vis_board = fill(hid_board, vis_board, y, x, casillas, "-")

    
    return hid_board, vis_board ,mark_cells ,win ,end 



def full_board(board, cells, val):
    """ Verifica si el tablero oculto esta completamente lleno (Indica el fin del juego)"""

    for y in range(cells):
        for x in range(cells):
            if board[y][x] == val:
                return False
    
    return True


def fill(oculto, visible, y, x, casillas, val):

    """ Descubre las celdas sin bomba a una casilla descubierta """

    ceros = [(y,x)]
    while len(ceros) > 0:
        y, x = ceros.pop()
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if 0 <= y+i <= casillas-1 and 0 <= x+j <= casillas-1:
                    if visible[y+i][x+j] == val and  oculto[y+i][x+j] == 0:
                        visible[y+i][x+j] = 0
                        if (y+i, x+j) not in ceros:
                            ceros.append((y+i, x+j))
                    else:
                        visible[y+i][x+j] = oculto[y+i][x+j]
    return visible


def final(win):
    """ Start Game """

    if win:
        print("*******************************")
        print("********* GANASTE \n/ *********")
        print("*******************************")

    elif not win:
        print("*******************************")
        print("********* PERDISTE :( *********")
        print("*******************************")



def verify(vis_board, bomb_cells ,mark_cells, cells, win, end):
    """ Verifica el estado del juego """
    win = win
    end = end
    if full_board(vis_board, cells, '-') and \
        sorted(mark_cells) == sorted(bomb_cells):
        win = True
        end = True

    return win, end



if __name__ == "__main__":
    print("Game: {}".format(define_game()))
    
    buffer_size = 1024
    dificultad=0

    hiden_board = None
    visible_board = None
    bomb_cells = []
    mark_cells = []
    win = False
    end = False
    


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        # Iniciacion del servidor 
        TCPServerSocket.bind((HOST, PORT))
        TCPServerSocket.listen()
        print("El servidor TCP está disponible y en espera de solicitudes")

        # Juego
        Client_conn, Client_addr = TCPServerSocket.accept()
        with Client_conn:
            # Recibiendo dificutad del juego
            data = Client_conn.recv(buffer_size)
            # dificultad solicitada por el jugador
            dificultad = int(data.decode())
            sett = dificult.get(dificultad)

            # Creando tableros para juedor y control
            visible_board = create_board(sett['casillas'], '-')
            hiden_board = create_board(sett['casillas'], 0)
            #Colocando bombas y pistas a tablero oculto
            hiden_board, bomb_cells = put_mines(hiden_board, sett["minas"], sett['casillas'])
            hiden_board = put_clues(hiden_board, sett["casillas"])
            show_board(hiden_board)

            # Pasando tablero a jugador con info de juego
            sett['tablero'] = visible_board
            data = json.dumps(sett)
            Client_conn.sendall(data.encode())

            # Flujo de Juego
            while True:
                data = Client_conn.recv(buffer_size)
                move = json.loads(data.decode())
                hiden_board, visible_board, mark_cells, win, end = make_move(hiden_board, visible_board, mark_cells,move['inst'], sett['casillas'],move['fil'], move['col'])
                win, end = verify(visible_board, bomb_cells, mark_cells, sett['casillas'], win, end)
                response = {"end":end, "win":win, "board":visible_board}
                data = json.dumps(response)
                Client_conn.sendall(data.encode())
                if end:
                    final(win)
                    break

