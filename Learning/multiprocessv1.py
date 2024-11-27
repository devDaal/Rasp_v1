from tkinter import *
from tkinter.messagebox import askyesnocancel
from multiprocessing import Process, Event
import time


class Ciclo:
    def __init__(self):
        pass
    def gpio_listener(self,process_id, event, interval):
        """
        Función para simular la lectura de pines GPIO.
        """
        print(f"Proceso {process_id} iniciado.")
        while True:
            event.wait() 
            print(f"[{process_id}] Leyendo pines GPIO...")
            time.sleep(interval)  # Simula el tiempo entre lecturas


class Page(Frame,Ciclo):
    def __init__(self):
        Frame.__init__(self)
        Ciclo.__init__(self)
        self.container = Frame(self, bg='blue')
        self.container.pack(expand=True, fill='both')

        self.title = Label(self.container, text='GPIO Multiprocessing', fg='white', bg='blue')
        self.title.grid()

        self.btn_start = Button(self.container, text="Start", command=self.iniciar_procesos)
        self.btn_start.grid()

        self.btn_stop = Button(self.container, text="Stop", command=self.detener_procesos)
        self.btn_stop.grid()
        
        self.exit_btn = Button(self.container, text="EXIT",command=self.exit_page)
        self.exit_btn.grid()

        # Variables para procesos
        self.processes = []
        self.events = []

        # Configurar procesos GPIO
        self.configurar_procesos()

    def configurar_procesos(self):
        """
        Configura los procesos y eventos para manejar los juegos de pines GPIO.
        """
        juegos_gpio = [
            ("Juego 1", 4),  # (Nombre, Intervalo de lectura)
            ("Juego 2", 8),
            ("Juego 3", 16)
        ]

        for juego, intervalo in juegos_gpio:
            event = Event()  # Evento para controlar pausa/reanudación
            process = Process(target=self.gpio_listener, args=(juego, event, intervalo))
            process.daemon = True  # Terminar el proceso con la aplicación

            self.events.append(event)
            self.processes.append(process)

    def iniciar_procesos(self):
        """
        Inicia los procesos y activa los eventos para que comiencen a leer pines GPIO.
        """
        for process, event in zip(self.processes, self.events):
            if not process.is_alive():
                process.start()  # Inicia el proceso si no está corriendo
            event.set()  # Activa el evento para que el proceso comience a leer

    def detener_procesos(self):
        """
        Detiene la lectura de los procesos (manteniéndolos como listeners).
        """
        for event in self.events:
            event.clear()  # Desactiva el evento, pausando la lectura

    def exit_page(self):
        self.exit_answer = askyesnocancel(title="Warning", icon="warning",
                                          message="Do yoy want to stop reading the encoders? If you stop right now, you will not be able to read again unless you restart the app")
        if self.exit_answer:
            print("Killing processes and Exiting to start page")
        elif self.exit_answer == False:
            print("Exiting to Start Page")
        else:
            pass

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("GPIO Interface")
        self.geometry('300x200')

        container = Frame(self, bg='black')
        container.grid(row=0, column=0, sticky="nsew")

        self.frames = {}
        self.load_frames(Page)

        self.show_frame(Page)

    def load_frames(self, *args):
        for F in args:
            frame = F()
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

    def show_frame(self, frame_to_show):
        frame = self.frames[frame_to_show]
        self.current_frame = frame
        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()