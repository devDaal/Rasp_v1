import RPi.GPIO as gp
gp.setmode(gp.BOARD)
global A
global B
global contador
global contador_retro
global fase
global ultima_fase
global updated
A = 15
B = 16
contador = 0
contador_retro = 0
fase = 0
ultima_fase = 0
updated = False
gp.setup(A, gp.IN)
gp.setup(B, gp.IN)

def ciclo ():        
    global updated
    global A
    global B
    global contador
    global fase
    global ultima_fase
    global contador_retro
    pinA = gp.input(A)
    pinB = gp.input(B)
    if pinA == 0 and pinB == 0:
        fase = 1
    elif pinA == 0 and pinB == 1:
        fase = 2
    elif pinA == 1 and pinB == 1:
        fase = 3
    elif pinA == 1 and pinB == 0:
        fase = 4
    
    if ultima_fase < fase:
        contador += 1
        updated = True
    elif fase == 1 and ultima_fase == 4:
        contador += 1
        updated = True
    elif ultima_fase > fase:
        contador_retro += 1
        updated = True
    elif fase == 4 and ultima_fase == 1:
        contador_retro += 1
        updated = True
    
        
    ultima_fase = fase
    
    
    
def imprimir_resultado():
    global updated
    if updated == True:
        print("Contador|",contador,"|")
        print("Contador Retroceso|",contador_retro,"|")
        updated = False
        
try:
    while True:
        ciclo()
        imprimir_resultado()
except KeyboardInterrupt:
    gp.cleanup()