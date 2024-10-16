import RPi.GPIO as gp
gp.setmode(gp.BOARD)
A = 15
B = 16
contador = 0
fase = 0
ultima_fase = 0
gp.setup(A, gp.IN)
gp.setup(B, gp.IN)

try:
    while True:
        pinA = gp.input(A)
        pinB = gp.input(B)
        if pinA == 0 and pinB == 0:
            fase = 1
            print("Fase :",fase)
        elif pinA == 0 and pinB == 1:
            fase = 2
            print("Fase :",fase)
        elif pinA == 1 and pinB == 1:
            fase = 3
            print("Fase :",fase)
        elif pinA == 1 and pinB == 0:
            fase = 4
            print("Fase :",fase)
        
        if ultima_fase < fase:
            contador += 1
        elif fase == 1 and ultima_fase == 4:
            contador += 1
        elif ultima_fase > fase:
            contador-= 1
        elif fase == 4 and ultima_fase == 1:
            contador -= 1
        
            
        ultima_fase = fase
 
        print("Contador|",contador,"|")
   
        

except KeyboardInterrupt:
    gp.cleanup()
            
       
    
            #IDEA para lectura: leer qué tanto tiempo transcurre en los cambios de fase y hacer un cálculo
            # matemático para estimar la frecuencia y por lo tanto el avance
            #IDEA para lectura: 