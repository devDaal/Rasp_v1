from tkinter import *
from tkinter.ttk import Combobox
import RPi.GPIO as gp 

class SensorTest(Frame):
    
    def __init__(self):
        super().__init__()
        self.grid()
        
        # Zona de Widgets de la interfaz
        self.sensor_container = Frame(self,bg='gray', width = '800', height = '412')
        self.sensor_container.grid_propagate(0)
        self.sensor_container.grid()
        
        self.frame_title = Label(self.sensor_container, text='Sensor Test', fg='white',bg='gray',font=("Robot",20,"bold"))
        self.frame_title.grid()
        
        self.sensor_setings_container = LabelFrame(self.sensor_container, bg="#4f4f4f",width='200', pady = 20)
        self.sensor_setings_container.grid(row=1, pady=10, ipady=5,padx=30)
       
        self.quantity_sensors_lbl = Label(self.sensor_setings_container, text='How many sensors?', bg="#4f4f4f",font=("Robot", 16,"bold"))
        self.quantity_sensors_lbl.grid()
       
        values = ["1","2","3","4","5","6"]#,"7","8","9"]
        
        self.quantity_combo = Combobox(self.sensor_setings_container, font=("Robot", 18,"normal"), values = values, width = 3, state = "readonly")
        self.quantity_combo.set("6")
        self.quantity_combo.grid(padx = 10, pady = 10)
               
        self.selected_btn = Button(self.sensor_setings_container, text='Select Sensor(s)', bg='green',fg='White',font=("Robot", 16,"bold"), command=self.get_selected_sensor)
        self.selected_btn.grid()
        
        # Test Frame
        self.sensor_test_container = LabelFrame(self.sensor_container, bg="#4f4f4f", pady = 20, width = '400', height = '260')
        self.sensor_test_container.grid_propagate(0)
        self.sensor_test_container.grid(row=1, column=1, pady=10, ipady=5,padx=30)
        
        self.btns_container = Frame(self.sensor_test_container,bg = "#4f4f4f")
        self.btns_container.grid(column = 0, row = 1, padx = (10,0), pady = '10')
        
        self.lbls_container = Frame(self.sensor_test_container, bg = '#4f4f4f', width = 250, height = 150)
        self.lbls_container.grid_propagate(0)
        self.lbls_container.grid(column = 1, row = 1)
        
        self.test_title = Label(self.sensor_test_container, text='Test', bg="#4f4f4f",font=("Robot", 20,"bold"))
        self.test_title.grid(column = 0, row = 0)
        
        self.sensor_test_start_btn = Button(self.btns_container, text='START', bg='green', fg='white',font=("Robot",16,"bold"),width='6',command=self.start_btn_sensor)
        self.sensor_test_start_btn.grid()
        
        self.sensor_test_stop_btn = Button(self.btns_container, text='STOP', bg='red', fg='white',font=("Robot",16,"bold"), width='6',command=self.stop_btn_sensor)
        self.sensor_test_stop_btn.grid(pady = (10,0))
        
        self.sensor_test_restart_btn = Button(self.btns_container, text='RESTART', bg='orange', fg='white',font=("Robot",15,"bold"), width='6',command=self.restart_btn_sensor)
        self.sensor_test_restart_btn.grid(pady=(10,10))
        
        self.pin_11_lbl = Label(self.lbls_container, text=' PIN 11', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_11_lbl.grid(row=1,column=1,padx=(30,5),pady=5)
        
        self.pin_13_lbl = Label(self.lbls_container, text=' PIN 13', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_13_lbl.grid(row=1,column=2,padx=5,pady=5)
        
        self.pin_15_lbl = Label(self.lbls_container, text=' PIN 15', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_15_lbl.grid(row=1,column=3,padx=5,pady=5)
        
        self.pin_16_lbl = Label(self.lbls_container, text=' PIN 16', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_16_lbl.grid(row=2,column=1,padx=(30,5),pady=5)
        
        self.pin_18_lbl = Label(self.lbls_container, text=' PIN 18', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_18_lbl.grid(row=2,column=2,padx=5,pady=5)
        
        self.pin_22_lbl = Label(self.lbls_container, text=' PIN 22', bg='gray', width=6, height=3,font=("Robot",12,"normal"))
        self.pin_22_lbl.grid(row=2,column=3,padx=5,pady=5)
        
        self.sensor_lbls = [self.pin_11_lbl,
                               self.pin_13_lbl,
                               self.pin_15_lbl,
                               self.pin_16_lbl,
                               self.pin_18_lbl,
                               self.pin_22_lbl]
        
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
#Agregar funcionalidad de que mande un aviso si se activa alguno no requerido??
        
    def restart_btn_sensor(self):
        for i in self.sensor_lbls:
            i['bg'] = 'gray'

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
            
            # Llama de nuevo a update_sensors después de 100 ms
            self.after(100, self.update_sensors)

    # Funcionalidad de botones
    def get_selected_sensor(self):
        for i in self.sensor_lbls:
            i.grid_remove()
        for i in range(int(self.quantity_combo.get())):
            self.sensor_lbls[i].grid()

        
class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Sensor Test")
        self.geometry('800x412+0+0')


if __name__ == "__main__":
    app = App()
    SensorTest().grid()    
    app.mainloop()