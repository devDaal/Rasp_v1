import serial
import time
import re

from tkinter import Tk, Label, Frame, LabelFrame, Button, PhotoImage,Message, messagebox
from tkinter.ttk import Progressbar

class Base():
    def __init__(self):

        self.frames = {}    # Dictionary to hold the frames that we are going to show

    def load_frames(self, *args):
        for F in args:

            frame = F(self) # Create objects from the classes listed above in the F loop

            self.frames[F] = frame # Save the created objects to our dictionary

            frame.grid(row=0, column=0, sticky="nsew")  # Load the frame objects into a grid stacking them on top of each other

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

class Functionality():
    """
        A class that contains most of the function pertaining to
        the testing of the jogbox
        ...

        Attributes
        ----------
        None
        
        Methods
        -------
        connect_serial:
            Switch between connecting and disconnecting serial.
            When connecting test if the jogbox responds correctly,
            subsequently start sending / receiving commands.
        test_loop:
            Holds the function testing for the monitor mode
        connection_to_jogbox_loop:
            Loop to keep the connection to the jogbox once the
            connection is stablished.
        led_test:
            Sends a sequence that turns each led one by one
        buzzer_test:
            Sends the command that makes the buzzer sound
        start_test:
            Starts the test of the object
        stop_test:
            Stops the test of the object
        start_stop_test:
            Switch between starting and stopping a test of the object
        update_results:
            Updates the frame Test_Results according to previous test
        reset_all_results:
            Resets the test results of all the steps of guidecheck
        exit_monitor_mode:
            When clicking the exit button close anything related to 
            monitor mode
        exit_guided_check:
            When clicking the exit button it closes 
            anything related to testing
        encode_binary:
            Receives a binary 16 bit binary number and encodes to
            the Led function command
        map_from_to:
            Receive original_lower number_to_map and map it from an 
            original range original_lower:original_upper to a 
            range map_lower:map_upper


    """
    def __init__(self):
        """ 
            Parameters
            ---------
            None
        """

        self.parent = None

        self.app = None

        self.connect_status = 0

        self.test_status = 0

        self.holder_connection_to_jogbox_loop = None

        self.holder_test_loop = None
    
    def connect_serial(self):
        """ 
            Switch between connecting and disconnecting serial.
            When connecting test if the jogbox responds correctly,
            subsequently start sending / receiving commands.

            Parameters
            ----------
            None

        """
        if (self.connect_status == 0):
            try:

                print("Attempting to connect to Serial....")
    
                global port # Set the port as global variable
                port = serial.Serial(
                '/dev/ttyUSB0',
                baudrate=4800,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.SEVENBITS,
                writeTimeout = 0,
                timeout = 0.05,
                rtscts=False,
                dsrdtr=False,
                xonxoff=True)

                
                print("Serial connected")

                port.write(b'?\r\n')
                port.write(b'L0800\r\n')   # Dont turn on LED, just the Buzzer
                time.sleep(0.5)
                port.write(b'L0800\r\n')

                message = port.readline()
                print(message)
                if (message[-2:] == b'\r\n'):
                    message = message.decode('Ascii').replace(".", "")
                    print(message)
                    
                    if (message == "b&s(1)\r\n"):
                        print("joystick is alive")
                        self.lbl_serial_status['bg']= "green"

                        message = port.readline() # Initial value from buttons
                        message = port.readline() # Initial value from the feedrate
                        if (message[-2:] == b'\r\n'):
                            message = message.decode('Ascii').replace(".", "")

                            if (message[:1] == "O"):
                                message = int(message[1:], 16)
                                if(type(self) != JogboxMonitorMode):self.parent.frames[FeedrateTest].container_jogbox_feedrate.progressbar_feedrate['value'] = message
                      



                        self.connect_status = 1
                        self.holder_connection_to_jogbox_loop = self.parent.after(1000, self.connection_to_jogbox_loop)
                        if(type(self)==JogboxMonitorMode): self.holder_test_loop = self.parent.after(100, self.test_loop)
                else:
                    print("Joystick did not respond")
                    port.close()
                    joystick_error_message = """Serial connection was established but the jogbox was unable to respond.
                    \nCheck if the jogbox is turning on, if not try reconnecting it.
                    \nIf the jogbox is not turning on, then it might be faulty."""
                    messagebox.showerror("Joystick error", joystick_error_message) 
            
            except Exception as e: 
                print(e)
                connection_error_message = """There was an error when connecting to serial.
                \nCheck the cable connection from the jogbox to the tester and try again."""
                messagebox.showerror("Connection error", connection_error_message) 

        elif (self.connect_status == 1):
            try:
                print("Attempting to disconnect serial.....")
                port.close()
                self.connect_status = 0
                self.lbl_serial_status['bg']= "red"

                self.parent.after_cancel(self.holder_connection_to_jogbox_loop) # If serial is disconnected dont keep alive the connection
                if(type(self)==JogboxMonitorMode): self.parent.after_cancel(self.holder_test_loop)
                print("Serial disconnected")
                
            except:
                print("Could not disconnect serial")
                messagebox.showerror("Error", "There was an error when disconnecting serial try again.") 
    
    def test_loop(self):
        """ 
            Loop that test all functions of the jogbox such as
            button press, joystick movement, feedrate, led's and buzzer


            Parameters
            ----------
            None

            Description of functioning
            ----------
            Messages are received in HEX form:
                'KFFFF' (K = Signals its a button press)
                'OFF' (O = Signals its a feedrate command)
                'JFFFFFF' (J = Signals its joystick movement)

            Button decoding:

                The hex message without the 'K' is decoded into a 16 bit binary form:
                    '0000000000000000'

                Each bit represents the state of a button on the jogbox as follows:
                    Bit = 1, button is active
                    Bit = 0 button is not active

                    (Position from left to right starting with 0)
                    0 = Joystick button
                    1 = Upload button
                    2 = Turtle button
                    3 = Jogbox button
                    4 = Checkmark button
                    5 = UNUSED
                    6 = Motor activate button
                    7 = Cancel button
                    8 = Z lock button
                    9 = Y lock button
                    10 = X Lock button
                    11 = Probe button
                    12 = Forward button
                    13 = Play / Pause button
                    14 = Lock button
                    15 = UNUSED

            Joystick Decoding:

                The hex message without the 'J' splits into chunks of 2
                'FF' 'FF' 'FF'
                each chunk represents X, Y and Z correspondingly, we take 
                the HEX representation and turn it into decimal and map it
                from 0 to 100
            
            Feedrate Decodign:

                Message for button presses are received in HEX form:
                'OFF' (O = Signals its a feedrate command)

                The hex message without the 'O' is converted into decimal representation
                that goes from 0 to 100 in steps of 10

        """

        message_raw = port.readline() # Raw Commando from Jogbox
        
        #print(message_raw)
        if (message_raw[-2:] == b'\r\n'):
            #print(message_raw)
            message_raw = message_raw.decode('Ascii').replace(".", "")
            #print(message_raw)
            if (message_raw[:1] == "J"):
                #print(message_raw)
                message = message_raw[1:] # Take out the J
                xyz = (re.findall('.{%d}' % 2, message)) # Split the string in chunks of 2
                xyz[0],xyz[1],xyz[2] = int(xyz[0],16),int(xyz[1],16),int(xyz[2],16)
                xyz[0],xyz[1],xyz[2] = int(self.map_from_to(xyz[0],90,170,0,100)),int(self.map_from_to(xyz[1],90,170,0,100)),int(self.map_from_to(xyz[2],65,190,0,100))
                #print("Joystick ( X: " + str(xyz[0]) + ", Y: " + str(xyz[1]) + ", Z: " + str(xyz[2]) + " )")

                self.container_jogbox_joystick.progressbar_x['value'] = xyz[0]
                self.container_jogbox_joystick.progressbar_y['value'] = xyz[1]
                self.container_jogbox_joystick.progressbar_z['value'] = xyz[2]
            
            if (message_raw[:1] == "O"):
                #print(message_raw)
                message = int(message_raw[1:], 16)
                self.container_jogbox_feedrate.progressbar_feedrate['value'] = message
                #print(message)
            
            if (message_raw[:1] == "K"):
                
                #print("'''''''''''''''''''''")
                #print(message_raw)
                message = message_raw[1:]
                message = bin(int(message, 16))[2:].zfill(16)   

                #print(message) 

                #print("'''''''''''''''''''''")
                
                if (message[0] == '1'): self.container_jogbox_btn.btn_joystick.press()
                else: self.container_jogbox_btn.btn_joystick.unpress()

                if (message[1] == '1'): self.container_jogbox_btn.btn_upload.press()
                else: self.container_jogbox_btn.btn_upload.unpress()

                if (message[2] == '1'): self.container_jogbox_btn.btn_turtle.press()
                else: self.container_jogbox_btn.btn_turtle.unpress()

                if (message[3] == '1'): self.container_jogbox_btn.btn_jogbox.press()
                else: self.container_jogbox_btn.btn_jogbox.unpress()

                if (message[4] == '1'): self.container_jogbox_btn.btn_checkmark.press()
                else: self.container_jogbox_btn.btn_checkmark.unpress()
                
                if (message[6] == '1'): self.container_jogbox_btn.btn_motor.press()
                else: self.container_jogbox_btn.btn_motor.unpress()

                if (message[7] == '1'): self.container_jogbox_btn.btn_cancel.press()
                else: self.container_jogbox_btn.btn_cancel.unpress()

                if (message[8] == '1'): self.container_jogbox_btn.btn_turn_up_down_arrow.press()
                else: self.container_jogbox_btn.btn_turn_up_down_arrow.unpress()

                if (message[9] == '1'): self.container_jogbox_btn.btn_up_down_arrow.press()
                else: self.container_jogbox_btn.btn_up_down_arrow.unpress()

                if (message[10] == '1'): self.container_jogbox_btn.btn_left_right_arrow.press()
                else: self.container_jogbox_btn.btn_left_right_arrow.unpress()

                if (message[11] == '1'): self.container_jogbox_btn.btn_probe.press()
                else: self.container_jogbox_btn.btn_probe.unpress()

                if (message[12] == '1'): self.container_jogbox_btn.btn_forward_arrow.press()
                else: self.container_jogbox_btn.btn_forward_arrow.unpress()

                if (message[13] == '1'): self.container_jogbox_btn.btn_play_pause.press()
                else: self.container_jogbox_btn.btn_play_pause.unpress()

                if (message[14] == '1'): self.container_jogbox_btn.btn_lockpad.press()    
                else: self.container_jogbox_btn.btn_lockpad.unpress()   

        self.holder_test_loop = self.parent.after(1, self.test_loop)
    
    def connection_to_jogbox_loop(self):
        """ 
            Loop to keep the connection to the jogbox once the
            connection is stablished
            The loop continuosly sends a b'.\r\n' through serial

            Parameters
            ----------
            None

        """
        port.write(b'.\r\n')
        #print("keeping alive")
        self.holder_connection_to_jogbox_loop = self.parent.after(4000, self.connection_to_jogbox_loop)
    
    def led_test (self,connect_status):
        """ 
            Sends a sequence of commands to turn each led 
            one by one and at the end turn all of them on

            Parameters
            ----------
            connect_status: Integer
                connection status variable

        """

        if(connect_status == 1):
            led_list = ['0000000000010000', 
                        '0010000000000000',
                        '0000000100000000', 
                        '0000000000000001', 
                        '0000000000001000',
                        '0000000001000000',  
                        '0000000000100000', 
                        '0000000010000000',
                        '0100000000000000',  
                        '0000000000000010', 
                        '0000010000000000',
                        '0001000000000000',  
                        '1000000000000000', 
                        '0000001000000000',  
                        '0000000000000100']
            for led in led_list:
                send = self.encode_binary(led)
                port.write(send)
                time.sleep(1)

            send = self.encode_binary('1111011111111111')
            port.write(send)
            time.sleep(3)

            send = self.encode_binary('0000100000000000')
            port.write(send)
            
        elif(connect_status == 0):
            messagebox.showerror("Error", "The jogbox is not connected.\n\nPress the connect serial button to connect") 

    def buzzer_test (self,connect_status):
        """ 
            Sends a command that makes the buzzer sound

            Parameters
            ----------
            connect_status: Integer
                connection status variable

        """
        if(connect_status == 1):
            send = self.encode_binary('0000100000000000')
            port.write(send)
            
        elif(connect_status == 0):
            messagebox.showerror("Error", "The jogbox is not connected.\n\nPress the connect serial button to connect") 

    def start_test(self):
        """ 
            Starts the test of the object 

            Parameters
            ----------
            None
        """
        #print("Starting joystick test")
        self.test_status = 1 # It was not running so set the status to running (1)
        self.btn_start_test ['bg'] = "red" 
        self.btn_start_test ['text'] = "STOP"
        self.holder_test_loop = self.app.after(100, self.test_loop) # Call the test loop again

    def stop_test(self):
        """ 
            Stop the test of the object

            Parameters
            ----------
            None

        """
        #print("Stopping joystick test")
        if(self.test_status == 1): self.app.after_cancel(self.holder_test_loop)  # Stop the loop of the test
        self.test_status = 0 # Set the status to not running
        self.btn_start_test ['bg'] = "green"
        self.btn_start_test ['text'] = "START"
        
    def start_stop_test(self): # Current test is recieved from the frame
        """ 
            Switch between starting and stopping the test of
            the object.
            When starting the test reset the results and gui of the object

            Parameters
            ----------
            None

        """
        if(self.parent.frames[ConnectionTest].connect_status == 1): # 1 = The jogbox is connected and responds

            if (self.test_status == 0): # 0 = Test is not running 
                if (type(self) == ButtonsTest): # If the test we are starting is the buttons then clear them
                    self.container_jogbox_btn.unpress_all()
                    
                self.reset_results()
                self.start_test()
                

            elif (self.test_status == 1): # 1 = Test is running
                self.stop_test()

                
        elif (self.parent.frames[ConnectionTest].connect_status == 0): # 0 = Jogbox was not able to connect
            connection_error_message = "Serial is not connected \nCheck the connection status on step 1 of the test"
            messagebox.showerror("Connection error", connection_error_message) 
    
    def update_results(self):
        """ 
            Updates the labels in the tests results frame according
            to the results of the previous tests

            Parameters
            ----------
            None

        """
        self.parent.frames[TestResults].clear_all()

        self.parent.frames[TestResults].test_results["feedrate"] = 1
        for porcentage in self.parent.frames[FeedrateTest].test_results:
            if (self.parent.frames[FeedrateTest].test_results[porcentage] == 0):
                #print (porcentage)
                self.parent.frames[TestResults].test_results["feedrate"] = 0

        self.parent.frames[TestResults].test_results["x"] = 1
        for porcentage in self.parent.frames[JoystickTest].test_results["x"]:
            if (self.parent.frames[JoystickTest].test_results["x"][porcentage] == 0):
                #print (porcentage)
                self.parent.frames[TestResults].test_results["x"] = 0
        
        self.parent.frames[TestResults].test_results["y"] = 1
        for porcentage in self.parent.frames[JoystickTest].test_results["y"]:
            if (self.parent.frames[JoystickTest].test_results["y"][porcentage] == 0):
                #print (porcentage)
                self.parent.frames[TestResults].test_results["y"] = 0
        
        self.parent.frames[TestResults].test_results["z"] = 1
        for porcentage in self.parent.frames[JoystickTest].test_results["z"]:
            if (self.parent.frames[JoystickTest].test_results["z"][porcentage] == 0):
                #print (porcentage)
                self.parent.frames[TestResults].test_results["z"] = 0

        if (self.parent.frames[TestResults].test_results["x"] == 1):
            self.parent.frames[TestResults].lbl_result_x['bg'] = "green"
        if (self.parent.frames[TestResults].test_results["y"] == 1):
            self.parent.frames[TestResults].lbl_result_y['bg'] = "green"
        if (self.parent.frames[TestResults].test_results["z"] == 1):
            self.parent.frames[TestResults].lbl_result_z['bg'] = "green"
        if (self.parent.frames[TestResults].test_results["feedrate"] == 1):
            self.parent.frames[TestResults].lbl_result_feedrate['bg'] = "green"
        if (self.parent.frames[ButtonsTest].test_results["joystick"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_joystick.press()
        if (self.parent.frames[ButtonsTest].test_results["upload"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_upload.press()
        if (self.parent.frames[ButtonsTest].test_results["turtle"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_turtle.press()
        if (self.parent.frames[ButtonsTest].test_results["jogbox"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_jogbox.press()
        if (self.parent.frames[ButtonsTest].test_results["checkmark"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_checkmark.press()
        if (self.parent.frames[ButtonsTest].test_results["motor"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_motor.press()
        if (self.parent.frames[ButtonsTest].test_results["cancel"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_cancel.press()
        if (self.parent.frames[ButtonsTest].test_results["turn_up_down"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_turn_up_down_arrow.press()
        if (self.parent.frames[ButtonsTest].test_results["up_down"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_up_down_arrow.press()
        if (self.parent.frames[ButtonsTest].test_results["left_right"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_left_right_arrow.press()
        if (self.parent.frames[ButtonsTest].test_results["probe"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_probe.press()
        if (self.parent.frames[ButtonsTest].test_results["forward"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_forward_arrow.press()
        if (self.parent.frames[ButtonsTest].test_results["play_pause"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_play_pause.press()
        if (self.parent.frames[ButtonsTest].test_results["lockpad"] == 1):
            self.parent.frames[TestResults].container_jogbox_btn.btn_lockpad.press()

        if (self.parent.frames[LedTest].container_jogbox_btn.btn_turtle.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_turtle.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_upload.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_upload.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_turtle.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_turtle.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_jogbox_1.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_jogbox_1.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_jogbox_2.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_jogbox_2.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_jogbox_3.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_jogbox_3.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_checkmark.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_checkmark.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_motor.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_motor.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_cancel.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_cancel.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_turn_up_down_arrow.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_turn_up_down_arrow.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_up_down_arrow.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_up_down_arrow.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_left_right_arrow.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_left_right_arrow.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_probe.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_probe.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_forward_arrow.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_forward_arrow.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_play_pause.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_play_pause.btn_fail()
        if (self.parent.frames[LedTest].container_jogbox_btn.btn_lockpad.btn_status == 1):
            self.parent.frames[TestResults].container_jogbox_led.btn_lockpad.btn_fail()
            
    def reset_all_results(self):
        """ 
            Resets the results of all the tests

            Parameters
            ----------
            None

        """
        self.parent.frames[TestResults].reset_results()

        self.parent.frames[ButtonsTest].reset_results()

        self.parent.frames[FeedrateTest].reset_results()

        self.parent.frames[JoystickTest].reset_results()

        self.parent.frames[TestResults].clear_all()

    def exit_guided_check(self):
        """ 
            When clicking the exit button it closes and resets 
            anything related to the guided check

            Parameters
            ----------
            None

        """

        # Reset top frames
        self.parent.show_frame(ConnectionTest)
        self.app.show_frame(StartPage)

        # Close all tests
        if (self.test_status == 1): self.stop_test()
        
        # Close Serial
        if (self.parent.frames[ConnectionTest].connect_status == 1):
            print("Serial was running")
            self.parent.frames[ConnectionTest].connect_serial()
        
        # Reset result frame
        self.reset_all_results()
    
        # Reset the btn in the test
        self.parent.frames[ButtonsTest].container_jogbox_btn.unpress_all()
        self.parent.frames[LedTest].container_jogbox_btn.unpress_all()
    
    def exit_monitor_mode (self):
        """ 
            When clicking the exit button it closes and resets 
            anything related to the monitor mode

            Parameters
            ----------
            None
            
        """

        self.parent.show_frame(StartPage)

        # If connection is running then close it 
        if (self.connect_status == 1):
            self.connect_serial()
    
    def encode_binary(self,binary_number):
        """ 
            When clicking the exit button it closes and resets 
            anything related to the guided check

            Parameters
            ----------
            binary_number: String
                16 bit encoded binary number
            
        """
        encoding = ((hex(int(binary_number, 2))[2:]).upper())
        encoding = encoding.zfill(4)
        encoding = bytes(("L" + encoding + "\r\n"), 'utf-8')
        return encoding

    def map_from_to(self,number_to_map,original_lower,original_upper,map_lower,map_upper):
        """ 
            Receive original_lower number_to_map and map it from an 
            original range original_lower:original_upper to a range map_lower:map_upper

            Parameters
            ----------
            number_to_map: Integer
                Number to map
            original_lower: Integer
                Lower value of original range
            original_upper: Integer
                Upper value of original range
            map_lower: Integer
                Lower value of value to map to
            map_upper: Integer
                Upper value of value to map to
            
            Returns
            -------
            mapped_number: Integer
                Mapped number
        """
        mapped_number =(number_to_map-original_lower)/(original_upper-original_lower)*(map_upper-map_lower)+map_lower
        return mapped_number

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

    def __init__(self, *args, scale = 1.0, **kwargs):
        """ 
            Parameters
            ---------
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        Base.__init__(self)
        Tk.__init__(self, *args, **kwargs) # Inherit from the main tkinter class
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.title("Jogbox Tester")
        self.call('tk','scaling', scale )
        
        #self.attributes("-fullscreen", True) # For final build this should be ativated
        self.geometry('800x412+0+0') # Size of screen
        
        
        #self.photo_logo = PhotoImage(file= "icons\its-logo-short.png").subsample(10,10)
        #self.iconphoto(True, self.photo_logo)   # Icon that shows on the left corner of the screen

        self.load_frames(StartPage, JogboxMonitorMode, GuidedCheck)

        self.show_frame(StartPage)  # Frame object to show at the top screen

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

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object
        """
        
        Frame.__init__(self, parent)

        self.counter_easter = 0     

        self.container = Frame(self,bg="gray")
        self.container.pack()

        self.container_title = Frame(self.container,bg="gray")
        self.container_title.grid(row=0,column=0)

        self.photo_logo = PhotoImage(file= "icons/its-logo.png").subsample(3,3)
        self.lbl_logo = Label(self.container_title,image=self.photo_logo, bg = "gray", fg = "black", font = ("Robot",20,"bold"))
        self.lbl_logo.image = self.photo_logo
        self.lbl_logo.grid(row=0,column=0,padx=(310,122),pady=(10,0))

        
        self.easter_egg= Button(self.container_title,borderwidth=0,takefocus="off",bg="gray",activebackground='gray',relief="flat",padx=50,pady=40,
                        command=lambda:self.__easter_egg_deploy()) # Assign image to label obj
        self.easter_egg.grid(row=0,column=1,padx=(0,100)) 

        Label(self.container, text="JOGBOX TESTER",borderwidth=2,bg="gray",fg="white",font=("Robot", 45,"bold")).grid(row=1,column=0,pady=(0,10))

        help_text = """Please select an option: \n
                        Guided Check: It will take you step by step through the process of checking the jogbox. \n
                        Check All: It will show you a screen where you can see all the parameters from the jogbox at once."""
        Message(self.container, text=help_text,borderwidth=2,bg="gray",fg="white",font=("Robot", 18,"normal"),width=1300, justify='center').grid(row=2,column=0)

        self.container_btn = LabelFrame(self.container,bg="#4f4f4f",fg="white",padx=100,pady=5)
        self.container_btn.grid(row=3,column=0,pady=10)

        Label(self.container_btn, text="GUIDED CHECK",borderwidth=2,bg="#4f4f4f",fg="white",font=("Robot", 20,"bold")).grid(row=0,column=0,pady=(10,0),padx=20)
        Label(self.container_btn, text="MONITOR MODE",borderwidth=2,bg="#4f4f4f",fg="white",font=("Robot", 20,"bold")).grid(row=0,column=1,pady=(10,0),padx=20)

        self.photo_123 = PhotoImage(file= "icons/ico_123.png").subsample(3,3)
        self.btn_guided_check = Button(self.container_btn,image=self.photo_123, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                                command=lambda: parent.show_frame(GuidedCheck))
        self.btn_guided_check.image = self.photo_123
        self.btn_guided_check.grid(row=1,column=0,pady=(10,20),padx=10)

        self.photo_monitor = PhotoImage(file= "icons/ico_monitor.png").subsample(3,3)
        self.btn_monitor_mode = Button(self.container_btn,image=self.photo_monitor, bg = "#383838", fg = "black", font =  ("Robot",20,"bold"),
                                command=lambda: parent.show_frame(JogboxMonitorMode))
        self.btn_monitor_mode.image= self.photo_monitor
        self.btn_monitor_mode.grid(row=1,column=1,pady=(10,20),padx=10)

    def __easter_egg_deploy(self):
        """ 
            Protected class 

            Parameters
            ----------
            None
            
        """
        self.counter_easter += 1
        #print(self.counter_easter)
        if self.counter_easter == 10:
            self.counter_easter = 0
            messagebox.showinfo("Developer","System developed by Alwurts")
          
class ConnectionTest(Frame, Functionality):
    """
        A class that holds the connection test to the jogbox.
        It is to be run inside the guided check class.
        It inherits from the Frame class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        None
    """
    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object
            app : tk frame class 
                Main / Top Level class of the interface
        """
        
        Frame.__init__(self, parent,bg="gray")
        Functionality.__init__(self)

        self.parent = parent

        self.app = parent.parent # Top level app

        Label(self, text="STEP 1: CONNECTION TESTING",borderwidth=2,bg="gray",fg="#ffffff",bd=2,font=("Robot", 24,"bold")).grid(row=0,column=0,columnspan=2,pady=(5,5),padx=(10,0))

        self.container = LabelFrame(self,bg="#4f4f4f",padx=50,pady=10)
        self.container.grid(row=1,column=0,padx=(20,10),pady=(0,0))

        Label(self.container, text="INSTRUCTIONS: ",borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 20,"bold")).grid(row=0,column=0,pady=(10,10),padx=5)
        
        help_text = """This step of the test takes care of assessing the connection between the tester and the jogbox. \r
        If this step fails or is not completed successfully the other steps can't be performed. \n
        1. Make sure the jogbox is properly connected. \n
        2. Click the button on the right "Connect Serial". \n
        3. If the connection is successful the "I/O" indicator will turn green, otherwise, a popup will show the error encountered."""
        Message(self.container, text=help_text,borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 19,"normal"),width=250, justify='left').grid(row=1,column=0,padx=(5,5),pady=(0,0))
        
        self.container_serial_connect = Frame(self.container,bg="#4f4f4f",padx=5,pady=20)
        self.container_serial_connect.grid(row=0,column=1,rowspan=2,padx=(5,0),pady=(0,10))

        self.btn_connect_serial = Button(self.container_serial_connect, text = "CONNECT SERIAL", bg = "#383838", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=5,
                                    command = lambda: self.connect_serial())
        self.btn_connect_serial.grid(row = 0,column = 0,padx=10)

        self.lbl_serial_status = Label(self.container_serial_connect, text = "I/0",borderwidth=3,relief="groove", bg = "red", fg = "white", font = ("Robot",30,"bold"),padx=10,pady=10)
        self.lbl_serial_status.grid(row = 0,column = 1,padx=10)

        parent.lbl_connection_status = self.lbl_serial_status

        self.container_action_btn = LabelFrame(self,bg="#4f4f4f",padx=30,pady=10)
        self.container_action_btn.grid(row=1,column=1,padx=(20,30),pady=(55,60))
       
        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png")
        self.btn_next_frame = Button(self.container_action_btn,image=self.photo_forward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                                command = lambda: parent.show_frame(ButtonsTest))
        self.btn_next_frame.image = self.photo_forward_arrow
        self.btn_next_frame.grid(row=0,column=0, pady=65)

        self.btn_exit = Button(self.container_action_btn,text="EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_guided_check())
        self.btn_exit.grid(row=1,column=0,pady=(20,0))

class ButtonsTest(Frame,Functionality):
    """
        A class that holds the button test of the jogbox.
        It is to be run inside the guided check class.
        It inherits from the Frame class of tkinter
        and functionality class.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        test_loop: 
            Holds the algorithm to test the buttons of the jogbox
        reset_result:
            Reset the results of the button testing

    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object
  
        """
    
        Frame.__init__(self, parent,bg="gray")
        Functionality.__init__(self)

        self.parent = parent

        self.app = parent.parent # Top level app

        self.test_results = {
            "probe": 0,
            "joystick": 0,
            "turtle": 0,
            "cancel": 0,
            "checkmark": 0,
            "forward": 0,
            "up_down": 0,
            "left_right": 0,
            "turn_up_down": 0,
            "upload": 0,
            "lockpad": 0,
            "jogbox": 0,
            "motor": 0,
            "play_pause": 0
            }

        Label(self, text="STEP 2: BUTTON TESTING",borderwidth=2,bg="gray",fg="#ffffff",bd=2,font=("Robot", 25,"bold")).grid(row=0,column=0,columnspan=2,padx=(25,5),pady=(10,0))

        self.container = LabelFrame(self,bg="#4f4f4f")
        self.container.grid(row=1,column=0,padx=(10,5))

        Label(self.container, text="INSTRUCTIONS: ",borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 20,"bold")).grid(row=0,column=0,pady=(10,10),padx=20)

        help_text = """In this step we will test the functioning of the jogbox keypad. \n
        1. Click the "Start" button to begin testing.\n
        2. On the jogbox click each of the buttons one by one.\n
        3. If a button press is registered then the corresponding button will turn green on the interface and stay that way.\n
        4. When all the buttons have been tested click the "Stop" button to stop testing.\n
        5. Continue to the next step."""
        Message(self.container, text=help_text,borderwidth=2,bg="#4f4f4f",fg="#ffffff",width=250,bd=2,font=("Robot", 16,"normal"), justify='left').grid(row=1,column=0,padx=(5,5))
        
        self.btn_start_test = Button(self.container, text = "START", bg = "green", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=30,
                                command = lambda: self.start_stop_test())
        self.btn_start_test.grid(row = 2,column = 0,padx=10)

        self.container_jogbox_btn = JogboxKeypadModelLabel(self.container)
        self.container_jogbox_btn.grid(row=0,column=1,rowspan=3,padx=(50,0))
        
        self.container_action_btn = LabelFrame(self,bg="#4f4f4f",padx=20,pady=100)
        self.container_action_btn.grid(row=1,column=2,padx=(20,0))

        self.photo_backward_arrow = PhotoImage(file="icons/ico_left-arrow.png")#.subsample(2,2)
        self.btn_previous_frame = Button(self.container_action_btn,image=self.photo_backward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                                    command = lambda: [parent.show_frame(ConnectionTest),self.stop_test()])
        self.btn_previous_frame.image = self.photo_backward_arrow
        self.btn_previous_frame.grid(row=0,column=0,padx=(5,5))

        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png")#.subsample(2,2)
        self.btn_next_frame = Button(self.container_action_btn,image=self.photo_forward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                                command = lambda: [parent.show_frame(FeedrateTest),self.stop_test()])
        self.btn_next_frame.image = self.photo_forward_arrow
        self.btn_next_frame.grid(row=0,column=1,padx=(5,5))

        self.btn_exit = Button(self.container_action_btn,text="EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_guided_check())
        self.btn_exit.grid(row=1,column=0,columnspan=2,pady=20)

    def test_loop(self):
        """ 
            Button test of the jogbox.
            Receive a message via serial.

            Parameters
            ----------
            None

            Explanation
            ------------
            Message for button presses are received in HEX form:
                'KFFFF' (K = Signals its a button press)

            The hex message without the 'K' is decoded into a 16 bit binary form:
                '0000000000000000'

            Each bit represents the state of a button on the jogbox as follows:
                Bit = 1, button is active
                Bit = 0 button is not active

                (Position from left to right starting with 0)
                0 = Joystick button
                1 = Upload button
                2 = Turtle button
                3 = Jogbox button
                4 = Checkmark button
                5 = UNUSED
                6 = Motor activate button
                7 = Cancel button
                8 = Z lock button
                9 = Y lock button
                10 = X Lock button
                11 = Probe button
                12 = Forward button
                13 = Play / Pause button
                14 = Lock button
                15 = UNUSED

        """
        message = port.readline()
        #print(message)
        if (message[-2:] == b'\r\n'):
            #print(message)
            message = message.decode('Ascii').replace(".", "")
            if (message[:1] == "K"):
                print(message)
                message = message[1:]
                #print(message)
                message = bin(int(message, 16))[2:].zfill(16)
                #print(message)
                if (message[0] == '1'): 
                    self.test_results["joystick"] = 1
                    self.container_jogbox_btn.btn_joystick.press()
                if (message[1] == '1'): 
                    self.test_results["upload"] = 1
                    self.container_jogbox_btn.btn_upload.press()
                if (message[2] == '1'): 
                    self.test_results["turtle"] = 1
                    self.container_jogbox_btn.btn_turtle.press()
                if (message[3] == '1'): 
                    self.test_results["jogbox"] = 1
                    self.container_jogbox_btn.btn_jogbox.press()
                if (message[4] == '1'): 
                    self.test_results["checkmark"] = 1
                    self.container_jogbox_btn.btn_checkmark.press()
                if (message[6] == '1'): 
                    self.test_results["motor"] = 1
                    self.container_jogbox_btn.btn_motor.press()
                if (message[7] == '1'): 
                    self.test_results["cancel"] = 1
                    self.container_jogbox_btn.btn_cancel.press()
                if (message[8] == '1'): 
                    self.test_results["turn_up_down"] = 1
                    self.container_jogbox_btn.btn_turn_up_down_arrow.press()
                if (message[9] == '1'): 
                    self.test_results["up_down"] = 1
                    self.container_jogbox_btn.btn_up_down_arrow.press()
                if (message[10] == '1'): 
                    self.test_results["left_right"] = 1
                    self.container_jogbox_btn.btn_left_right_arrow.press()
                if (message[11] == '1'): 
                    self.test_results["probe"] = 1
                    self.container_jogbox_btn.btn_probe.press()
                if (message[12] == '1'): 
                    self.test_results["forward"] = 1
                    self.container_jogbox_btn.btn_forward_arrow.press()
                if (message[13] == '1'): 
                    self.test_results["play_pause"] = 1
                    self.container_jogbox_btn.btn_play_pause.press()
                if (message[14] == '1'): 
                    self.test_results["lockpad"] = 1
                    self.container_jogbox_btn.btn_lockpad.press()
                

        self.holder_test_loop = self.app.after(1, self.test_loop)
    
    def reset_results(self):
        """ 
            Resets the results of the test

            Parameters
            ----------
            None
        """
        #print(self.test_results)
        self.test_results = {
            "probe": 0,
            "joystick": 0,
            "turtle": 0,
            "cancel": 0,
            "checkmark": 0,
            "forward": 0,
            "up_down": 0,
            "left_right": 0,
            "turn_up_down": 0,
            "upload": 0,
            "lockpad": 0,
            "jogbox": 0,
            "motor": 0,
            "play_pause": 0
            }
        #print(self.test_results)

class FeedrateTest(Frame, Functionality):
    """
        A class that holds the feedrate test of the jogbox.
        It is to be run inside the guided check class.
        It inherits from the Frame class of tkinter
        and functionality class.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        test_loop: 
            Holds the algorithm to test the feedrate potentiometer of the jogbox
        reset_result:
            Reset the results of the button testing
    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object

        """
        
        Frame.__init__(self, parent,bg="gray")
        Functionality.__init__(self)

        self.parent = parent

        self.app = parent.parent # Top level app

        self.test_results = {
            "0": 0,
            "10": 0,
            "20": 0,
            "30": 0,
            "40": 0,
            "50": 0,
            "60": 0,
            "70": 0,
            "80": 0,
            "90": 0,
            "100": 0
            }

        Label(self, text="STEP 3: FEEDRATE TESTING",borderwidth=2,bg="gray",fg="#ffffff",bd=2,font=("Robot", 24,"bold")).grid(row=0,column=0,columnspan=2,padx=(120,0),pady=(40,25))

        self.container = LabelFrame(self,bg="#4f4f4f")
        self.container.grid(row=1,column=0,padx=(10,0))

        Label(self.container, text="INSTRUCTIONS: ",borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 20,"bold")).grid(row=0,column=0,pady=(10,10),padx=20)

        help_text = """In this step we will test the function of the feedrate potentiometer.\n
        1. Click the "Start" button to begin testing.\n
        2. Turn the feedrate potentiometer left and right through all its range.\n
        3. The bar on the right will show the corresponding value of the feedrate.\n
        4. When you have turned the potentiometer through its range click on "Stop".\n
        5. Continue to the next step."""
        Message(self.container, text=help_text,borderwidth=2,bg="#4f4f4f",fg="#ffffff",width=350,bd=2,font=("Robot", 16,"normal"), justify='left').grid(row=1,column=0,padx=(40,20))
        
        self.btn_start_test = Button(self.container, text = "START", bg = "green", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=30,
                            command = lambda: self.start_stop_test())
        self.btn_start_test.grid(row = 2,column = 0,padx=10)

        #Label(self.container, text="Status",borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 20,"bold")).grid(row=3,column=0)
        
        self.container_jogbox_feedrate = FeedrateBarFrame(self.container)
        self.container_jogbox_feedrate.grid(row=0,column=1,rowspan=3,padx=(80,0))
      
        self.container_action_btn = LabelFrame(self,bg="#4f4f4f",pady=60)
        self.container_action_btn.grid(row=1,column=1,padx=(10,0))

        self.photo_backward_arrow = PhotoImage(file="icons/ico_left-arrow.png")
        self.btn_previous_frame = Button(self.container_action_btn,image=self.photo_backward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                            command = lambda: [parent.show_frame(ButtonsTest),self.stop_test()])
        self.btn_previous_frame.image = self.photo_backward_arrow
        self.btn_previous_frame.grid(row=0,column=0,padx=10)

        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png")
        self.btn_next_frame = Button(self.container_action_btn,image=self.photo_forward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                        command = lambda: [parent.show_frame(JoystickTest),self.stop_test()])
        self.btn_next_frame.image = self.photo_forward_arrow
        self.btn_next_frame.grid(row=0,column=1,padx=10)

        self.btn_exit = Button(self.container_action_btn,text="EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_guided_check())
        self.btn_exit.grid(row=1,column=0,columnspan=2,pady=20,padx=20)

    def test_loop(self):
        """ 
            feedrate / Potentiometer test of the jogbox.
            Receive a message via serial.
           
            Parameters
            ----------
            None

            Explanation
            ------------
            Message for button presses are received in HEX form:
                'OFF' (O = Signals its a feedrate command)

            The hex message without the 'O' is converted into decimal representation
            that goes from 0 to 100 in steps of 10

        """
        message = port.readline()
        #print(message)
        if (message[-2:] == b'\r\n'):
            #print(message)
            message = message.decode('Ascii').replace(".", "")
            if (message[:1] == "O"):
                print(message)
                message = int(message[1:], 16)
                self.container_jogbox_feedrate.progressbar_feedrate['value'] = message
                self.test_results[str(message)]= 1
                #print(message)

        self.holder_test_loop = self.app.after(1, self.test_loop)

    def reset_results(self):
        """ 
            Resets the results of the test

            Parameters
            ----------
            None
        """
        self.test_results = {
            "0": 0,
            "10": 0,
            "20": 0,
            "30": 0,
            "40": 0,
            "50": 0,
            "60": 0,
            "70": 0,
            "80": 0,
            "90": 0,
            "100": 0
            }

class JoystickTest(Frame,Functionality):
    """
        A class that holds the joystick test of the jogbox.
        It is to be run inside the guided check class.
        It inherits from the Frame class of tkinter
        and functionality class.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        test_loop: 
            Holds the algorithm to test the x, y and z potentiometer 
            of the jogbox.
        reset_result:
            Reset the results of the button testing
    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object
        
        """
        
        Frame.__init__(self, parent,bg="gray")
        Functionality.__init__(self)

        self.parent = parent

        self.app = parent.parent # Top level app

        self.test_results = {
            "x":{"10": 0,
                "20": 0,
                "30": 0,
                "40": 0,
                "50": 0,
                "60": 0,
                "70": 0,
                "80": 0,
                "90": 0},
            "y":{"10": 0,
                "20": 0,
                "30": 0,
                "40": 0,
                "50": 0,
                "60": 0,
                "70": 0,
                "80": 0,
                "90": 0},
            "z":{"10": 0,
                "20": 0,
                "30": 0,
                "40": 0,
                "50": 0,
                "60": 0,
                "70": 0,
                "80": 0,
                "90": 0}
            }

        Label(self, text="STEP 4: JOYSTICK TESTING",borderwidth=2,bg="gray",fg="#ffffff",bd=2,font=("Robot", 24,"bold")).grid(row=0,column=0,columnspan=2,padx=(120,0),pady=(40,25))

        self.container = LabelFrame(self,bg="#4f4f4f")
        self.container.grid(row=1,column=0,padx=(15,5))

        Label(self.container, text="INSTRUCTIONS: ",borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 20,"bold")).grid(row=0,column=0,pady=(10,10),padx=10)

        help_text = """In this step we will test the function of the x, y and z joystick.\n
        1. Click the "Start" button to begin testing.\n
        2. Move the x, y and z joystick one by one through all its range.\n
        3. The bars on the right will show the corresponding value that is being moved.\n
        4. When you have turned x, y and z through their range click on "Stop".\n
        5. Continue to the next step."""
        Message(self.container, text=help_text,borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,width=400,font=("Robot", 16,"normal"), justify='left').grid(row=1,column=0,padx=(2,0))
        
        self.btn_start_test = Button(self.container, text = "START", bg = "green", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=30,
                            command = lambda: self.start_stop_test())
        self.btn_start_test.grid(row = 2,column = 0,padx=10)

        self.container_jogbox_joystick = JoystickBarsFrame(self.container)
        self.container_jogbox_joystick.grid(row=0,column=1,rowspan=3,padx=(20,0))
        
        self.container_action_btn = LabelFrame(self,bg="#4f4f4f",pady=60)
        self.container_action_btn.grid(row=1,column=2,padx=(5,0))

        self.photo_backward_arrow = PhotoImage(file="icons/ico_left-arrow.png")
        self.btn_previous_frame = Button(self.container_action_btn,image=self.photo_backward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                            command = lambda: [parent.show_frame(FeedrateTest),self.stop_test()])
        self.btn_previous_frame.image = self.photo_backward_arrow
        self.btn_previous_frame.grid(row=0,column=0,padx=10)

        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png")
        self.btn_next_frame = Button(self.container_action_btn,image=self.photo_forward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                        command = lambda: [parent.show_frame(LedTest),self.stop_test()])
                    
        self.btn_next_frame.image = self.photo_forward_arrow
        self.btn_next_frame.grid(row=0,column=1,padx=10)

        self.btn_exit = Button(self.container_action_btn,text="EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_guided_check())
        self.btn_exit.grid(row=1,column=0,columnspan=2,pady=20,padx=20)

    def test_loop(self):
        """ 
            x, y and z potentiometer  test of the jogbox.
            Receive a message via serial.
   
            Parameters
            ----------
            None

            Explanation
            ------------
            Message for button presses are received in HEX form:
                'JFFFFFF' (J = Signals its joystick movement)

            The hex message without the 'J' splits into chunks of 2
                'FF' 'FF' 'FF'
            each chunk represents X, Y and Z correspondingly, we take 
            the HEX representation and turn it into decimal and map it
            from 0 to 100
        """

        message = port.readline()
        #print(message)
        if (message[-2:] == b'\r\n'):
        
            message = message.decode('Ascii').replace(".", "")
            #print(message)
            if (message[:1] == "J"):
                #print(message)
                message = message[1:] # Take out the J
                xyz = (re.findall('.{%d}' % 2, message)) # Split the string in chunks of 2
                xyz[0],xyz[1],xyz[2] = int(xyz[0],16),int(xyz[1],16),int(xyz[2],16)
                xyz[0],xyz[1],xyz[2] = int(self.map_from_to(xyz[0],90,170,0,100)),int(self.map_from_to(xyz[1],90,170,0,100)),int(self.map_from_to(xyz[2],65,190,0,100))
                #print("Joystick ( X: " + str(xyz[0]) + ", Y: " + str(xyz[1]) + ", Z: " + str(xyz[2]) + " )")
                
                self.container_jogbox_joystick.progressbar_x['value'] = xyz[0]
                self.container_jogbox_joystick.progressbar_y['value'] = xyz[1]
                self.container_jogbox_joystick.progressbar_z['value'] = xyz[2]

                for porcentage in self.test_results["x"]:
                        if ((int(porcentage) - 5) < (xyz[0]) < (int(porcentage) + 5)): self.test_results["x"][porcentage]= 1
                        if ((int(porcentage) - 5) < (xyz[1]) < (int(porcentage) + 5)): self.test_results["y"][porcentage]= 1 
                        if ((int(porcentage) - 5) < (xyz[2]) < (int(porcentage) + 5)): self.test_results["z"][porcentage]= 1              
                #print("-----------------------------------------")
                #print(self.test_results)
                

        self.holder_test_loop = self.app.after(1, self.test_loop)

    def reset_results(self):
        """ 
            Resets the results of the test

            Parameters
            ----------
            None
        """

        self.test_results = {
            "x":{"10": 0,
                "20": 0,
                "30": 0,
                "40": 0,
                "50": 0,
                "60": 0,
                "70": 0,
                "80": 0,
                "90": 0},
            "y":{"10": 0,
                "20": 0,
                "30": 0,
                "40": 0,
                "50": 0,
                "60": 0,
                "70": 0,
                "80": 0,
                "90": 0},
            "z":{"10": 0,
                "20": 0,
                "30": 0,
                "40": 0,
                "50": 0,
                "60": 0,
                "70": 0,
                "80": 0,
                "90": 0}
        }

class LedTest(Frame,Functionality):
    """
        A class that holds the led test of the jogbox.
        It is to be run inside the guided check class.
        It inherits from the Frame class of tkinter 
        and functionality class.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        test_loop: 
            Holds the algorithm to test the led of the jogbox
        reset_result:
            Reset the results of the led testing
    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object
        """
    
        Frame.__init__(self, parent,bg="gray")
        Functionality.__init__(self)

        self.parent = parent

        self.app = parent.parent # Top level app

        self.connect_status = self.parent.frames[ConnectionTest].connect_status

        self.test_results = {
            "probe": 0,
            "joystick": 0,
            "turtle": 0,
            "cancel": 0,
            "checkmark": 0,
            "forward": 0,
            "up_down": 0,
            "left_right": 0,
            "turn_up_down": 0,
            "upload": 0,
            "lockpad": 0,
            "jogbox": 0,
            "motor": 0,
            "play_pause": 0
            }

        Label(self, text="STEP 5: LED / BUZZER TESTING",borderwidth=2,bg="gray",fg="#ffffff",bd=2,font=("Robot", 24,"bold")).grid(row=0,column=0,columnspan=2,padx=(125,25),pady=(5,2))

        self.container = LabelFrame(self,bg="#4f4f4f")
        self.container.grid(row=1,column=0,padx=(5,0))

        Label(self.container, text="INSTRUCTIONS: ",borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,font=("Robot", 20,"bold")).grid(row=0,column=0,columnspan=2,padx=20)

        help_text = """In this step we will test the function of the led's and buzzer of the jogbox.\n
        1. Click the "Test led" button to begin ciclying through the led's.\n
        2. On the jogbox check whether all the led's are turning on or not.\n
        3. When the test finishes all the led's will light up followed by 2 beeps.\n
        4. If a certain led is NOT turning on, then click its corresponding button on the interface.\n
        5. Continue to the next step."""
        Message(self.container, text=help_text,borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,width=350,font=("Robot", 16,"normal"), justify='left').grid(row=1,column=0,columnspan=2,padx=(10,5))
        
        self.btn_start_test_led = Button(self.container, text = "TEST LED", bg = "green", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=30,
                                command = lambda: self.led_test(self.parent.frames[ConnectionTest].connect_status))
        self.btn_start_test_led.grid(row = 2,column = 0,padx=10)

        self.btn_start_test_buzzer = Button(self.container, text = "TEST BUZZER", bg = "green", fg = "white", font = ("Robot",14,"bold"),pady=10,padx=30,
                                command = lambda: self.buzzer_test(self.parent.frames[ConnectionTest].connect_status))
        self.btn_start_test_buzzer.grid(row = 2,column = 1,padx=10)

        self.container_jogbox_btn = JogboxKeypadModelButton(self.container,1)
        self.container_jogbox_btn.grid(row=0,column=2,rowspan=4,padx=(20,0))
        
        self.container_action_btn = LabelFrame(self,bg="#4f4f4f",padx=10,pady=60)
        self.container_action_btn.grid(row=1,column=2,padx=(10,0))

        self.photo_backward_arrow = PhotoImage(file="icons/ico_left-arrow.png")
        self.btn_previous_frame = Button(self.container_action_btn,image=self.photo_backward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                                    command = lambda: [parent.show_frame(JoystickTest)])
        self.btn_previous_frame.image = self.photo_backward_arrow
        self.btn_previous_frame.grid(row=0,column=0,padx=10)

        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png")
        self.btn_next_frame = Button(self.container_action_btn,image=self.photo_forward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                                command = lambda: [parent.show_frame(TestResults),self.update_results()])
        self.btn_next_frame.image = self.photo_forward_arrow
        self.btn_next_frame.grid(row=0,column=1,padx=10)

        self.btn_exit = Button(self.container_action_btn,text="EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_guided_check())
        self.btn_exit.grid(row=1,column=0,columnspan=2,pady=20)

    def test_loop(self):
        """ 
            Button test of the jogbox.
            Receive a message via serial.

            Message for button presses are received in HEX form:
                'KFFFF' (K = Signals its a button press)

            The hex message without the 'K' is decoded into a 16 bit binary form:
                '0000000000000000'

            Each bit represents the state of a button on the jogbox as follows:
                Bit = 1, button is active
                Bit = 0 button is not active

                (Position from left to right starting with 0)
                0 = Joystick button
                1 = Upload button
                2 = Turtle button
                3 = Jogbox button
                4 = Checkmark button
                5 = UNUSED
                6 = Motor activate button
                7 = Cancel button
                8 = Z lock button
                9 = Y lock button
                10 = X Lock button
                11 = Probe button
                12 = Forward button
                13 = Play / Pause button
                14 = Lock button
                15 = UNUSED

            Parameters
            ----------
            None
        """
        message = port.readline()
        if (message[-2:] == b'\r\n'):
            message = message.decode('Ascii').replace(".", "")
            if (message[:1] == "K"):
            
                message = message[1:]
                #print(message)
                message = bin(int(message, 16))[2:].zfill(16)
                #print(message)
                if (message[0] == '1'): 
                    self.test_results["joystick"] = 1
                    self.container_jogbox_btn.btn_joystick.press()
                if (message[1] == '1'): 
                    self.test_results["upload"] = 1
                    self.container_jogbox_btn.btn_upload.press()
                if (message[2] == '1'): 
                    self.test_results["turtle"] = 1
                    self.container_jogbox_btn.btn_turtle.press()
                if (message[3] == '1'): 
                    self.test_results["jogbox"] = 1
                    self.container_jogbox_btn.btn_jogbox.press()
                if (message[4] == '1'): 
                    self.test_results["checkmark"] = 1
                    self.container_jogbox_btn.btn_checkmark.press()
                if (message[6] == '1'): 
                    self.test_results["motor"] = 1
                    self.container_jogbox_btn.btn_motor.press()
                if (message[7] == '1'): 
                    self.test_results["cancel"] = 1
                    self.container_jogbox_btn.btn_cancel.press()
                if (message[8] == '1'): 
                    self.test_results["turn_up_down"] = 1
                    self.container_jogbox_btn.btn_turn_up_down_arrow.press()
                if (message[9] == '1'): 
                    self.test_results["up_down"] = 1
                    self.container_jogbox_btn.btn_up_down_arrow.press()
                if (message[10] == '1'): 
                    self.test_results["left_right"] = 1
                    self.container_jogbox_btn.btn_left_right_arrow.press()
                if (message[11] == '1'): 
                    self.test_results["probe"] = 1
                    self.container_jogbox_btn.btn_probe.press()
                if (message[12] == '1'): 
                    self.test_results["forward"] = 1
                    self.container_jogbox_btn.btn_forward_arrow.press()
                if (message[13] == '1'): 
                    self.test_results["play_pause"] = 1
                    self.container_jogbox_btn.btn_play_pause.press()
                if (message[14] == '1'): 
                    self.test_results["lockpad"] = 1
                    self.container_jogbox_btn.btn_lockpad.press()
                

        self.holder_test_loop = self.app.after(1, self.test_loop)
    
    def reset_results(self):
        """ 
            Resets the results of the test

            Parameters
            ----------
            None
        """
        
        self.test_results = {
            "probe": 0,
            "joystick": 0,
            "turtle": 0,
            "cancel": 0,
            "checkmark": 0,
            "forward": 0,
            "up_down": 0,
            "left_right": 0,
            "turn_up_down": 0,
            "upload": 0,
            "lockpad": 0,
            "jogbox": 0,
            "motor": 0,
            "play_pause": 0
            }

class TestResults(Frame, Functionality):
    """
        A class that holds the test results interface of the jogbox.
        It is to be run inside the guided check class.
        It inherits from the Frame class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        reset_results: 
            Reset the results of the led testing
        clear_all:
            Sets the UI of the test results to default
    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the StartPage object    
        """
        
        Frame.__init__(self, parent,bg="gray")
        Functionality.__init__(self)

        self.parent = parent

        self.app = parent.parent # Top level app

        self.test_results = {
            "x": 0,
            "y": 0,
            "z": 0,
            "feedrate": 0
            }

        Label(self, text="STEP 6: RESULTS",borderwidth=2,bg="gray",fg="#ffffff",bd=2,font=("Robot", 24,"bold")).grid(row=0,column=0,columnspan=2,padx=(120,0),pady=(5,5))

        self.container = LabelFrame(self,bg="#4f4f4f")
        self.container.grid(row=1,column=0,padx=(30,10))

        help_text = """For each of the test we performed on the jogbox we have a corresponding result box\n
                Each box will show:\n
                -RED: Not detected or not working\n
                -GREEN: Detected and functioning correctly"""
        Message(self.container, text=help_text,borderwidth=2,bg="#4f4f4f",fg="#ffffff",bd=2,width=150,font=("Robot", 14,"bold"), justify='left').grid(row=1,column=0,padx=(40,20))
        
        self.lbl_result_x = Label(self.container, text = "JOYSTICK X",borderwidth=3,relief="groove", bg = "red", fg = "white", font = ("Robot",16,"bold"),padx=10,pady=10)
        self.lbl_result_x.grid(row = 2,column = 0,pady=5,padx=2)

        self.lbl_result_y = Label(self.container, text = "JOYSTICK Y",borderwidth=3,relief="groove", bg = "red", fg = "white", font = ("Robot",16,"bold"),padx=10,pady=10)
        self.lbl_result_y.grid(row = 3,column = 0,pady=5,padx=2)

        self.lbl_result_z = Label(self.container, text = "JOYSTICK Z",borderwidth=3,relief="groove", bg = "red", fg = "white", font = ("Robot",16,"bold"),padx=10,pady=10)
        self.lbl_result_z.grid(row = 4,column = 0,pady=5,padx=2)

        self.lbl_result_feedrate = Label(self.container, text = "FEEDRATE",borderwidth=3,relief="groove", bg = "red", fg = "white", font = ("Robot",16,"bold"),padx=15,pady=10)
        self.lbl_result_feedrate.grid(row = 5,column = 0,pady=5,padx=2)
        
        Label(self.container, text="KEYPAD",borderwidth=2, wraplength=1,bg="#4F4F4F",fg="white",bd=2,font=("Robot", 35,"bold")).grid(row=0,rowspan=6,column=1,padx=(10,0))

        self.container_jogbox_btn = JogboxKeypadModelLabel(self.container)
        self.container_jogbox_btn.fail_all()
        self.container_jogbox_btn.grid(row=0,column=2,rowspan=6,padx=(0,10))

        Label(self.container, text="LEDS",borderwidth=2, wraplength=1,bg="#4F4F4F",fg="white",bd=2,font=("Robot", 35,"bold")).grid(row=0,rowspan=6,column=3)

        self.container_jogbox_led = JogboxKeypadModelLabel(self.container, 1)
        self.container_jogbox_led.press_all()
        self.container_jogbox_led.grid(row=0,column=4,rowspan=6,padx=(0,0))
      
        self.container_action_btn = LabelFrame(self,bg="#4f4f4f",pady=110)
        self.container_action_btn.grid(row=1,column=2,padx=(10,0))

        self.photo_backward_arrow = PhotoImage(file="icons/ico_left-arrow.png")
        self.btn_previous_frame = Button(self.container_action_btn,image=self.photo_backward_arrow, bg = "#383838", fg = "black", font = ("Robot",20,"bold"),
                            command = lambda: parent.show_frame(LedTest))
        self.btn_previous_frame.image = self.photo_backward_arrow
        self.btn_previous_frame.grid(row=0,column=0,padx=5)

        self.btn_exit = Button(self.container_action_btn,text="EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_guided_check())
        self.btn_exit.grid(row=1,column=0,pady=20,padx=10)

    def reset_results (self):
        """ 
            Resets the results of the test

            Parameters
            ----------
            None
        """
        self.test_results = {
            "x": 0,
            "y": 0,
            "z": 0,
            "feedrate": 0
            }
    
    def clear_all(self):
        """ 
            Sets the UI to the default state

            Parameters
            ----------
            None
        """
        self.lbl_result_x['bg']= "red"
        self.lbl_result_y['bg']= "red"
        self.lbl_result_z['bg']= "red"
        self.lbl_result_feedrate['bg']= "red"
        self.container_jogbox_btn.fail_all()
        self.container_jogbox_led.press_all()

class GuidedCheck(Frame, Base):
    """
        A class that holds guided check interface of the jogbox.
        It is to be run inside the main page, and holds child tests objects.
        It inherits from the Frame class of tkinter and the Base class.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        None
    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the object
        """
        
        Frame.__init__(self, parent,bg="gray")
        Base.__init__(self)

        self.parent = parent

        self.load_frames(ConnectionTest, ButtonsTest, FeedrateTest, JoystickTest, LedTest, TestResults)

        self.show_frame(ConnectionTest)
            
class JogboxMonitorMode(Frame, Functionality):
    """
        A class that holds the monitor mode of the app.
        It is to be run inside the main page.
        It inherits from the Frame class of tkinter and the Functionality class.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        None
    """

    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the object
        """
        
        Frame.__init__(self, parent,bg="gray")

        Functionality.__init__(self)

        self.parent = parent

        self.holder_connection_to_jogbox_loop = None

        self.holder_test_loop = None
        
        Label(self, text="MONITOR MODE",borderwidth=2,bg="gray",fg="white",bd=2,font=("Robot", 26,"bold")).grid(row=0,column=0,columnspan=6,pady=(5,5))

        Label(self, text="JOYSTICK",borderwidth=2, wraplength=1,bg="gray",fg="white",bd=2,font=("Robot", 22,"bold")).grid(row=1,column=0,padx=(10,0))
        self.container_jogbox_joystick = JoystickBarsFrame(self)
        self.container_jogbox_joystick.grid(row=1,column=1,pady=10,padx=(10,15))

        Label(self, text="FEEDRATE",borderwidth=2, wraplength=1,bg="gray",fg="white",bd=2,font=("Robot", 22,"bold")).grid(row=1,column=2)
        self.container_jogbox_feedrate = FeedrateBarFrame(self)
        self.container_jogbox_feedrate.grid(row=1,column=3,pady=10,padx=(10,15))
        
        Label(self, text="KEYPAD",borderwidth=2, wraplength=1,bg="gray",fg="white",bd=2,font=("Robot", 22,"bold")).grid(row=1,column=4)
        self.container_jogbox_btn = JogboxKeypadModelLabel(self)
        self.container_jogbox_btn.grid(row=1,column=5,pady=10,padx=(10,15))

        Label(self, text="ACTIONS",borderwidth=2, wraplength=1,bg="gray",fg="white",bd=2,font=("Robot", 22,"bold")).grid(row=1,column=6)
        self.container_action_btn = LabelFrame(self,pady=40,bg="#4f4f4f")
        self.container_action_btn.grid(row=1,column=7,padx=(10,60))

        self.btn_connect_serial = Button(self.container_action_btn, text = "CONNECT SERIAL", bg = "#383838", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=5,
                                    command = lambda: self.connect_serial())
        self.btn_connect_serial.grid(row = 1,column = 0,pady=3,padx=10)

        self.lbl_serial_status = Label(self.container_action_btn, text = "I/0",borderwidth=3,relief="groove", bg = "red", fg = "white", font = ("Robot",30,"bold"),padx=10,pady=10)
        self.lbl_serial_status.grid(row = 1,column = 1,pady=5,padx=10)

        self.btn_led_test = Button(self.container_action_btn, text = "TEST LEDS", bg = "#383838", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=30,
                            command = lambda: self.led_test(self.connect_status))
        self.btn_led_test.grid(row = 2,column = 0,columnspan=2,pady=10,padx=5)

        self.btn_buzzer_test = Button(self.container_action_btn, text = "TEST BUZZER", bg = "#383838", fg = "white", font = ("Robot",15,"bold"),pady=10,padx=22,
                                command = lambda: self.buzzer_test(self.connect_status))
        self.btn_buzzer_test.grid(row = 3,column = 0,columnspan=2,pady=10,padx=5)
        
        self.btn_exit = Button(self.container_action_btn, text = "EXIT", bg = "red", fg = "white", font = ("Robot",25,"bold"),
                        command = lambda: self.exit_monitor_mode())
        self.btn_exit.grid(row = 4,column = 0,columnspan=2,pady=(20,10),padx=20)

class FeedrateBarFrame(LabelFrame):
    """
        A class that holds the UI for the feedrate.
        It inherits from the LabelFrame class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        None
    """
    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the object
        """
        LabelFrame.__init__(self,parent,bg="#4f4f4f")

        Label(self, text="100%",borderwidth=2,bg="#4f4f4f",fg="#ffffff", anchor='ne', height=7,font=("Robot", 20,"bold") ).grid(row=1,column=0)
        Label(self, text="0%",borderwidth=2,bg="#4f4f4f",fg="#ffffff", anchor='se', height=7,font=("Robot", 20,"bold") ).grid(row=5,column=0)

        self.progressbar_feedrate = Progressbar(self, length = 240,orient='vertical')
        self.progressbar_feedrate['value'] = 50
        self.progressbar_feedrate.grid(column = 1, row = 1, rowspan=5,padx=(5,20),pady=7)
        
class JoystickBarsFrame(LabelFrame):
    """
        A class that holds the UI for the x, y and z joystick.
        It inherits from the LabelFrame class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        
        Methods
        -------
        None
    """
    def __init__(self, parent):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the object
        """
        LabelFrame.__init__(self,parent,bg="#4f4f4f")

        Label(self, text="100",borderwidth=2,bg="#4f4f4f",fg="#ffffff", anchor='ne', height=6,font=("Robot", 20,"bold") ).grid(row=1,column=0)
        Label(self, text="0",borderwidth=2,bg="#4f4f4f",fg="#ffffff", anchor='e',font=("Robot", 20,"bold")).grid(row=3,column=0)
        Label(self, text="-100",borderwidth=2,bg="#4f4f4f",fg="#ffffff", anchor='se', height=6,font=("Robot", 20,"bold")).grid(row=5,column=0)

        Label(self, text="X",borderwidth=2,bg="#4f4f4f",fg="#ffffff",font=("Robot", 25,"bold")).grid(row=0,column=1)
        Label(self, text="Y",borderwidth=2,bg="#4f4f4f",fg="#ffffff",font=("Robot", 25,"bold")).grid(row=0,column=2)
        Label(self, text="Z",borderwidth=2,bg="#4f4f4f",fg="#ffffff",font=("Robot", 25,"bold")).grid(row=0,column=3)

        self.progressbar_x = Progressbar(self, length = 225,orient='vertical')
        self.progressbar_x['value'] = 50
        self.progressbar_x.grid(column = 1, row = 1, rowspan=5,padx=(5,10),pady=(0,5))

        self.progressbar_y = Progressbar(self, length = 225,orient='vertical')
        self.progressbar_y['value'] = 50
        self.progressbar_y.grid(column = 2, row = 1, rowspan=5,padx=(10,10),pady=(0,5))

        self.progressbar_z = Progressbar(self, length = 225,orient='vertical')
        self.progressbar_z['value'] = 50
        self.progressbar_z.grid(column = 3, row = 1, rowspan=5,padx=(10,20),pady=(0,5))

class JogboxKeypadModelLabel(LabelFrame):
    """
        A class that holds the UI for the Keypad of jogbox 
        and shows them as labels.
        It inherits from the LabelFrame class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        for_led : Integer
            1: We show UI for the leds
            0: We show UI for keypad
        
        Methods
        -------
        None
    """

    def __init__(self, parent, for_led = 0):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the object
            for_led : Integer
                1: We show UI for the leds
                0: We show UI for keypad
        """
        self.for_led = for_led
        
        LabelFrame.__init__(self,parent,bg="#4f4f4f")
        
        self.photo_probe = PhotoImage(file= "icons/ico_probe.png").subsample(2,2)
        self.btn_probe = JogboxButtonModelLabel(self,self.photo_probe,0,0)
        
        if self.for_led == 0:
            self.photo_joystick = PhotoImage(file= "icons/ico_start_joystick.png").subsample(2,2)
            self.btn_joystick= JogboxButtonModelLabel(self,self.photo_joystick,0,1)

        self.photo_turtle = PhotoImage(file= "icons/ico_turtle.png").subsample(2,2)
        self.btn_turtle= JogboxButtonModelLabel(self,self.photo_turtle,0,2)

        self.photo_cancel = PhotoImage(file= "icons/ico_x.png").subsample(2,2)
        self.btn_cancel= JogboxButtonModelLabel(self,self.photo_cancel,1,0)

        self.photo_checkmark = PhotoImage(file= "icons/ico_check.png").subsample(2,2)
        self.btn_checkmark= JogboxButtonModelLabel(self,self.photo_checkmark,1,1)

        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png").subsample(2,2)
        self.btn_forward_arrow= JogboxButtonModelLabel(self,self.photo_forward_arrow,1,2)

        self.photo_up_down_arrow = PhotoImage(file="icons/ico_up-down-arrow.png").subsample(2,2)
        self.btn_up_down_arrow= JogboxButtonModelLabel(self,self.photo_up_down_arrow,2,0)

        self.photo_left_right_arrow = PhotoImage(file= "icons/ico_left-right-arrow.png").subsample(2,2)
        self.btn_left_right_arrow= JogboxButtonModelLabel(self,self.photo_left_right_arrow,2,1)

        self.photo_turn_up_down_arrow = PhotoImage(file= "icons/ico_turn-up-down-arrow.png").subsample(2,2)
        self.btn_turn_up_down_arrow= JogboxButtonModelLabel(self,self.photo_turn_up_down_arrow,2,2)

        self.photo_upload = PhotoImage(file= "icons/ico_upload.png").subsample(2,2)
        self.btn_upload= JogboxButtonModelLabel(self,self.photo_upload,3,0)

        self.photo_lockpad = PhotoImage(file= "icons/ico_padlock.png").subsample(2,2)
        self.btn_lockpad= JogboxButtonModelLabel(self,self.photo_lockpad,3,2)

        if self.for_led == 1:
            self.container = Frame(self,bg = "#4f4f4f")
            self.container.grid(row=4,column=0,pady=2)

            self.photo_jogbox = PhotoImage(file= "icons/ico_joystick.png").subsample(3,4)
            self.btn_jogbox_1= JogboxButtonModelLabel(self.container,self.photo_jogbox,0,0)
            self.btn_jogbox_1.grid(row=0,column=0,pady=2)
            
            self.btn_jogbox_2= JogboxButtonModelLabel(self.container,self.photo_jogbox,1,0)
            self.btn_jogbox_2.grid(row=1,column=0,pady=2)
            
            self.btn_jogbox_3= JogboxButtonModelLabel(self.container,self.photo_jogbox,2,0)
            self.btn_jogbox_3.grid(row=2,column=0,pady=2)
        else:
            self.photo_jogbox = PhotoImage(file= "icons/ico_joystick.png").subsample(2,2)
            self.btn_jogbox= JogboxButtonModelLabel(self,self.photo_jogbox,4,0)

        self.photo_motor_btn = PhotoImage(file= "icons/ico_motor.png").subsample(2,2)
        self.btn_motor= JogboxButtonModelLabel(self,self.photo_motor_btn,4,1)

        self.photo_play_pause = PhotoImage(file= "icons/ico_play-pause.png").subsample(2,2)
        self.btn_play_pause= JogboxButtonModelLabel(self,self.photo_play_pause,4,2)
    
    def unpress_all(self):
        """ 
            Unpress all the labels in the keypad

            Parameters
            ----------
            None
        """
        self.btn_probe.unpress()
        if self.for_led == 0: self.btn_joystick.unpress()
        self.btn_turtle.unpress()
        self.btn_cancel.unpress()
        self.btn_checkmark.unpress()
        self.btn_forward_arrow.unpress()
        self.btn_up_down_arrow.unpress()
        self.btn_left_right_arrow.unpress()
        self.btn_turn_up_down_arrow.unpress()
        self.btn_upload.unpress()
        self.btn_lockpad.unpress()
        if self.for_led == 1:
            self.btn_jogbox_1.unpress()
            self.btn_jogbox_2.unpress()
            self.btn_jogbox_3.unpress()
        else: 
            self.btn_jogbox.unpress()
        self.btn_motor.unpress()
        self.btn_play_pause.unpress() 
    
    def press_all(self):
        """ 
            Press all the labels in the keypad

            Parameters
            ----------
            None
        """
        self.btn_probe.press()
        if self.for_led == 0: self.btn_joystick.press()
        self.btn_turtle.press()
        self.btn_cancel.press()
        self.btn_checkmark.press()
        self.btn_forward_arrow.press()
        self.btn_up_down_arrow.press()
        self.btn_left_right_arrow.press()
        self.btn_turn_up_down_arrow.press()
        self.btn_upload.press()
        self.btn_lockpad.press()
        if self.for_led == 1:
            self.btn_jogbox_1.press()
            self.btn_jogbox_2.press()
            self.btn_jogbox_3.press()
        else: 
            self.btn_jogbox.press()
        self.btn_motor.press()
        self.btn_play_pause.press() 

    def fail_all(self):
        """ 
            Fail all the labels in the keypad

            Parameters
            ----------
            None
        """
        self.btn_probe.btn_fail()
        if self.for_led == 0: self.btn_joystick.btn_fail()
        self.btn_turtle.btn_fail()
        self.btn_cancel.btn_fail()
        self.btn_checkmark.btn_fail()
        self.btn_forward_arrow.btn_fail()
        self.btn_up_down_arrow.btn_fail()
        self.btn_left_right_arrow.btn_fail()
        self.btn_turn_up_down_arrow.btn_fail()
        self.btn_upload.btn_fail()
        self.btn_lockpad.btn_fail()
        if self.for_led == 1:
            self.btn_jogbox_1.btn_fail()
            self.btn_jogbox_2.btn_fail()
            self.btn_jogbox_3.btn_fail()
        else:
            self.btn_jogbox.btn_fail()
        self.btn_motor.btn_fail()
        self.btn_play_pause.btn_fail()       

class JogboxKeypadModelButton(LabelFrame):
    """
        A class that holds the UI for the Keypad of jogbox 
        and shows them as buttons.
        It inherits from the LabelFrame class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        for_led : Integer
            1: We show UI for the leds
            0: We show UI for keypad
        
        Methods
        -------
        None
    """
    def __init__(self, parent, for_led = 0):
        """
            Parameters
            ----------
            parent : tk class 
                object that is to hold the object
            for_led : Integer
                1: We show UI for the leds
                0: We show UI for keypad
        """
        self.for_led = for_led
        LabelFrame.__init__(self,parent,bg="#4f4f4f")
        
        self.photo_probe = PhotoImage(file= "icons/ico_probe.png").subsample(2,2)
        self.btn_probe = JogboxButtonModelButton(self,self.photo_probe,0,0)
        
        if self.for_led == 0:
            self.photo_joystick = PhotoImage(file= "icons/ico_start_joystick.png").subsample(2,2)
            self.btn_joystick= JogboxButtonModelButton(self,self.photo_joystick,0,1)

        self.photo_turtle = PhotoImage(file= "icons/ico_turtle.png").subsample(2,2)
        self.btn_turtle= JogboxButtonModelButton(self,self.photo_turtle,0,2)

        self.photo_cancel = PhotoImage(file= "icons/ico_x.png").subsample(2,2)
        self.btn_cancel= JogboxButtonModelButton(self,self.photo_cancel,1,0)

        self.photo_checkmark = PhotoImage(file= "icons/ico_check.png").subsample(2,2)
        self.btn_checkmark= JogboxButtonModelButton(self,self.photo_checkmark,1,1)

        self.photo_forward_arrow = PhotoImage(file="icons/ico_right-arrow.png").subsample(2,2)
        self.btn_forward_arrow= JogboxButtonModelButton(self,self.photo_forward_arrow,1,2)

        self.photo_up_down_arrow = PhotoImage(file="icons/ico_up-down-arrow.png").subsample(2,2)
        self.btn_up_down_arrow= JogboxButtonModelButton(self,self.photo_up_down_arrow,2,0)

        self.photo_left_right_arrow = PhotoImage(file= "icons/ico_left-right-arrow.png").subsample(2,2)
        self.btn_left_right_arrow= JogboxButtonModelButton(self,self.photo_left_right_arrow,2,1)

        self.photo_turn_up_down_arrow = PhotoImage(file= "icons/ico_turn-up-down-arrow.png").subsample(2,2)
        self.btn_turn_up_down_arrow= JogboxButtonModelButton(self,self.photo_turn_up_down_arrow,2,2)

        self.photo_upload = PhotoImage(file= "icons/ico_upload.png").subsample(2,2)
        self.btn_upload= JogboxButtonModelButton(self,self.photo_upload,3,0)

        self.photo_lockpad = PhotoImage(file= "icons/ico_padlock.png").subsample(2,2)
        self.btn_lockpad= JogboxButtonModelButton(self,self.photo_lockpad,3,2)

        if self.for_led == 1:
            self.container = Frame(self,bg = "#4f4f4f")
            self.container.grid(row=4,column=0,pady=2)

            self.photo_jogbox = PhotoImage(file= "icons/ico_joystick.png").subsample(3,4)
            self.btn_jogbox_1= JogboxButtonModelButton(self.container,self.photo_jogbox,0,0)
            self.btn_jogbox_1.grid(row=0,column=0,pady=2)
            
            self.btn_jogbox_2= JogboxButtonModelButton(self.container,self.photo_jogbox,1,0)
            self.btn_jogbox_2.grid(row=1,column=0,pady=2)
            
            self.btn_jogbox_3= JogboxButtonModelButton(self.container,self.photo_jogbox,2,0)
            self.btn_jogbox_3.grid(row=2,column=0,pady=2)
        
        else:
            self.photo_jogbox = PhotoImage(file= "icons/ico_joystick.png").subsample(2,2)
            self.btn_jogbox= JogboxButtonModelButton(self,self.photo_jogbox,4,0)

        self.photo_motor_btn = PhotoImage(file= "icons/ico_motor.png").subsample(2,2)
        self.btn_motor= JogboxButtonModelButton(self,self.photo_motor_btn,4,1)

        self.photo_play_pause = PhotoImage(file= "icons/ico_play-pause.png").subsample(2,2)
        self.btn_play_pause= JogboxButtonModelButton(self,self.photo_play_pause,4,2)

    def unpress_all(self):
        """ 
            Unpress all the buttons in the keypad

            Parameters
            ----------
            None
        """
        self.btn_probe.unpress()
        if self.for_led == 0: self.btn_joystick.unpress()
        self.btn_turtle.unpress()
        self.btn_cancel.unpress()
        self.btn_checkmark.unpress()
        self.btn_forward_arrow.unpress()
        self.btn_up_down_arrow.unpress()
        self.btn_left_right_arrow.unpress()
        self.btn_turn_up_down_arrow.unpress()
        self.btn_upload.unpress()
        self.btn_lockpad.unpress()
        if self.for_led == 1:
            self.btn_jogbox_1.unpress()
            self.btn_jogbox_2.unpress()
            self.btn_jogbox_3.unpress()
        else:
            self.btn_jogbox.unpress()
        self.btn_motor.unpress()
        self.btn_play_pause.unpress() 
               
class JogboxButtonModelLabel(Label):
    """
        A class that holds the UI for a single button of the jogbox
        it show it as a label.
        It inherits from the Label class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        icon: PhotoImage class
            Icon to display in the button
        row: Integer
            Row to put the button in
        column: Integer
            Column to put the button in
        
        Methods
        -------
        press:
            Sets the color of the button to green
        unpress:
            Sets the color of the button to dark gray
        btn_fail:
            Sets the color of the button to red

    """
    def __init__(self,parent,icon,row,column):
        """
            Parameters
            ----------
            parent : tk class 
                Parent object that is to hold the object
            icon: PhotoImage class
                Icon to display in the button
            row: Integer
                Row to put the button in
            column: Integer
                Column to put the button in
        """
        Label.__init__(self,parent,image = icon,bg = "#383838", fg = "black",borderwidth=4, relief="groove")
        self.image= icon
        self.grid(row=row,column=column,pady=13,padx=10)
    
    def press(self):
        """ 
            Turns the color of the button to green

            Parameters
            ----------
            None
        """
        self['bg'] = "green"

    def unpress(self): 
        """ 
            Turns the color of the button to dark gray (default)

            Parameters
            ----------
            None
        """
        self['bg'] = "#383838"

    def btn_fail(self): 
        """ 
            Turns the color of the button to red

            Parameters
            ----------
            None
        """
        self['bg'] = "red"
  
class JogboxButtonModelButton(Button):
    """
        A class that holds the UI for a single button of the jogbox
        it show it as a button.
        It inherits from the button class of tkinter.
        ...

        Attributes
        ----------
        parent : tk class 
            Parent object that is to hold the object
        icon: PhotoImage class
            Icon to display in the button
        row: Integer
            Row to put the button in
        column: Integer
            Column to put the button in
        
        Methods
        -------
        press:
            Sets the color of the button to green
        unpress:
            Sets the color of the button to dark gray
        

    """
    def __init__(self,parent,icon,row,column):
        """
            Parameters
            ----------
            parent : tk class 
                Parent object that is to hold the object
            icon: PhotoImage class
                Icon to display in the button
            row: Integer
                Row to put the button in
            column: Integer
                Column to put the button in
        """
        Button.__init__(self,parent,image = icon,bg = "#383838", fg = "black",borderwidth=4,command = lambda: self.press())
        self.image= icon
        self.grid(row=row,column=column,pady=13,padx=10)

        self.btn_status = 0

    def press(self):
        """ 
            Switches between button states 1(red) and 0(green)

            Parameters
            ----------
            None
        """
        if (self.btn_status == 0):
            self['bg'] = "red"
            self.btn_status = 1
        elif (self.btn_status == 1):
            self['bg'] = "#383838"
            self.btn_status = 0
    
    def unpress(self):
        """ 
            
            Set the state of the button to 0.
            Turns the color of the button to dark gray (defalut).

            Parameters
            ----------
            None
        """
        self['bg'] = "#383838"
        self.btn_status = 0

if __name__ == "__main__":
    app = App(scale = 0.58)
    app.mainloop()
