import RPi.GPIO as gp
import time


gp.setmode(gp.BOARD)
A = 35
B = 36

# ----------------------------------Variables globales

lastA = None
lastB = None
contador_pos = 0
contador_neg = 0

#-----------------------------------------------------------------------------

gp.setup(A, gp.IN)
gp.setup(B, gp.IN)

#-------------------------------------------------Ciclo de la funcion-------------------------------------------

def ciclo():        
    global lastA, lastB,contador_pos, contador_neg
    
    pinB = gp.input(B)
    pinA = gp.input(A)
    if lastB != pinB or lastA != pinA:
        if lastA == 0 and lastB == 0:
            if pinA == 0 and pinB == 1:
                contador_neg += 1
            elif pinB == 0 and pinA == 1:
                contador_pos += 1
            
    lastB = pinB
    lastA = pinA
    
# -----------------------------------------------Función principal----------------------------------------------

def iniciar_conteo():
    tiempo = 10
    print("Presiona Enter para comenzar el conteo.")
    input()
    print("Contando por", tiempo ,"segundos...")

    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < tiempo:
        ciclo()
    contador_abs = contador_pos - contador_neg
    posicion = contador_abs/500
    print("Contador Avance |", posicion, "|")
    print("Conteo detenido después de",tiempo, "segundos.")
    gp.cleanup()
#---------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        iniciar_conteo()
    except KeyboardInterrupt:
        gp.cleanup()