import os
import json
import socket
from string import ascii_uppercase

HOST = "127.0.0.1"
PORT = 65432
buffer_size = 10240

def insert_host():
    import re

    host=''
    port=0

    regexIP = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
    25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
    25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
    25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

    regexPort = "^[1-9]+[0-9]*$"


    while True:
        host = input("Ingresa el host: ")
        if re.match(regexIP, host):
            break
        else:
            print("Ingresa un host Valido")

    os.system("clear")

    port = input("Ingresa el puerto: ")
    while True:
        if re.match(regexPort, port):
            break
        else:
            print("Ingresa un Port Valido")
    
    os.system("clear")

    return (host, port)


def select_dificult():
    print("Selecciona la dificultad de tu juego")
    print("1. Principiante")
    print("2. Avanzado")

    dificultad = 0

    while True:
        try:
            dificultad = int(input())
            if dificultad in [1,2]:
                break
            else:
                print("Ingresa un valor Valido (1 o 2)")

        except Exception as e:
            print("Ingresa un valor Valido (1 o 2)")

    return dificultad



def instrucction():
    valid_y = [*range(1,casillas+1)]
    valid_x = list(ascii_uppercase)[0:casillas]

    inst = 0
    y = 0
    while True:
        print("Selecciona tu movimiento")
        print("0. Descubrir")
        print("1. Marcar")
        print("2. Desarcar")
        try:
            inst = int(input())
            if inst in [0,1,2]:
                break
            else:
                os.system("clear")
                print("Ingresa instruccion valida")
        except:
            os.system("clear")
            print("Ingresa instruccion valida")
        

    while True:
        
        try:
            y = int(input("Elige fila: "))
            if y in valid_y:
                y = y - 1 
                break
            else:
                os.system("clear")
                print("Ingresa fila Valida")
        except Exception:
            os.system("clear")
            print("Ingresa fila valida")

    x_axis = list(ascii_uppercase)
    while True:
        x = input("Elige columna: ")
        if x in valid_x:
            os.system("clear")
            x = x_axis.index(x)
            break
        else:
            os.system("clear")
            print("Ingresa instruccion valida")

    print("Instruccion es {} en ({},{})".format(instrucciones.get(inst), y, x))
    return inst, y, x


def show_board(board):
    """ Muestra el tablero en consola """
    from string import ascii_uppercase


    end = "  "
    print(" ", end="  ")
    for i in range(len(board)):
        print(list(ascii_uppercase)[i], end="  ")
    print("")

    for i,fila in enumerate(board):
        if i >= 9:
            end=" "
        else:
            end="  "
        print(i+1, end=end)
        for elem in fila:
            print(elem, end="  ")
        print()



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





if __name__ == '__main__':

    instrucciones = {0:"Descubrir", 1:"Marcar", 2:"Desmarcar"}
    casillas = 0
    board = None
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))
        linea = select_dificult()
        TCPClientSocket.sendall(str(linea).encode())
        data = TCPClientSocket.recv(buffer_size)
        
        game = json.loads(data.decode())
        board = game['tablero']
        casillas = game['casillas']
        print("Se inicio juego nivel {0} con {1}x{1} casillas y {2} minas".format(game['name'], game['casillas'], game['minas']))
        show_board(board)

        while True:
            ins, y, x = instrucction()
            move = {"inst":ins, "fil":y, "col":x}
            data = json.dumps(move)
            TCPClientSocket.sendall(data.encode())
            data = TCPClientSocket.recv(buffer_size)
            resposne = json.loads(data.decode())
            show_board(resposne['board'])
            if resposne['end']:
                final(resposne['win'])
