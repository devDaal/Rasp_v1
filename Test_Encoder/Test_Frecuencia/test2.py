import RPi.GPIO as gp
import time

gp.setmode(gp.BOARD)

# Pines del encoder
A = 15
B = 16

# Variables globales
contador = 0
contador_retro = 0
fase = 0
ultima_fase = 0
updated = False
updated_retro = False
ultimoA = 0
ultimoB = 0

# Configuración de pines
gp.setup(A, gp.IN)
gp.setup(B, gp.IN)

def ciclo():        
    global updated, contador, contador_retro, fase, ultima_fase,ultimoA, ultimoB, updated_retro
    
    # Leer los valores de los pines del encoder
    pinA = gp.input(A)
    pinB = gp.input(B)

    if (ultimoA != pinA) or (ultimoB != pinB): 
       # Determinar la fase actual basándose en los valores de A y B
        if pinA == 0 and pinB == 0:
            fase = 1
        elif pinA == 0 and pinB == 1:
            fase = 2
        elif pinA == 1 and pinB == 1:
            fase = 3
        elif pinA == 1 and pinB == 0:
            fase = 4

        # Actualizar el contador normal si la fase incrementa en sentido horario
        if (ultima_fase == 1 and fase == 2) or (ultima_fase == 2 and fase == 3) or \
           (ultima_fase == 3 and fase == 4) or (ultima_fase == 4 and fase == 1):
            contador += 1
            updated = True

        # Actualizar el contador de retroceso si la fase disminuye en sentido antihorario
        elif (ultima_fase == 1 and fase == 4) or (ultima_fase == 4 and fase == 3) or \
             (ultima_fase == 3 and fase == 2) or (ultima_fase == 2 and fase == 1):
            contador_retro += 1
            updated_retro = True
        else:
            pass
    # Guardar la fase actual como la última para la próxima iteración
    ultima_fase = fase
    ultimoA = pinA
    ultimoB = pinB

def imprimir_resultado():
    global updated, updated_retro
    if updated:
        #print("Contador Avance |", contador, "|")
        #print("Contador Retroceso |", contador_retro, "|")
        updated = False
    elif updated_retro:
        updated_retro = False

# Función principal
def iniciar_conteo():
    print("Presiona Enter para comenzar el conteo.")
    input()  # Espera a que el usuario presione Enter
    print("Comenzando conteo por 10 segundos...")

    # Ejecutar el conteo durante 10 segundos
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < 5:
        ciclo()
        imprimir_resultado()

    print(contador)
    print(contador_retro)
    print("Conteo detenido después de 10 segundos.")
    gp.cleanup()  # Limpiar la configuración de los pines GPIO

# Iniciar el programa
if __name__ == "__main__":
    try:
        iniciar_conteo()
    except KeyboardInterrupt:
        gp.cleanup()
