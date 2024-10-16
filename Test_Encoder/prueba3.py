import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO
PIN_A = 17  # Pin GPIO para la señal A del encoder
PIN_B = 27  # Pin GPIO para la señal B del encoder

# Variables globales
contador = 0  # Almacena el conteo de pulsos
estado_anterior_A = 0  # Último estado leído en la señal A

# Configuración del modo GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Entrada con pull-up
GPIO.setup(PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Entrada con pull-up

def callback_A(channel):
    """Manejador de interrupciones para la señal A."""
    global contador, estado_anterior_A
    estado_A = GPIO.input(PIN_A)  # Leer el estado actual de A
    estado_B = GPIO.input(PIN_B)  # Leer el estado actual de B

    # Determinar la dirección del movimiento
    if estado_A != estado_anterior_A:  # Detecta un cambio en A
        if estado_A == estado_B:
            contador += 1  # Movimiento positivo
        else:
            contador -= 1  # Movimiento negativo

        print(f"Posición actual: {contador}")

    estado_anterior_A = estado_A  # Actualizar el estado anterior

# Configuración de interrupciones
GPIO.add_event_detect(PIN_A, GPIO.BOTH, callback=callback_A)  # Detectar cambios en A

try:
    print("Iniciando la lectura del encoder. Presiona Ctrl+C para detener.")
    while True:
        time.sleep(0.1)  # Espera para reducir la carga del CPU

except KeyboardInterrupt:
    print("\nFinalizando el programa...")

finally:
    GPIO.cleanup()  # Liberar los pines GPIO