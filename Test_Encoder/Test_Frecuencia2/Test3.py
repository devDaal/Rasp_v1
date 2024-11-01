import RPi.GPIO as gp
import time
from goto import with_goto
#from tkinter import IntVar



gp.setmode(gp.BOARD)
A = 35
B = 36

# ----------------------------------Variables globales
positivo = False
negativo = False
lastA = None
lastB = None
contador_pos = 0
contador_neg = 0

#-----------------------------------------------------------------------------

gp.setup(A, gp.IN)
gp.setup(B, gp.IN)

#-------------------------------------------------Ciclo de la funcion-------------------------------------------
@with_goto
def ciclo():        
    global positivo, negativo, lastA, lastB,contador_pos, contador_neg
    
    label.verificar_pines
    #time.sleep(0.2)
    pinB = gp.input(B)
    pinA = gp.input(A)
    if lastB != pinB or lastA != pinA:
        if lastA == 0 and lastB == 0:
            if pinA == 0 and pinB == 1:
                negativo = True
            elif pinB == 0 and pinA == 1:
                positivo = True
            if positivo:
                contador_pos += 1
            elif negativo:
                contador_neg += 1
            
    positivo = False
    negativo = False
    lastB = pinB
    lastA = pinA
    
# -----------------------------------------------Función principal----------------------------------------------
def iniciar_conteo():
    tiempo = 3
    print("Presiona Enter para comenzar el conteo.")
    input()
    print("Comenzando conteo por ", tiempo ," segundos...")

    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < tiempo:
        ciclo()

    print("Contador Final Avance |", contador_pos, "|")
    print("Contador Final Retroceso |", contador_neg, "|")
    print("Conteo detenido después de ",tiempo, " segundos.")
    gp.cleanup()
#---------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        iniciar_conteo()
    except KeyboardInterrupt:
        gp.cleanup()