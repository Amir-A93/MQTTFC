#Here, the core modules of MQTT Fleet Control is placed
import broker_manager
import clients_manager
import executable_manager
import paho.mqtt.client as mqtt
import os
import threading
import json

class Server_Controller:
    
    
    sub_topics_directory = "metadata/topics_to_subscribe.json"
    pub_topics_directory = "metadata/topics_to_publish.json"

    broker_mtf_directory = "metadata/broker_metadata.json"
    client_mtf_directory = "metadata/client_metadata.json"
    
    
    client = mqtt.Client()
    MQTT_thread_handler = threading.Thread(target=client.loop_forever)
    
    def __init__(self,log_func):

        self.broker_list = self.Load_brokers()
        self.selected_broker = self.broker_list[0]

        self.client_list = self.Load_clients()

        self.sub_topics = self.load_topics_to_subscribe()
        self.pub_topics = self.load_topics_to_publish()
        
        if(log_func != None):
            self.log = log_func
        else:
            self.log = self.Log

    def Subscribe_to_All(self):
        for topic in self.sub_topics:
            self.Subscribe(topic_name=topic)

    def Subscribe(self,topic_name):
        self.client.subscribe(topic=topic_name)
        print("Subscribed to topic " + topic_name)
        self.log ("CONTROLLER:: " + "Subscribed to topic " + topic_name)
    
    def Connect_to_Selected_Broker(self,on_connect_func, on_message_func):
        try:
            if(not self.MQTT_thread_handler.is_alive()):
                self.client.on_connect = on_connect_func
                self.client.on_message = on_message_func
        
                self.log("CONTROLLER:: connecting to " + str(self.selected_broker))
                
                self.client.connect(self.selected_broker[0],self.selected_broker[1],self.selected_broker[2])
                self.MQTT_thread_handler.start()

            else:
                self.log("CONTROLLER:: Dashboard already connected to a broker. Close the dashboard and start again.")
        
        except:
                self.log("CONTROLLER:: Probably no broker is selected yet. Please select from the list.")
            
        
    def Client_PowerOn(self,c_index,callback):
        output = self.client_list[c_index].power_on()
        if(output == 0):
            self.log("Client is already running.")
        else:
            self.log(output)
            self.log("Client " + self.client_list[c_index].name + " is power on.")
            callback()
            
    def Client_PowerOff(self,c_index,callback):
        output = self.client_list[c_index].power_off()
        if(output == 0):
            self.log("Client is already off.")
        else:
            self.log(output)
            self.log("Client " + self.client_list[c_index].name + " is power off.")
            callback()
        
    def Load_brokers(self):
        brkr_mtf = open(self.broker_mtf_directory)
        data = json.load(brkr_mtf)
        broker_list = []
        for item in data:
            broker_list.append([item['ip'],int(item['port']),int(item['timeout'])])
        return broker_list

    def load_topics_to_subscribe(self):
        f = open(self.sub_topics_directory)
        data = json.load(f)
        topic_list = []
        for item in data:
            topic_list.append(item)
        return topic_list
    
    def load_topics_to_publish(self):
        f = open(self.pub_topics_directory)
        data = json.load(f)
        topic_list = []
        for item in data:
            topic_list.append(item)
    
    def Load_clients(self):
        client_mtf = open(self.client_mtf_directory)
        data = json.load(client_mtf)
        c_list = []
        for item in data:
            c_list.append(clients_manager.Client(name=item['name'],
                                                           id=item['id'],
                                                           type=item['type'],
                                                           directory=item['directory'],
                                                           broker=item['broker']))
        return c_list
    
    #"name":"Lubu_FL_1",
    #"id":"Lubu_FL_1",
    #"type":"VM",
    #"directory":"/home/etsamir/Desktop/ETS/projects/MQTT_Fleet_Control/Server/remote_controller/Lubu_FL_1/",
    #"broker":"localhost"},
    

    def Log(self,msg):
        print(msg)

