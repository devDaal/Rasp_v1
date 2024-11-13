import threading
from tkinter import *
from tkinter.ttk import Combobox
import RPi.GPIO as gp

class Encoder(Frame):
    def __init__(self,container):
        super().__init__(container)
        self.grid()
       #-------------------------------------------------------------------Frame & Title----------------------------------------------------------------------------------------------
       
        self.encoder_container= Frame(self,bg='gray',padx=100,pady=10)
        self.encoder_container.pack(expand="True", fill='both')
       
        self.encoder_label=Label(self.encoder_container, text="Encoders",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
        self.encoder_label.grid(pady=5)
    
       #-------------------------------------------------------------------------Variables--------------------------------------------------------------------------------------------
       
        self.encoder_resolution_chosen = StringVar()
        self.encoder_resolution_chosen.set('1 um')
        self.encoder_ammount_chosen = StringVar()
        self.encoder_ammount_chosen.set('1')
        self.digital_selected = StringVar()
        self.digital_selected.set(1)
        self.limit_mode = IntVar()
        self.reference_mode = IntVar()
        self.updated_reference_mode = False
       
        self.resolution_values = {
           "5 um":"50",
           "1 um":"250",
           "0.5 um":"500",
           "0.1 um":"2500",
           "0.05 um":"5000"
           }
              
       #------------------------------------------------------------------------Settings----------------------------------------------------------------------------------------------
       
        self.encoder_setings_container = LabelFrame(self.encoder_container, bg="#4f4f4f",width='200', height='200',fg="white", pady = 20)
        self.encoder_setings_container.grid(row=1, pady=10, ipady=10)
       
        self.ammount_lbl = Label(self.encoder_setings_container,text='How many encoders?', bg="#4f4f4f",font=("Robot", 16,"bold"))
        self.ammount_lbl.grid()#sticky='ew')
       
        self.combobox_ammount_chossen = Combobox(self.encoder_setings_container,state='readonly', width = 15,font=("Robot", 16,"bold"), textvariable = self.encoder_ammount_chosen)
        self.combobox_ammount_chossen ['values'] = ('1','2','3')
        self.combobox_ammount_chossen.grid(row=1, padx=10)
        self.combobox_ammount_chossen.current()
       
        self.types_lbl = Label(self.encoder_setings_container,text='Resolution:', bg="#4f4f4f",font=("Robot", 16,"bold"))
        self.types_lbl.grid()#sticky='ew')
       
        self.combobox_resolution_chossen = Combobox(self.encoder_setings_container,state='readonly', width = 15,font=("Robot", 16,"bold"), textvariable = self.encoder_resolution_chosen)
        self.combobox_resolution_chossen ['values'] = list(self.resolution_values.keys())
        self.combobox_resolution_chossen.grid(row=3, padx=10)
        self.combobox_resolution_chossen.current()
       
       #--------------------------------------------------------------------------
       
        self.digital_encoder_lbl = Label(self.encoder_setings_container, text='Encoder Type:', bg="#4f4f4f",font=("Robot", 16,"bold"))
        self.digital_encoder_lbl.grid(pady=(10,0))
       
        values = {"Analog Encoder" : "1",
                "Digital Encoder" : "2"}
       
        for (text, value) in values.items():
            temp_radio = Radiobutton(self.encoder_setings_container,bg="#4f4f4f", text = text, font=("Robot", 12,"normal"), variable = self.digital_selected,value = value)#,command=self.click_btn_radios)
            temp_radio.grid()
       
       #--------------------------------------------------------------------------
        
        self.reference_chk = Checkbutton(self.encoder_setings_container, bg = "#4f4f4f", text = "Reference Mark", font=("Robot", 12), onvalue=True, offvalue=False, variable = self.reference_mode)
        self.reference_chk.grid(pady=(10,0))  
       
       #--------------------------------------------------------------------------
       
        self.limit_chk = Checkbutton(self.encoder_setings_container, bg = "#4f4f4f", text = "Limit", font=("Robot", 12), onvalue=1, offvalue=0, variable = self.limit_mode)
        self.limit_chk.grid(pady=10)
       
       #--------------------------------------------------------------------------
       
        self.update_btn = Button(self.encoder_setings_container, text='Update Settings', bg='green',fg='White',font=("Robot", 14,"bold"), command=self.update_encoder_settings)
        self.update_btn.grid()
        
       #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       
        self.encoder_exit_btn = Button(self.encoder_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
        self.encoder_exit_btn.grid()
       #-----------------------------------------------------------------------------Test---------------------------------------------------------------------------------------------
        
        self.encoder_test_container = LabelFrame(self.encoder_container, bg="#4f4f4f", font=("Robot", 25, "bold"))
        self.encoder_test_container.grid(row=1, column=1, padx=(50, 10), sticky='ew')

        self.encoder_test_title = Label(self.encoder_test_container, text='Test', bg="#4f4f4f", fg='White', font=("Robot", 25, "bold"))
        self.encoder_test_title.grid(column=1)
       
        self.encoder_test_start_btn = Button(self.encoder_test_container, text='START', bg='green', fg='white',font=("Robot",16,"bold"),width='6',command=self.start_btn_encoder)
        self.encoder_test_start_btn.grid(row=1,column=0,padx=(10,0))
        
        self.encoder_test_stop_btn = Button(self.encoder_test_container, text='STOP', bg='red', fg='white',font=("Robot",16,"bold"), width='6',command=self.stop_btn_encoder)
        self.encoder_test_stop_btn.grid(row=2,column=0,padx=(10,0),pady=(10,0))
       
        self.encoder_test_restart_btn = Button(self.encoder_test_container, text='ORIGIN', bg='orange', fg='white',font=("Robot",16,"bold"), width='6',command=self.restart_btn_encoder)
        self.encoder_test_restart_btn.grid(row=3,column=0,padx=(10,0),pady=10)
       
        self.invisible_lbl = Label(self.encoder_test_container,bg="#4f4f4f", text=" ")
        self.invisible_lbl.grid(column = 3, row = 0,padx= 25) #Don´t mind this label it's here just because I couldn't
                                                             #choose the width of the frame and I didn't want the frame
                                                             #to be changing it's size because of the RM lbls
       
        #----------------------------------------------------------------------1------------------------------------
        self.frame_encoder_1 = Frame(self.encoder_test_container, bg="gray")
        self.frame_encoder_1.grid(padx=5, pady=(10, 0), sticky='ew', row=1, column=2)
        self.frame_encoder_1.columnconfigure(0, weight=1)
 
        self.lbl_encoder_1 = Label(self.encoder_test_container, text='Position 1(mm):', bg="#4f4f4f", fg='black', font=("Robot", 15, "normal"))
        self.lbl_encoder_1.grid(row=1, column=1, pady=(10, 10))

        self.distance_lbl_encoder_1 = Label(self.frame_encoder_1, text='', bg="gray", fg='black', font=("Robot", 15, "normal"),width=7)
        self.distance_lbl_encoder_1.grid(sticky='e')
        #---------------------------------------------------------------------2-------------------------------------------
        self.frame_encoder_2 = Frame(self.encoder_test_container, bg="gray")
        self.frame_encoder_2.grid(padx=5, pady=(10, 0), sticky='ew', row=2, column=2)
        self.frame_encoder_2.columnconfigure(0, weight=1)

        self.lbl_encoder_2 = Label(self.encoder_test_container, text='Position 2(mm):', bg="#4f4f4f", fg='black', font=("Robot", 15, "normal"))
        self.lbl_encoder_2.grid(row=2, column=1, pady=(10, 10))

        self.distance_lbl_encoder_2 = Label(self.frame_encoder_2, text='', bg="gray", fg='black', font=("Robot", 15, "normal"))
        self.distance_lbl_encoder_2.grid(sticky='e')
       #----------------------------------------------------------------------3------------------------------------
        self.frame_encoder_3 = Frame(self.encoder_test_container, bg="gray")
        self.frame_encoder_3.grid(padx=5, pady=(10, 0), sticky='ew', row=3, column=2)
        self.frame_encoder_3.columnconfigure(0, weight=1)

        self.lbl_encoder_3 = Label(self.encoder_test_container, text='Position 3(mm):', bg="#4f4f4f", fg='black', font=("Robot", 15, "normal"))
        self.lbl_encoder_3.grid(row=3, column=1, pady=(10, 10))

        self.distance_lbl_encoder_3 = Label(self.frame_encoder_3, text='', bg="gray", fg='black', font=("Robot", 15, "normal"))
        self.distance_lbl_encoder_3.grid(sticky='e')
       
       #------------------------------------------------------------------------
       
        self.ref_mark_1_lbl = Label(self.encoder_test_container, text=' RM1', bg='gray',width=4, font=("Robot",10,"normal"))
        self.ref_mark_1_lbl.grid(row=1,column=3,pady=(5,0),padx = 5)
        self.ref_mark_1_lbl.grid_remove()
       
        self.ref_mark_2_lbl = Label(self.encoder_test_container, text=' RM2', bg='gray',width=4, font=("Robot",10,"normal"))
        self.ref_mark_2_lbl.grid(row=2,column=3,pady=(5,0),padx = 5)
        self.ref_mark_2_lbl.grid_remove()
       
        self.ref_mark_3_lbl = Label(self.encoder_test_container, text=' RM3', bg='gray',width=4, font=("Robot",10,"normal"))
        self.ref_mark_3_lbl.grid(row=3,column=3,pady=(5,0),padx = 5)
        self.ref_mark_3_lbl.grid_remove()
       
       #----------------------------------------------------------------------GPIO pins-----------------------------------------------------------------------------------------------
       
        gp.setmode(gp.BOARD)
        self.A = 35
        self.B = 36
        self.C = 37
        gp.setup(self.A, gp.IN)
        gp.setup(self.B, gp.IN)
        gp.setup(self.C, gp.IN)
        self.lastA = None
        self.lastB = None
        self.lastC = None
        self.positive_counter = 0
        self.negative_counter = 0
        self.cycle_status = True
        self.position = 0
        self.absolute_counter = 0
        self.encoder_start_mode = False
        self.resolution = 1
       
        # Iniciar hilo para el encoder
        self.encoder_thread = threading.Thread(target=self.cycle)
        self.encoder_thread.daemon = True  # Permite terminar el hilo al cerrar la app
        self.running_status = True
        self.encoder_thread.start()
       
       
       
       #---------------------------------------------------------------------------Methods--------------------------------------------------------------------------------------------
       
    def update_encoder_settings(self):
        self.encoder_test_type = self.digital_selected.get()
        self.updated_reference_mode = self.reference_mode.get()
        self.updated_limit_mode = self.limit_mode.get()
        self.show_hide_ammount()
        self.resolution = self.resolution_values.get(self.combobox_resolution_chossen.get())
        self.ref_mark_1_lbl['bg'] = 'grey'
        self.ref_mark_2_lbl['bg'] = 'grey'
        self.ref_mark_3_lbl['bg'] = 'grey'
        self.show_hide_ref_mark()
        """print(self.encoder_test_type)
        print("\n")
        print(self.updated_reference_mode)
        print("\n")
        print(self.updated_limit_mode)
        print("\n")"""
        
    def show_hide_ammount(self):
        if self.combobox_ammount_chossen.current() == 0:
            self.frame_encoder_1.grid()
            self.lbl_encoder_1.grid()
            self.distance_lbl_encoder_1.grid()
            self.frame_encoder_2.grid_remove()
            self.lbl_encoder_2.grid_remove()
            self.distance_lbl_encoder_2.grid_remove()
            self.frame_encoder_3.grid_remove()
            self.lbl_encoder_3.grid_remove()
            self.distance_lbl_encoder_3.grid_remove()
        elif self.combobox_ammount_chossen.current() == 1:
            self.frame_encoder_1.grid()
            self.lbl_encoder_1.grid()
            self.distance_lbl_encoder_1.grid()
            self.frame_encoder_2.grid()
            self.lbl_encoder_2.grid()
            self.distance_lbl_encoder_2.grid()
            self.frame_encoder_3.grid_remove()
            self.lbl_encoder_3.grid_remove()
            self.distance_lbl_encoder_3.grid_remove()
        else:
            self.frame_encoder_1.grid()
            self.lbl_encoder_1.grid()
            self.distance_lbl_encoder_1.grid()
            self.frame_encoder_2.grid()
            self.lbl_encoder_2.grid()
            self.distance_lbl_encoder_2.grid()
            self.frame_encoder_3.grid()
            self.lbl_encoder_3.grid()
            self.distance_lbl_encoder_3.grid()
            
    def show_hide_ref_mark(self):
        if self.updated_reference_mode:
            if self.combobox_ammount_chossen.current() == 0:
                self.ref_mark_1_lbl.grid()
                self.ref_mark_2_lbl.grid_remove()
                self.ref_mark_3_lbl.grid_remove()
                
            elif self.combobox_ammount_chossen.current() == 1:
                self.ref_mark_1_lbl.grid()
                self.ref_mark_2_lbl.grid()
                self.ref_mark_3_lbl.grid_remove()
            else:
                self.ref_mark_1_lbl.grid()
                self.ref_mark_2_lbl.grid()
                self.ref_mark_3_lbl.grid()
        else:
            self.ref_mark_1_lbl.grid_remove()
            self.ref_mark_2_lbl.grid_remove()
            self.ref_mark_3_lbl.grid_remove()
            
            
    def start_btn_encoder(self):
        self.cycle_status = True
        self.update_ui()
        
    def stop_btn_encoder(self):
        self.cycle_status = False
        
    def restart_btn_encoder(self):
        self.positive_counter = 0
        self.negative_counter = 0
        self.position = 0
        self.absolute_counter = 0
        
    def distance_counter_x(self):
        pass
    def cycle (self):
        while self.running_status:
            self.pinB = gp.input(self.B)
            self.pinA = gp.input(self.A)
            if self.updated_reference_mode:
                self.pinC = gp.input(self.C)
                #Aqui mas o menos debe de ir mostrar y ocultar el cuadrito
                if self.lastC != self.pinC:
                    if self.pinC == 1:
                        self.ref_mark_1_lbl['bg'] = 'green'
                    self.lastC = self.pinC
            
            if self.lastB != self.pinB or self.lastA != self.pinA:
                if self.lastA == 0 and self.lastB == 0:
                    if self.pinA == 0 and self.pinB == 1:
                        self.negative_counter += 1
                        #print("Negativo")
                    elif self.pinB == 0 and self.pinA == 1:
                        self.positive_counter += 1
                        #print("Positivo")
            self.lastA = self.pinA
            self.lastB = self.pinB
            self.absolute_counter = self.positive_counter - self.negative_counter
            self.position = self.absolute_counter/int(self.resolution)
        
    def update_ui(self):
        if self.cycle_status:
            self.distance_lbl_encoder_1.config(text=f"{self.position}")
            self.after(50, self.update_ui)
        
        
           
        
class App(Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Encoder Test")
        
    def on_closing(self):
        self.destroy()
        self.running_status = False


if __name__ == "__main__":
    app = App()
    Encoder(app).grid()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()