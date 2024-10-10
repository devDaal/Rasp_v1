from tkinter import *
import RPi.GPIO as gp 

class SensorTest(Frame):
    
    def __init__(self, container):
        super().__init__(container)
        self.grid()
        
        # Zona de Widgets de la interfaz
        self.sensor_container = Frame(self,bg='blue')
        self.sensor_container.grid()
        
        self.frame_title = Label(self.sensor_container, text='Sensor Test', fg='white',bg='blue',font=("Robot",20,"bold"))
        self.frame_title.grid()
        
        self.sensor_selected = IntVar()
        
        self.sensor_setings_container = LabelFrame(self.sensor_container, bg="#4f4f4f",width='200', pady = 20)
        self.sensor_setings_container.grid(row=1, pady=10, ipady=5,padx=30)
       
        self.quantity_sensors_lbl = Label(self.sensor_setings_container, text='How many sensors?', bg="#4f4f4f",font=("Robot", 16,"bold"))
        self.quantity_sensors_lbl.grid()
       
        values = {"1" : "1",
                  "2" : "2",
                  "3" : "3",
                  "4" : "4",
                  "5" : "5",
                  "6" : "6",
                  "7" : "7",
                  "8" : "8",
                  "9" : "9"}
        
        for (text, value) in values.items():
            temp_radio = Radiobutton(self.sensor_setings_container,bg="#4f4f4f", text = text, font=("Robot", 18,"normal"), variable = self.sensor_selected,value = value)
            temp_radio.grid()
       
        self.selected_btn = Button(self.sensor_setings_container, text='Select Sensor(s)', bg='green',fg='White',font=("Robot", 16,"bold"), command=self.get_selected_sensor)
        self.selected_btn.grid()
        
        # Test Frame
        self.sensor_test_container = LabelFrame(self.sensor_container, bg="#4f4f4f", pady = 20)
        self.sensor_test_container.grid(row=1, column=1, pady=10, ipady=5,padx=30)
        
        self.test_title = Label(self.sensor_test_container, text='Test', bg="#4f4f4f",font=("Robot", 20,"bold"))
        self.test_title.grid()
        
        self.sensor_test_start_btn = Button(self.sensor_test_container, text='START', bg='green', fg='white',font=("Robot",16,"bold"),width='6',command=self.start_btn_sensor)
        self.sensor_test_start_btn.grid(padx=(10,0))
        
        self.sensor_test_stop_btn = Button(self.sensor_test_container, text='STOP', bg='red', fg='white',font=("Robot",16,"bold"), width='6',command=self.stop_btn_sensor)
        self.sensor_test_stop_btn.grid(padx=(10,0))
        
        self.pin_11_lbl = Label(self.sensor_test_container, text=' PIN 11', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_11_lbl.grid(row=1,column=1,padx=(30,5),pady=5)
        
        self.pin_13_lbl = Label(self.sensor_test_container, text=' PIN 13', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_13_lbl.grid(row=1,column=2,padx=5,pady=5)
        
        self.pin_15_lbl = Label(self.sensor_test_container, text=' PIN 15', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_15_lbl.grid(row=1,column=3,padx=5,pady=5)
        
        self.pin_16_lbl = Label(self.sensor_test_container, text=' PIN 16', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_16_lbl.grid(row=2,column=1,padx=(30,5),pady=5)
        
        self.pin_18_lbl = Label(self.sensor_test_container, text=' PIN 18', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_18_lbl.grid(row=2,column=2,padx=5,pady=5)
        
        self.pin_22_lbl = Label(self.sensor_test_container, text=' PIN 22', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_22_lbl.grid(row=2,column=3,padx=5,pady=5)
        
        # Configuración de los pines GPIO
        gp.setmode(gp.BOARD)
        self.read_pin_11 = 11
        self.read_pin_13 = 13
        self.read_pin_15 = 15
        self.read_pin_16 = 16
        self.read_pin_18 = 18
        self.read_pin_22 = 22
        gp.setup(self.read_pin_11, gp.IN)
        gp.setup(self.read_pin_13, gp.IN)
        gp.setup(self.read_pin_15, gp.IN)
        gp.setup(self.read_pin_16, gp.IN)
        gp.setup(self.read_pin_18, gp.IN)
        gp.setup(self.read_pin_22, gp.IN)
        
        self.start_mode = False  # Estado inicial
        
    def start_btn_sensor(self):
        """Inicia la lectura de los pines y actualiza los colores."""
        self.start_mode = True
        self.update_sensors()

    def stop_btn_sensor(self):
        """Detiene la lectura de los pines."""
        self.start_mode = False

    def update_sensors(self):
        """Actualiza el estado de los sensores y cambia el color de los labels."""
        if self.start_mode:
            self.pin_11 = gp.input(self.read_pin_11)
            self.pin_13 = gp.input(self.read_pin_13)
            self.pin_15 = gp.input(self.read_pin_15)
            self.pin_16 = gp.input(self.read_pin_16)
            self.pin_18 = gp.input(self.read_pin_18)
            self.pin_22 = gp.input(self.read_pin_22)
            
            # Actualiza colores según el estado de los pines
            self.pin_11_lbl['bg'] = 'green' if self.pin_11 else 'gray'
            self.pin_13_lbl['bg'] = 'green' if self.pin_13 else 'gray'
            self.pin_15_lbl['bg'] = 'green' if self.pin_15 else 'gray'
            self.pin_16_lbl['bg'] = 'green' if self.pin_16 else 'gray'
            self.pin_18_lbl['bg'] = 'green' if self.pin_18 else 'gray'
            self.pin_22_lbl['bg'] = 'green' if self.pin_22 else 'gray'
            
            # Llama de nuevo a update_sensors después de 10 ms
            self.after(10, self.update_sensors)

    # Funcionalidad de botones
    def get_selected_sensor(self):
        self.test_amount_sensor = self.sensor_selected.get()
        
class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Sensor Test")


if __name__ == "__main__":
    app = App()
    SensorTest(app).grid()    
    app.mainloop()