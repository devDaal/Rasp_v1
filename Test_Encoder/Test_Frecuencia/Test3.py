import RPi.GPIO as gp
import time
from goto import with_goto
#from tkinter import IntVar



gp.setmode(gp.BOARD)

# Pines del encoder
A = 35
B = 36

# Variables globales
contador = 0
contador_retro = 0
fase = None
ultima_fase = None
ultimoA = None
ultimoA2 = None
ultimoB = None
ultimoB2 = None

# Configuración de pines
gp.setup(A, gp.IN)
gp.setup(B, gp.IN)

@with_goto
def ciclo():        
    global contador, contador_retro, fase, ultima_fase, ultimoA, ultimoB, ultimoA2, ultimoB2
    
    # Leer los valores de los pines del encoder
    label.verificar_pines
    pinA = gp.input(A)
    pinB = gp.input(B)
    if (ultimoA == pinA == ultimoA2) and (ultimoB == pinB == ultimoB2):
        goto.verificar_pines
    #with open("Current pins.txt","a") as file1:
        #file1.write(str(pinA) + "    " + str(pinB) + "\n")
    if  (ultimoA != pinA) or (ultimoB != pinB):
        with open("Current pins.txt","a") as file1:
            file1.write(str(contador_retro) + " | " + str(pinA) + "    " + str(pinB) + " | " +str(contador) +"\n")
        if pinA == 0 and pinB == 0:
            fase = 1
        elif pinA == 0 and pinB == 1:
            fase = 2
        elif pinA == 1 and pinB == 1:
            fase = 3
        elif pinA == 1 and pinB == 0:
            fase = 4

        # Actualizar el contador normal si la fase incrementa en sentido horario
        if (ultima_fase == 1 and fase == 2):
            contador += 1
            #print("|",contador,"|Fase|",fase, "|" ,ultima_fase,"|Ult Fase|" " A |",pinA, "|",pinB,"| B |""Ult A|",ultimoA, "|",ultimoB, "|""Ult B")

        # Actualizar el contador de retroceso si la fase disminuye en sentido antihorario
        elif (ultima_fase == 1 and fase == 4):
            contador_retro += 1
            #print(contador_retro,"|""Fase |",fase, "|" ,ultima_fase,"|""Ult Fase |" " A |",pinA, "|",pinB,"| B |""Ult A|",ultimoA, "|",ultimoB, "|""Ult B")

    else:
        goto.verificar_pines
        
    
    
    ultima_fase = fase
    ultimoA2 = ultimoA
    ultimoA = pinA
    ultimoB2 = ultimoB
    ultimoB = pinB

# Función principal
def iniciar_conteo():
    tiempo = 3
    print("Presiona Enter para comenzar el conteo.")
    input()  # Espera a que el usuario presione Enter
    print("Comenzando conteo por",tiempo,"segundos...")

    # Ejecutar el conteo durante 10 segundos
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < tiempo:
        ciclo()

    print("Contador Final Avance |", contador, "|")
    print("Contador Final Retroceso |", contador_retro, "|")
    print("Conteo detenido después de",tiempo,"segundos.")
    gp.cleanup()  # Limpiar la configuración de los pines GPIO

# Iniciar el programa
if __name__ == "__main__":
    try:
        iniciar_conteo()
    except KeyboardInterrupt:
        gp.cleanup()