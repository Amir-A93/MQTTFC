from executable_class import *

userID = input("Enter UserID: ")
print("User with ID=" + userID +" is created.")


class Counter_Client(PubSub_Base_Executable):
    
    count_cap = 0
    
    def __init__(self,myID,broker_ip, broker_port, introduction_topic, controller_executable_topic,controller_echo_topic,count_cap, start_loop = True):
        
        self.count_cap = count_cap
        self.executables.append("count")

        PubSub_Base_Executable.__init__(self,myID,broker_ip, broker_port, introduction_topic, controller_executable_topic,controller_echo_topic,start_loop)
        
    def execute_on_msg (self,client,userdata, msg):
        PubSub_Base_Executable.execute_on_msg(self,client,userdata,msg)
        msg_parts = str(msg.payload.decode()).split()
        
        if msg_parts[0] == 'count':
            self.count()

    def count(self):
         for i in range(self.count_cap):
              self.publish(self.controller_echo_topic,"count",str(i))




exec_program =  Counter_Client( myID = userID,
                                broker_ip = 'localhost',
                                broker_port = 1883,
                                introduction_topic='client_introduction',
                                controller_executable_topic='controller_executable',
                                controller_echo_topic="echo",
                                count_cap=100,
                                start_loop=False)

exec_program.base_loop();

