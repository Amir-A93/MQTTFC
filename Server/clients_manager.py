import os
class Client:
    name = ""
    id = ""
    directory = ""
    broker = ""
    status = ""
    executables = [""]

    def __init__(self, name, id, type, directory, broker):
        self.name = name
        self.id = id
        self.type = type
        self.directory = directory
        self. broker = broker
        self.status = "OFF"
        self.executables = []

        self.check_status()

    def power_on(self):
        if(self.status == "ON"):
            return 0
        else:
            os_command_output = os.popen("VBoxManage startvm " + self.name + " --type headless").read()
            self.status = "ON"
            return os_command_output
        
    def power_off(self):
        if(self.status == "OFF"):
            return 0
        else:
            os_command_output = os.popen("VBoxManage controlvm " + self.name +  " poweroff").read()
            self.status = "OFF"
            return os_command_output

    def check_status(self):
        os_command_output = os.popen("vboxmanage list runningvms").read()
        if(os_command_output.find(self.name) > 0):
            self.update_status("ON")

    def update_status(self, new_status):
        self.status = new_status
    


def Inspect_Container_Client(client,log_func):
    return 0
def Inspect_Pie_Client(client,log_func):
    return 0
def Inspect_VM_Client(client,log_func):
    return 0


def PowerOn_Container_Client(client,log_func):
    return 0
def PowerOn_Pie_Client(client,log_func):
    return 0
def PowerOn_VM_Client(client,log_func):
    return 0


def PowerOff_Container_Client(client,log_func):
    return 0
def PowerOff_Pie_Client(client,log_func):
    return 0
def PowerOff_VM_Client(client,log_func):
    return 0
