from tkinter import *
from tkinter.ttk import Combobox

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
       self.counter = 0
       self.phase = 0
       self.last_phase = 0
       self.updated = False
       
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
       self.combobox_resolution_chossen ['values'] = ('5 um','1 um', '0.5 um', '0.1 um', '0.05 um')
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
       
       self.reference_chk = Checkbutton(self.encoder_setings_container, bg = "#4f4f4f", text = "Reference Mark", font=("Robot", 12), onvalue=1, offvalue=0, variable = self.reference_mode)
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
       self.encoder_test_stop_btn.grid(row=2,column=0,padx=(10,0))
        #----------------------------------------------------------------------1
       self.frame_encoder_1 = Frame(self.encoder_test_container, bg="gray")
       self.frame_encoder_1.grid(padx=5, pady=(10, 0), sticky='ew', row=1, column=2)
       self.frame_encoder_1.columnconfigure(0, weight=1)

       self.lbl_encoder_1 = Label(self.encoder_test_container, text='Distance (X axis):', bg="#4f4f4f", fg='black', font=("Robot", 15, "normal"))
       self.lbl_encoder_1.grid(row=1, column=1, pady=(10, 10))

       self.distance_lbl_encoder_1 = Label(self.frame_encoder_1, text='       1', bg="gray", fg='black', font=("Robot", 15, "normal"))
       self.distance_lbl_encoder_1.grid(sticky='e')
        #---------------------------------------------------------------------2
       self.frame_encoder_2 = Frame(self.encoder_test_container, bg="gray")
       self.frame_encoder_2.grid(padx=5, pady=(10, 0), sticky='ew', row=2, column=2)
       self.frame_encoder_2.columnconfigure(0, weight=1)

       self.lbl_encoder_2 = Label(self.encoder_test_container, text='Distance (Y axis):', bg="#4f4f4f", fg='black', font=("Robot", 15, "normal"))
       self.lbl_encoder_2.grid(row=2, column=1, pady=(10, 10))

       self.distance_lbl_encoder_2 = Label(self.frame_encoder_2, text='       2', bg="gray", fg='black', font=("Robot", 15, "normal"))
       self.distance_lbl_encoder_2.grid(sticky='e')
       #----------------------------------------------------------------------3
       self.frame_encoder_3 = Frame(self.encoder_test_container, bg="gray")
       self.frame_encoder_3.grid(padx=5, pady=(10, 0), sticky='ew', row=3, column=2)
       self.frame_encoder_3.columnconfigure(0, weight=1)

       self.lbl_encoder_3 = Label(self.encoder_test_container, text='Distance (Z axis) :', bg="#4f4f4f", fg='black', font=("Robot", 15, "normal"))
       self.lbl_encoder_3.grid(row=3, column=1, pady=(10, 10))

       self.distance_lbl_encoder_3 = Label(self.frame_encoder_3, text='       3', bg="gray", fg='black', font=("Robot", 15, "normal"))
       self.distance_lbl_encoder_3.grid(sticky='e')
       #----------------------------------------------------------------------GPIO pins-----------------------------------------------------------------------------------------------
       
       gp.setmode(gp.BOARD)
       self.read_pin_15 = 15
       self.read_pin_16 = 16
       gp.setup(self.read_pin_15, gp.IN)
       gp.setup(self.read_pin_16, gp.IN)
       
       self.encoder_start_mode = False
       
       #---------------------------------------------------------------------------Methods--------------------------------------------------------------------------------------------
       
    def update_encoder_settings(self):
        self.encoder_test_type = self.digital_selected.get()
        self.updated_reference_mode = self.reference_mode.get()
        self.updated_limit_mode = self.limit_mode.get()
        self.show_hide_ammount()
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
    def start_btn_encoder(self):
        pass
    def stop_btn_encoder(self):
        pass
    def distance_counter_x(self):
        pass
    def cycle (self):
        self.pinA = gp.input(A)
        self.pinB = gp.input(B)
        if self.pinA == 0 and self.pinB == 0:
            self.phase = 1
        elif self.pinA == 0 and self.pinB == 1:
            self.phase = 2
        elif self.pinA == 1 and self.pinB == 1:
            self.phase = 3
        elif self.pinA == 1 and self.pinB == 0:
            self.phase = 4
        if (ultima_fase == 1 and self.phase == 2) or (ultima_fase == 2 and self.phase == 3) or \
           (ultima_fase == 3 and self.phase == 4) or (ultima_fase == 4 and self.phase == 1):
            contador += 1
            updated = True

    # Actualizar el contador de retroceso si la fase disminuye en sentido antihorario
        elif (ultima_fase == 1 and fase == 4) or (ultima_fase == 4 and fase == 3) or \
             (ultima_fase == 3 and fase == 2) or (ultima_fase == 2 and fase == 1):
            contador -= 1
            updated = True   
        
class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Encoder Test")


if __name__ == "__main__":
    app = App()
    Encoder(app).grid()    
    app.mainloop()