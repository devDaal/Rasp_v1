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
        #self.attributes("-fullscreen", True) # For final build this should be ativated
        #self.geometry('800x520') # Size of screen
        self.resizable(1,1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.port = None
        self.connect_status = 0
        
        self.load_frames(StartPage)
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

        self.container = Frame(self,bg="gray", padx=152,pady=20)
        self.container.pack(expand="True", fill='both')

        self.container_title = Frame(self.container,bg="gray")
        self.container_title.grid(row=0,column=1)
        
        self.easter_egg= Button(self.container,borderwidth=0,takefocus="off",bg="orange",activebackground='gray',relief="flat",padx=50,pady=40,
                        command=lambda:self.__easter_egg_deploy(),cursor='watch')
        self.easter_egg.grid(row=0,column=2,padx=(10,0)) 
        
        self.motor_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons\\motor.png").subsample(21,21)
        self.motor_btn = Button(self.container, image=self.motor_photo,bg= 'blue')
        self.motor_btn.image= self.motor_photo
        self.motor_btn.grid(row=1, column=2,padx=(50,50), pady=(80,50))
        
        self.encoder_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons\\encoder.png").subsample(4,4)
        self.encoder_btn = Button(self.container, image=self.encoder_photo, bg= 'red')
        self.encoder_btn.image= self.encoder_photo
        self.encoder_btn.grid(row=2, column=2, padx=(50,50), pady=(30,50))
        
        self.settings_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons\\settings.png").subsample(55,55)
        self.settings_btn = Button(self.container,image=self.settings_photo, bg= 'green')
        self.settings_btn.image= self.settings_photo
        self.settings_btn.grid(row=1, column=1, padx=(50,50), pady=(80,50))
        
        self.ph10_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons\\ph10.png").subsample(4,4)
        self.ph10_btn = Button(self.container, bg= 'yellow',image=self.ph10_photo)
        self.ph10_btn.image= self.ph10_photo
        self.ph10_btn.grid(row=2, column=1, padx=(50,50), pady=(30,50))
        
        self.sensor_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons\\sensor.png").subsample(22,22)
        self.sensor_btn = Button(self.container, bg= 'white', image=self.sensor_photo)
        self.sensor_btn.image = self.sensor_photo
        self.sensor_btn.grid(row=1, column=0, padx=(50,50), pady=(80,50))
        
        self.jogbox_photo = PhotoImage(file= "C:\\Users\\ITS_Servicio\\Desktop\\Raspv1\\Tests\\icons\\jogbox.png").subsample(6,6)
        self.jogbox_btn = Button(self.container, bg= 'grey', image=self.jogbox_photo)
        self.jogbox_btn.image = self.jogbox_photo
        self.jogbox_btn.grid(row=2, column=0, padx=(50,50), pady=(30,50))

        

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

if __name__ == "__main__":
    app = App()
    app.mainloop()