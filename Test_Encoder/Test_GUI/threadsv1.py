import threading
import time
import tkinter as tk
import RPi.GPIO as gp

class EncoderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Encoder Position")
        
        # Configuración de la interfaz
        self.label = tk.Label(self, text="Position: 0", font=("Helvetica", 16))
        self.label.pack(pady=20)
        
        # Variables del encoder
        self.position = 0
        self.is_running = True
        
        # Configuración de pines GPIO
        gp.setmode(gp.BOARD)
        self.pin_A = 15
        self.pin_B = 16
        gp.setup(self.pin_A, gp.IN)
        gp.setup(self.pin_B, gp.IN)

        # Iniciar hilo para el encoder
        self.encoder_thread = threading.Thread(target=self.read_encoder)
        self.encoder_thread.daemon = True  # Permite terminar el hilo al cerrar la app
        self.encoder_thread.start()
        
        # Actualizar la UI cada 50 ms
        self.update_ui()

    def read_encoder(self):
        last_position = 0
        while self.is_running:
            # Lee los pines del encoder y determina el movimiento
            current_A = gp.input(self.pin_A)
            current_B = gp.input(self.pin_B)

            if current_A and not current_B:   # Ejemplo de lógica de movimiento hacia adelante
                self.position += 1
            elif not current_A and current_B: # Ejemplo de lógica de movimiento hacia atrás
                self.position -= 1
            
            last_position = self.position
            
            # Retardo breve para aliviar CPU, puedes ajustar este valor según precisión
            time.sleep(0.001)

    def update_ui(self):
        # Actualiza la posición en la UI
        self.label.config(text=f"Position: {self.position}")
        
        # Llama a update_ui de nuevo después de 50 ms
        self.after(50, self.update_ui)

    def on_closing(self):
        # Apaga el hilo del encoder y cierra GPIO
        self.is_running = False
        gp.cleanup()
        self.destroy()

if __name__ == "__main__":
    app = EncoderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
