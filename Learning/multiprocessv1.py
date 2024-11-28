from tkinter import *
from multiprocessing import Process, Event, Queue
import time
from tkinter.messagebox import askyesnocancel


def gpio_listener(process_id, event, interval, queue):
    """
    Función para simular la lectura de pines GPIO.
    Envía los valores leídos al Queue para ser procesados por la GUI.
    """
    print(f"Proceso {process_id} iniciado.")
    counter = 0
    while True:
        event.wait()  # Espera hasta que se active el evento
        counter += 1  # Simula un conteo de entradas GPIO
        #print(f"[{process_id}] Leyendo pines GPIO... {counter}")
        queue.put((process_id, counter))  # Envía el valor al Queue
        time.sleep(interval)  # Simula el tiempo entre lecturas


class Page(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.container = Frame(self, bg='blue')
        self.container.pack(expand=True, fill='both')

        self.title = Label(self.container, text='GPIO Multiprocessing', fg='white', bg='blue')
        self.title.grid()

        self.btn_start = Button(self.container, text="Start", command=self.iniciar_procesos)
        self.btn_start.grid()

        self.btn_stop = Button(self.container, text="Stop", command=self.detener_procesos)
        self.btn_stop.grid()

        # Etiquetas para mostrar contadores
        self.label_x = Label(self.container, text="Contador X: 0", bg="white")
        self.label_x.grid(row=4)

        self.label_y = Label(self.container, text="Contador Y: 0", bg="white")
        self.label_y.grid(row=5)
        
        self.exit_btn = Button(self.container, text="Exit",command=self.exit_page)
        self.exit_btn.grid(row=3)

        # Variables para procesos
        self.processes = []
        self.events = []
        self.queues = []

        # Configurar procesos GPIO
        self.configurar_procesos()

        # Actualizar GUI periódicamente
        self.after(100, self.actualizar_gui)

    def configurar_procesos(self):
        """
        Configura los procesos, eventos y colas para manejar los juegos de pines GPIO.
        """
        juegos_gpio = [
            ("Juego X", 0.01),  # (Nombre, Intervalo de lectura)
            ("Juego Y", 0.1)
        ]

        for juego, intervalo in juegos_gpio:
            event = Event()  # Evento para controlar pausa/reanudación
            queue = Queue()  # Cola para recibir datos del proceso
            process = Process(target=gpio_listener, args=(juego, event, intervalo, queue))
            process.daemon = True  # Terminar el proceso con la aplicación

            self.events.append(event)
            self.queues.append(queue)
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

    def actualizar_gui(self):
        """
        Revisa las colas de datos y actualiza la interfaz con los contadores de cada proceso.
        """
        for idx, queue in enumerate(self.queues):
            while not queue.empty():
                process_id, counter = queue.get()
                if process_id == "Juego X":
                    self.label_x.config(text=f"Contador X: {counter}")
                elif process_id == "Juego Y":
                    self.label_y.config(text=f"Contador Y: {counter}")

        self.after(100, self.actualizar_gui)  # Llama a sí misma cada 100ms
        
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
            frame = F(self)
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
    
        