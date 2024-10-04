from tkinter import *
from tkinter import messagebox

class Base():
    def __init__(self):

        self.frames = {}    # Dictionary to hold the frames that we are going to show

    def load_frames(self, *args):
        for F in args:

            frame = F() # Create objects from the classes listed above in the F loop

            self.frames[F] = frame # Save the created objects to our dictionary

            frame.grid(row=0, column=0, sticky="nsew")  # Load the frame objects into a grid stacking them on top of each other
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            
    def show_frame(self, frame_to_show):
        """ 
            Receives a class and look for it in our frames dictionary,
            if we found it then show it as the top screen

            Parameters
            ----------
            frame_to_show: Class type that we want to show 
        """
        frame = self.frames[frame_to_show]  # Look for the class in our dictionary
        self.current_frame = frame  # Set the frame as our current frame variable
        frame.tkraise() # Raise the frame to the top

class App(Base,Tk):
    """
        A class that inherits from the main tkinter class
        and some functions from the Base class
        It is the top object that holds the whole interface
        ...

        Attributes
        ----------
        None
        
        Methods
        -------
        None
    """

    def __init__(self, *args, **kwargs):
        """ 
            Parameters
            ---------
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        Base.__init__(self)
        Tk.__init__(self, *args, **kwargs) # Inherit from the main tkinter class
        

        self.title("Prototype")
        self.resizable(1,1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.port = None
        self.connect_status = 0
        
        self.load_frames(StartPage, Settings, Motor, Encoder, Jogbox, Sensor, PH10)
        self.show_frame(StartPage)  # Frame object to show at the top screen
        
        """self.photo_logo = PhotoImage(file= "icons\its-logo-short.png").subsample(10,10)
        self.iconphoto(True, self.photo_logo)   # Icon that shows on the left corner of the screen"""

        
        
class StartPage(Frame):

    """
        A class that holds the start - main page of the interface
        It inherits from the Frame class of tkinter
        ...

        Attributes
        ----------
        parent : tk class 
            object that is to hold the StartPage object
        
        Methods
        -------
        None
    """

    def __init__(self):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object
        """
        
        Frame.__init__(self)
        self.counter_easter = 0

        self.start_container = Frame(self,bg="gray", padx=152,pady=20)
        self.start_container.pack(expand="True", fill='both')

        self.start_container_title = Frame(self.start_container,bg="gray")
        self.start_container_title.grid(row=0,column=1)
        
        self.easter_egg= Button(self.start_container,borderwidth=0,takefocus="off",bg="gray",activebackground='gray',relief="flat",padx=50,pady=40,
                        command=lambda:self.__easter_egg_deploy(),cursor='watch')
        self.easter_egg.grid(row=0,column=2,padx=(10,0)) 
        
        #-------------------------------------------------------------------------------------Motors--------------------------------------------------------------------------------
        
        self.motor_frame = Frame(self.start_container, bg='gray',height='30', width='30')
        self.motor_frame.grid(row=1, column=2, padx=(50,50), pady=(80,50))
        
        self.motor_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons1\\motor.png").subsample(21,21)
        self.motor_btn = Button(self.motor_frame, image=self.motor_photo,bg= 'gray',command=lambda: app.show_frame(Motor))
        self.motor_btn.image= self.motor_photo
        self.motor_btn.grid(row='0')
        
        self.motor_lbl = Label(self.motor_frame,text='Motors',fg='Black', bg='gray')
        self.motor_lbl.grid(row='1')
        
        
        #-----------------------------------------------------------------------------------Encoders-------------------------------------------------------------------------------
        
        self.encoder_frame = Frame(self.start_container, bg='gray',height='30', width='30')
        self.encoder_frame.grid(row=2, column=2, padx=(50,50), pady=(30,50))
        
        self.encoder_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons1\\encoder2.png").subsample(4,4)
        self.encoder_btn = Button(self.encoder_frame, image=self.encoder_photo, bg= 'gray',command=lambda: app.show_frame(Encoder))
        self.encoder_btn.image= self.encoder_photo
        self.encoder_btn.grid(row='0')
        
        self.encoder_lbl = Label(self.encoder_frame, text='Encoders',fg='Black', bg='gray')
        self.encoder_lbl.grid(row='1')
        
        #------------------------------------------------------------------------------------------Settings-------------------------------------------------------------------------
        
        self.settings_frame = Frame(self.start_container, bg='gray',height='30', width='30')
        self.settings_frame.grid(row=1, column=1, padx=(50,50), pady=(80,50))
        
        self.settings_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons1\\Imagen2.png").subsample(6,6)
        self.settings_btn = Button(self.settings_frame,image=self.settings_photo, bg= 'gray',command=lambda: app.show_frame(Settings))
        self.settings_btn.image= self.settings_photo
        self.settings_btn.grid(row=0)
        
        self.settings_lbl = Label(self.settings_frame, text='Settings',fg='Black', bg='gray')
        self.settings_lbl.grid(row=1)
        
        #--------------------------------------------------------------------------------------PH10 Tester---------------------------------------------------------------------------
        
        self.ph10_frame = Frame(self.start_container, bg='gray',height='30', width='30')
        self.ph10_frame.grid(row=2, column=1, padx=(50,50), pady=(30,50))
        
        self.ph10_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons1\\ph10.png").subsample(4,4)
        self.ph10_btn = Button(self.ph10_frame, bg= 'gray',image=self.ph10_photo,command=lambda: app.show_frame(PH10))
        self.ph10_btn.image= self.ph10_photo
        self.ph10_btn.grid(row=0)
        
        self.ph10_lbl = Label(self.ph10_frame, text='PH10 Tester',fg='Black', bg='gray')
        self.ph10_lbl.grid(row=1)
        
        #----------------------------------------------------------------------------------------Sensors-----------------------------------------------------------------------------
        
        self.sensor_frame = Frame(self.start_container, bg='gray',height='30', width='30')
        self.sensor_frame.grid(row=1, column=0, padx=(50,50), pady=(80,50))
        
        self.sensor_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons1\\sensor.png").subsample(22,22)
        self.sensor_btn = Button(self.sensor_frame, bg= 'gray', image=self.sensor_photo,command=lambda: app.show_frame(Sensor))
        self.sensor_btn.image = self.sensor_photo
        self.sensor_btn.grid(row=0)
        
        self.sensor_lbl = Label(self.sensor_frame, text='Sensors',fg='Black', bg='gray')
        self.sensor_lbl.grid(row=1)
        
        #------------------------------------------------------------------------------------JogBox Tester---------------------------------------------------------------------------
        
    
        self.jogbox_frame = Frame(self.start_container, bg='gray',height='30', width='30')
        self.jogbox_frame.grid(row=2, column=0, padx=(50,50), pady=(30,50))
        
        self.jogbox_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons1\\jogbox.png").subsample(6,6)
        self.jogbox_btn = Button(self.jogbox_frame, bg= 'gray', image=self.jogbox_photo,command=lambda: app.show_frame(Jogbox))
        self.jogbox_btn.image = self.jogbox_photo
        self.jogbox_btn.grid(row=0)
        
        self.jogbox_lbl = Label(self.jogbox_frame, text='JogBox Tester',fg='Black', bg='gray')
        self.jogbox_lbl.grid(row=1)

        
    def __easter_egg_deploy(self):
        """ 
            Protected class 

            Parameters
            ----------
            None
            
        """
        self.counter_easter += 1
        if self.counter_easter == 10:
            self.counter_easter = 0
            messagebox.showinfo("Developers","GUI developed by Alwurts and Daal")

class Settings(Frame):
    def __init__(self):
       Frame.__init__(self) 
       
       self.settings_container= Frame(self,bg='gray',padx=400,pady=10)
       self.settings_container.pack(expand="True", fill='both')
       
       self.settings_label=Label(self.settings_container, text="Settings",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
       self.settings_label.grid(pady=5)
       
       self.settings_exit_btn = Button(self.settings_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
       self.settings_exit_btn.grid()
       
class Motor(Frame):
    def __init__(self):
       Frame.__init__(self) 
       
       self.motor_container= Frame(self,bg='gray',padx=400,pady=10)
       self.motor_container.pack(expand="True", fill='both')
       
       self.motor_label=Label(self.motor_container, text="Motors",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
       self.motor_label.grid(pady=5)
       
       self.motor_exit_btn = Button(self.motor_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
       self.motor_exit_btn.grid()
       
class Encoder(Frame):
    def __init__(self):
       Frame.__init__(self) 
       
       self.encoder_container= Frame(self,bg='gray',padx=400,pady=10)
       self.encoder_container.pack(expand="True", fill='both')
       
       self.encoder_label=Label(self.encoder_container, text="Encoders",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
       self.encoder_label.grid(pady=5)
       
       self.encoder_exit_btn = Button(self.encoder_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
       self.encoder_exit_btn.grid()
    
class PH10(Frame):
    def __init__(self):
       Frame.__init__(self) 
       
       self.encoder_container= Frame(self,bg='gray',padx=400,pady=10)
       self.encoder_container.pack(expand="True", fill='both')
       
       self.encoder_label=Label(self.encoder_container, text="PH10 Tester",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
       self.encoder_label.grid(pady=5)
       
       self.encoder_exit_btn = Button(self.encoder_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
       self.encoder_exit_btn.grid()
       
class Jogbox(Frame):
    def __init__(self):
       Frame.__init__(self) 
       
       self.encoder_container= Frame(self,bg='gray',padx=400,pady=10)
       self.encoder_container.pack(expand="True", fill='both')
       
       self.encoder_label=Label(self.encoder_container, text="JogBox Tester",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
       self.encoder_label.grid(pady=5)
       
       self.encoder_exit_btn = Button(self.encoder_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
       self.encoder_exit_btn.grid()
       
class Sensor(Frame):
    def __init__(self):
       Frame.__init__(self) 
       
       self.encoder_container= Frame(self,bg='gray',padx=400,pady=10)
       self.encoder_container.pack(expand="True", fill='both')
       
       self.encoder_label=Label(self.encoder_container, text="Sensors",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 30,"bold"))
       self.encoder_label.grid(pady=5)
       
       self.encoder_exit_btn = Button(self.encoder_container, text='EXIT',bg='red',fg='white',font=("Robot", 25,"bold"), command=lambda: app.show_frame(StartPage))
       self.encoder_exit_btn.grid()

if __name__ == "__main__":
    app = App()
    app.mainloop()