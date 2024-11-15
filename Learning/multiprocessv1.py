from tkinter import *
from multiprocessing import *
import time

class Page(Frame):
    
    def __init__(self):
        super().__init__()
        
       #-------------------------------------------------------------------Frame & Title----------------------------------------------------------------------------------------------
       
        self.container = Frame(self, bg= 'blue')
        self.container.pack(expand = 'True', fill = 'both')
        
        self.title = Label(self.container, text='Multiprocessing',fg = 'white', bg = 'blue')
        self.title.grid()
        
        self.btn1 = Button(self.container,text="Saludito a Mike",command=self.saludo)
        self.btn1.grid()
        
        self.btn2 = Button(self.container,text="Iniciar Procesos",command=self.iniciar_procesos)
        self.btn2.grid()
    
       #-------------------------------------------------------------------------Variables--------------------------------------------------------------------------------------------
       
        self.cycle_status = True
        """self.process_x.join()
        self.process_y.join()"""
              
       #------------------------------------------------------------------------Settings----------------------------------------------------------------------------------------------
       
        
       
       #---------------------------------------------------------------------------Methods--------------------------------------------------------------------------------------------
    def saludo(self):
        print("Saludos Mike")
        
    def iniciar_procesos(self):
        
        
        
        #for cycle_processes in range(encoders_seleccionados)
            #crear solo el numero de procesos de los encoders que estén seleccionados
            
    #Boton start:
        #actualizar GUI    
        #if primera vez:
            #procesos.start()
        #else:
            #solo comenzar a actualizar GUI
            
    #Boton STOP:
        #Dejar de actualizar GUI
        #Ver si se pueden dejar como listeners los procesos
        
        if self.cycle_status:
            self.counter_x = process_cycle('x',3)
            self.process_x = Process(target=self.counter_x.cycle)
            
            self.counter_y = process_cycle('y',5)
            self.process_y = Process(target=self.counter_y.cycle)
            
            self.process_x.start()
            self.process_y.start()
            
            self.cycle_status = False
        
    
        
        
class process_cycle:
    
    def __init__(self, ID, time):
        self.ID = ID
        self.secs = time
        self.counter = 0
        
    def cycle(self):
        print("Iniciando proceso en ",self.ID)
        while self.counter < 5000000:
            self.counter += 1
            
        time.sleep(self.secs)
        print("Done ",self.ID)
    
class App(Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Multiprocessing Test")
        self.geometry('200x200')
        container = Frame(self, bg='black')
        container.grid(row=0,column=0)
        
        
        self.frames = {}    # Dictionary to hold the frames that we are going to show
        
        self.load_frames(Page,)
        self.show_frame(Page)
        
    def load_frames(self, *args):
        for F in args:

            frame = F() # Create objects from the classes listed above in the F loop

            self.frames[F] = frame # Save the created objects to our dictionary

            frame.grid(row=0, column=0, sticky="nsew")  # Load the frame objects into a grid stacking them on top of each other
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            
    def show_frame(self, frame_to_show):
       
        frame = self.frames[frame_to_show]  # Look for the class in our dictionary
        self.current_frame = frame  # Set the frame as our current frame variable
        frame.tkraise()
       


if __name__ == "__main__":
    app = App()
    app.mainloop()