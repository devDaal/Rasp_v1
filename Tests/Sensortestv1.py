from tkinter import *
#import RPI.GPIO as gp
import time

class SensorTest(Frame):
    
    def __init__(self, container):
        super().__init__(container)
        self.grid()
        #---------------------------------------------------------------Zona de Widgets de la interfaz-----------------------------------------------------------------------
        self.sensor_container = Frame(self,bg='blue')
        self.sensor_container.grid()
        
        self.frame_title = Label(self.sensor_container, text='Sensor Test', fg='white',bg='blue',font=("Robot",20,"bold"))
        self.frame_title.grid()
        
        self.sensor_selected = IntVar()
        
        self.sensor_setings_container = LabelFrame(self.sensor_container, bg="#4f4f4f",width='200', pady = 20)
        self.sensor_setings_container.grid(row=1, pady=10, ipady=5,padx=30)
       
        self.quantity_sensors_lbl = Label(self.sensor_setings_container, text='How many sensors?', bg="#4f4f4f",font=("Robot", 16,"bold"))
        self.quantity_sensors_lbl.grid()
       
       #-----------------------------------------------------------
       
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
            temp_radio = Radiobutton(self.sensor_setings_container,bg="#4f4f4f", text = text, font=("Robot", 18,"normal"), variable = self.sensor_selected,value = value)#,command=self.click_btn_radios)
            temp_radio.grid()
       
       #-----------------------------------------------------------
       
        self.selected_btn = Button(self.sensor_setings_container, text='Select Sensor(s)', bg='green',fg='White',font=("Robot", 16,"bold"), command=self.get_selected_sensor)
        self.selected_btn.grid()
        
        #------------------------------------------------------------Test Frame--------------------------------
        
        self.sensor_test_container = LabelFrame(self.sensor_container, bg="#4f4f4f", pady = 20)
        self.sensor_test_container.grid(row=1, column=1, pady=10, ipady=5,padx=30)
        
        self.test_title = Label(self.sensor_test_container, text='Test', bg="#4f4f4f",font=("Robot", 20,"bold"))
        self.test_title.grid()
        
        self.sensor_test_start_btn = Button(self.sensor_test_container, text='START', bg='green', fg='white',font=("Robot",16,"bold"),width='6',command=self.start_btn_sensor)
        self.sensor_test_start_btn.grid(padx=(10,0))
        
        self.sensor_test_stop_btn = Button(self.sensor_test_container, text='STOP', bg='red', fg='white',font=("Robot",16,"bold"), width='6',command=self.stop_btn_sensor)
        self.sensor_test_stop_btn.grid(padx=(10,0))
        
        #Crear diccionario de los 9 pines que se pueden utilizar
        #Agregar funcionalidad de que seleccione los primeros 'x' pines que seleccione el usuario
        
        #Crear los widgets que representan a las entradas de la rasp (donde se recibe la señal de los sensores)
        
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
        
        
        
        """
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
        
        
    def start_btn_sensor(self):
        self.start_mode = 1
        self.stop_mode = 0
        self.pin_11 = gp.input(self.read_pin_11)
        self.pin_13 = gp.input(self.read_pin_13)
        self.pin_15 = gp.input(self.read_pin_15)
        self.pin_16 = gp.input(self.read_pin_16)
        self.pin_18 = gp.input(self.read_pin_18)
        self.pin_22 = gp.input(self.read_pin_22)
        
        try:
            while self.start_mode == 1:
                if self.pin_11 == 1: self.pin_11_lbl['bg']='green'
                if self.pin_13 == 1: self.pin_13_lbl['bg']='green'
                if self.pin_15 == 1: self.pin_15_lbl['bg']='green'
                if self.pin_16 == 1: self.pin_16_lbl['bg']='green'
                if self.pin_18 == 1: self.pin_18_lbl['bg']='green'
                if self.pin_22 == 1: self.pin_22_lbl['bg']='green'
                self.App.after(10, start_btn_sensor)
        except (self.stop_mode == 0):
            gp.cleanup()
                
    """
        
        #Funcionalidad de los widgets (cambiar el color del widget dependiendo de si se lee 1 o 0 en el puerto)
        #Velocidad de lectura de datos: alta
        #Actualización de los widgets: alta (método .update())
        
        #¿Cómo escribir lo de los pines sin tener que escribir lo mismo tantas veces? ¿se puede usar un diccionario?
        #¿Cómo hacer la funcionalidad de los labels sin tener que escribir lo mismo tantas veces?
       
    
  #--------------------------------------------------------------------Funcionalidad de botones---------------------------------------------------------------------------
    def get_selected_sensor(self):
        self.test_amount_sensor = self.sensor_selected.get()
        
        
    def stop_btn_sensor(self):
        self.stop_mode = 1
        self.start_mode = 0


class App(Tk):
    def __init__(self):
        super().__init__()
        #self.geometry('300x300')
        self.title("Sensor Test")


if __name__ == "__main__":
    app=App()
    SensorTest(app)    
    app.mainloop()