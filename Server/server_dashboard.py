import tkinter as tk
import time
import server_core_modules

class Controller_Dashboard:
    ##__________________________________________MQTT___________________________________

    def __init__(self):

        self.root = tk.Tk()    
        self.server = server_core_modules.Server_Controller(log_func=self.Print_onShellOutput)
        self.server.MQTT_thread_handler.setDaemon(True)

        self.selected_client = 0
        self.init_menubar()
        self.init_tkinter_elements()
        self.init_Lists()
        
    #_____________________________________________FUNCTIONS____________________________

    def on_connect(self,client,userdata, flags, rc):
        print("Connect")
        self.Print_onShellOutput("Connected to broker " + self.server.selected_broker[0] + " with result code " + str(rc))
        self.server.Subscribe_to_All()

    def on_message(self,client,userdata, msg):
        self.Print_onShellOutput(msg.payload.decode())

    def Connect_to_Broker(self):
        self.server.Connect_to_Selected_Broker(self.on_connect,self.on_message) 
        
    def Client_PowerOn(self):
        print(self.selected_client)
        self.server.Client_PowerOn(self.selected_client,self.refresh_client_list)
    
    def Client_PowerOff(self):
        self.server.Client_PowerOff(self.selected_client,self.refresh_client_list)

    def Print_onShellOutput(self,msg):
        print(msg)
        self.shell_output.config(state= tk.NORMAL)
        self.shell_output.insert(tk.END, "\n" + msg )
        self.shell_output.see(tk.END)
        self.shell_output.config(state= tk.DISABLED)

    def CheckEntry(self,e):
        self.Print_onShellOutput("CONTROLLER::INPUT>> "  + self.userInput.get())
        self.userInput.delete(0,'end')

    def donothing():
        x = 0

    def print_hello():
        print("Hello")

    
    def refresh_client_list(self):
        self.Lb1.delete(0,tk.END)
        cc = 0
        for item in self.server.client_list:
            self.Lb1.insert(cc, item.name + " | " + item.type + " | " + item.status)
            cc += 1

    ##____________________________________________LIST SELECT FUNCTIONS _______________

    def broker_list_function(self,e):
        self.server.selected_broker = self.server.broker_list[self.Lb2.curselection()[0]]
        print("Selected Broker now is: " + self.server.selected_broker[0])
    
    def client_list_function(self,e):
        self.selected_client = self.Lb1.curselection()[0]
    
    ##____________________________________________INITIALIZERS__________________________

    def init_Lists(self):
        #CLIENT LIST
            cc = 0
            for item in self.server.client_list:
                self.Lb1.insert(cc, item.name + " | " + item.type + " | " + item.status)
                cc += 1
        #BROKER LIST
            bc = 0
            for item in self.server.broker_list:
                self.Lb2.insert(bc, item[0])
                bc += 1

        #CLIENT PROPERTIES

        #EXECUTABLE LIST

    def init_menubar(self):

        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.donothing)
        filemenu.add_command(label="Open", command=self.donothing)
        filemenu.add_command(label="Save", command=self.donothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=self.donothing)
        helpmenu.add_command(label="About...", command=self.donothing)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=self.menubar)


    def init_tkinter_elements(self):

        self.right_frame = tk.Frame(self.root, bd=2)
        self.left_frame = tk.Frame(self.root, bd=2)
        self.inner_right_top_frame = tk.Frame(self.right_frame, bd=3)
        self.inner_right_bottom_frame = tk.Frame(self.right_frame, bd=2)

        self.action_buttons_frame = tk.Frame(self.right_frame, bd=10)

        self.Lb1 = tk.Listbox(self.left_frame, justify="left",background="#26242f",foreground="white")
        #Lb1.insert(1, "list1")
        self.Lb2 = tk.Listbox(self.left_frame, justify="left",background="#26242f",foreground="white")
        self.Lb3 = tk.Listbox(self.inner_right_top_frame,justify="left",background="#26242f",foreground="white")
        #Lb3.insert(1, "list3")
        self.Lb4 = tk.Listbox(self.inner_right_top_frame,justify="left",background="#26242f",foreground="white")
        #Lb4.insert(1, "list4")

        self.userInput = tk.Entry(self.inner_right_bottom_frame,background="#26244c",foreground="white")
        self.shell_output = tk.Text(self.inner_right_bottom_frame,background="#26242f",foreground="white",height=2,width=1)

        self.ac_bt0 = tk.Button(self.action_buttons_frame,text="Power ON")
        self.ac_bt1 = tk.Button(self.action_buttons_frame,text="Power OFF")
        self.ac_bt2 = tk.Button(self.action_buttons_frame,text="3"    ,command=self.print_hello)
        self.ac_bt3 = tk.Button(self.action_buttons_frame,text="4"    ,command=self.print_hello)
        self.ac_bt4 = tk.Button(self.action_buttons_frame,text="5"    ,command=self.print_hello)
        self.ac_bt5 = tk.Button(self.action_buttons_frame,text="6"    ,command=self.print_hello)
        self.ac_bt6 = tk.Button(self.action_buttons_frame,text="7"    ,command=self.print_hello)
        self.ac_bt7 = tk.Button(self.action_buttons_frame,text="8"    ,command=self.print_hello)
        self.ac_bt8 = tk.Button(self.action_buttons_frame,text="9"    ,command=self.print_hello)
        self.ac_bt9 = tk.Button(self.action_buttons_frame,text="Connect to Broker")

        self.userInput.bind("<Return>",self.CheckEntry)
        self.Lb2.bind("<<ListboxSelect>>", self.broker_list_function)
        self.Lb1.bind("<<ListboxSelect>>", self.client_list_function)
        
        self.root.title("MQTT Fleet Controller Dashboard")
        self.root.config(bg="#26242f")   
        self.root.geometry("1440x800")

        self.rootHeight = self.root.winfo_height()
        self.rootWidth =  self.root.winfo_width()

        self.root.rowconfigure(0, weight=1)
        # root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=4)

        self.right_frame.columnconfigure(0,weight=1)
        self.right_frame.rowconfigure(0)
        self.right_frame.rowconfigure(1,weight=10)
        self.right_frame.rowconfigure(2,weight=10)

        self.left_frame.columnconfigure(0,weight=1)
        self.left_frame.rowconfigure(0,weight=2)
        self.left_frame.rowconfigure(1,weight=1)

        self.inner_right_top_frame.columnconfigure(0,weight=1)
        self.inner_right_top_frame.columnconfigure(1,weight=1)
        self.inner_right_top_frame.rowconfigure(0,weight=1)

        self.inner_right_bottom_frame.columnconfigure(0,weight=1)
        self.inner_right_bottom_frame.rowconfigure(0,weight=7)
        self.inner_right_bottom_frame.rowconfigure(1,weight=1)

        self.action_buttons_frame.rowconfigure(0,weight=1)
        self.action_buttons_frame.columnconfigure(0,weight=1)
        self.action_buttons_frame.columnconfigure(1,weight=1)
        self.action_buttons_frame.columnconfigure(2,weight=1)
        self.action_buttons_frame.columnconfigure(3,weight=1)
        self.action_buttons_frame.columnconfigure(4,weight=1)
        self.action_buttons_frame.columnconfigure(5,weight=1)
        self.action_buttons_frame.columnconfigure(6,weight=1)
        self.action_buttons_frame.columnconfigure(7,weight=1)
        self.action_buttons_frame.columnconfigure(8,weight=1)
        self.action_buttons_frame.columnconfigure(9,weight=1)

        self.right_frame                 .grid(row=0,column=1,sticky='nwse',padx=2,pady=2)
        self.left_frame                  .grid(row=0,column=0,sticky='nwse',padx=2,pady=2)
        self.action_buttons_frame        .grid(row=0,column=0,sticky='nwse',padx=1,pady=1)
        self.inner_right_top_frame       .grid(row=1,column=0,sticky='nwse',padx=1,pady=1)
        self.inner_right_bottom_frame    .grid(row=2,column=0,sticky='nwse',padx=1,pady=1)
        self.Lb1.grid(row=0,column=0,sticky='nwse',padx=1,pady=1)
        #self.Lb2.grid(row=1,column=0,sticky='nwse',padx=1,pady=1)
        #self.Lb3.grid(row=0,column=0,sticky='nwse',padx=1,pady=1)
        #self.Lb4.grid(row=0,column=1,sticky='nwse',padx=1,pady=1)
        self.shell_output.grid(row=0,column=0,sticky='nwse',padx=2,pady=2)
        #self.userInput.grid(row=1,column=0,sticky='nwse',padx=2,pady=2)
        self.ac_bt0.grid(row=0,column=0,sticky='nswe')
        self.ac_bt1.grid(row=0,column=1,sticky='nswe')
        # self.ac_bt2.grid(row=0,column=2,sticky='nswe')
        # self.ac_bt3.grid(row=0,column=3,sticky='nswe')
        # self.ac_bt4.grid(row=0,column=4,sticky='nswe')
        # self.ac_bt5.grid(row=0,column=5,sticky='nswe')
        # self.ac_bt6.grid(row=0,column=6,sticky='nswe')
        # self.ac_bt7.grid(row=0,column=7,sticky='nswe')
        # self.ac_bt8.grid(row=0,column=8,sticky='nswe')
        #self.ac_bt9.grid(row=0,column=9,sticky='nswe')

        self.ac_bt0.config(command=self.Client_PowerOn)
        self.ac_bt1.config(command=self.Client_PowerOff)
        self.ac_bt9.config(command=self.Connect_to_Broker)
        

    

#____________________________________________GUI START_____________________________________________

dashbooard = Controller_Dashboard()
dashbooard.root.mainloop()


