from executable_class import *
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import time
import os
from os import path
import pickle
import time
import pandas as pd
import sys 
from io import StringIO
import json


class TTP_Client(PubSub_Base_Executable): ##CHANGE:: change class name
    
    ##Here you put the class specific variables
    ##...
    ##_________________________________________

    def __init__(self,
                 myID,
                 broker_ip,
                 broker_port,
                 introduction_topic,
                 controller_executable_topic,
                 controller_echo_topic, 
                 start_loop): 
                ##CHANGE:: --> , <<Extended Parameters>> ...):
        
        
        ## Here you initialize the class specific variables
        self.sessions = [] # [owner_id, partner_id, topic]
        self.topic_size = 32

        ##_________________________________________________

        ##IMPORTANT:: This line of code is needed to append the name of newly defined class specific executables::
        self.executables.append('enroll_device')
        self.executables.append('establish_private_topic')
       
        ## ____________________________________________________________________________________________

        #IMPORTANT:: DON'T CHANGE:: Let the base class initializer be at the buttom. This is for the case if client start loop is set to start rightaway.
        PubSub_Base_Executable.__init__(self,
                                        myID,
                                        broker_ip,
                                        broker_port,
                                        introduction_topic,
                                        controller_executable_topic,
                                        controller_echo_topic,
                                        start_loop) ## DON'T CHANGE
        
        self.client_to_TTP_topic = "C2TTP"
        self.TTP_to_client_topic = "TTP2C"
        self.client.subscribe(self.client_to_TTP_topic)
        ##____________________________________________________________________________________________________________________________________________________

    def execute_on_msg (self,client,userdata, msg):
        PubSub_Base_Executable.execute_on_msg(self,client,userdata,msg)

        try:

            header_body = str(msg.payload.decode()).split('::')
            header_parts = header_body[0].split('|')
            
            ##IMPORTANT:: Here you extend the message parser to check for the class specific executables
            ## CHANGE:: --> if msg_parts[0] == <<executable function name>>:
                ##Here you execute accordingly, or simply just invoke the executable: example: self.<<executable name>>(parameterst)
            if header_parts[2] == 'enroll_device':
                id = header_body[1].split('-id ')[1].split(' -csize ')[0]
                csize = int(header_body[1].split('-csize ')[1].split(' -nxor ')[0])
                nxor = int(header_body[1].split('-nxor ')[1].split(' -crp ')[0])
                crp = header_body[1].split(' -crp ')[1].split(';')[0]
                self.enroll_device(id,crp,csize,nxor)

            elif header_parts[2] == 'establish_private_topic':
                id1 = header_body[1].split('-id1 ')[1].split(' -id2 ')[0]                
                id2 = header_body[1].split(' -id2 ')[1].split(' -l ')[0]
                self.topic_size = int(header_body[1].split(' -l ')[1].split(' -rl ')[0])
                replen          = int(header_body[1].split(' -rl ')[1].split(';')[0])
                self.establish_private_topic(id1,id2,replen)
            ##__________________________________________________________________________________________________________________
            ##________________________________________________________________________________
        except:
            print("Error occured or message was not right!")
            
    ##Here you define the new class specific executables:
    def enroll_device(self, id, crp_str,csize,nxor):
        print("Enrolling " + str(id))
        crp_str_parts = crp_str.split('&')
        meta_shape = crp_str_parts[0].split(' ')
        challenge_str = crp_str_parts[1]
        resp_str = crp_str_parts[2]
        
        challenge_set = np.fromstring(challenge_str,dtype=int,sep=' ')
        challenge_set = challenge_set.reshape(int(meta_shape[1]),int(meta_shape[2]))
        
        response_set = np.fromstring(resp_str,dtype=int,sep=' ')
        print(challenge_set.shape)
        print(response_set.shape)
        acc = self.train_model(set_size=challenge_set.shape[0],
                         challenge_size=challenge_set.shape[1]-1,
                         xor_size=nxor,
                         challenge_set=challenge_set,
                         responses=response_set,
                         client_id=id)
        
        client_dir =  "CLIENT_" + id
        if(path.exists(client_dir) != True):
            os.mkdir(client_dir)

        client_info = {
            "id": id,
            "csize" : csize,
            "nxor" : nxor,
            "model_acc": acc
        }

        with open(client_dir + "/client_info.json", 'w') as output:
            json.dump(client_info,output)

        self.echo_msg("Client " + id + " has been enrolled with model accuracy = " + str(acc))


    def establish_private_topic(self, id1, id2,replen):
        print("Establishing private topic for wispering between " + str(id1) +" and " + str(id2))
        
        client1_info = self.load_client(id1)
        client2_info = self.load_client(id2)

        topic_draft = np.random.randint(0,2,self.topic_size,dtype=int) 
        topic_str = ""
        for i in topic_draft:
            topic_str += str(int(i))
        print(topic_str)

        id1_CSet = self.match_making(topic_draft=topic_draft,id=id1,rl=replen,cs = client1_info['csize'])
        id2_CSet = self.match_making(topic_draft=topic_draft,id=id2,rl=replen,cs = client2_info['csize'])
        
        cset1_msg = json.dumps(id1_CSet)
        cset2_msg = json.dumps(id2_CSet)

        self.publish(self.TTP_to_client_topic,"register_private_topic",' -id ' + str(id1) + ' -c ' + str(id2) + ' -rl ' + str(replen) + ' -cset ' + cset1_msg)
        self.publish(self.TTP_to_client_topic,"subscribe_to_private_topic",' -id ' + str(id2) +  ' -rl ' + str(replen) + ' -cset ' + cset2_msg)
        
        #self.publish(self.TTP_to_client_topic,"subscribe_to_private_topic",' -id ' + str(id2) + ' -topic ' + wisper_topic)
        self.sessions.append([id1,id2,topic_str])
    ##___________________________________________________

    def load_client(self,id):
        client_dir =  "CLIENT_" + id
        if(path.exists(client_dir) != True):
            print("ERROR: Client directory not found!")

        with open(client_dir + "/client_info.json", 'r') as output:
            client_info = json.load(output)
        return client_info
    
    def generate_challenge(self, numCRPs,challenge_size):
        challenges = np.random.randint(0, 2, [challenge_size, numCRPs])      
        return challenges
    
    def calc_features(self, challenges,challenge_size):
        # calculate feature vector of linear model
        temp = [np.prod(1 - 2 * challenges[i:, :], 0) for i in range(challenge_size)]
        features = np.concatenate((temp, np.ones((1, challenges.shape[1]))))
        return features

    def infer_with_model(self,id,challenge_size,set_size):
        challenges = self.generate_challenge(set_size,challenge_size)
        feature_set = self.calc_features(challenges,challenge_size)
        feature_set    = np.transpose(feature_set,(1,0))
        feature_tensor = torch.tensor(feature_set,dtype=torch.float32)
        model = self.load_nn_model(id)  
        responses = torch.floor(model(feature_tensor) + 0.5)
        challenge_transposed = np.transpose(challenges,(1,0))
        # print(challenge_transposed.shape)
        return [challenge_transposed.tolist(), responses.tolist()]
    
    def match_making(self, topic_draft, id,cs,rl):
        
        challenge_size = cs
        repetition_length = rl
        batch_size = cs * rl * 5
        challenge_pack = []
        [challenges, responses] = self.infer_with_model(id,challenge_size,batch_size)

        batch_empty = False
        taken_elements = []
        for topic_index in topic_draft:
            for i in range(repetition_length):
                for j in range(len(challenges)):
                    try:
                        if(int(topic_index) == int(responses[j][0])):
                            challenge_pack.append(challenges.pop(j))
                            responses.pop(j)
                            taken_elements.append(j)
                            break
                    except:
                        print("j is: " + str(j))
                        print("length of batch: " + str(len(responses)))
                        # break
        
        return challenge_pack

    def generate_wisper_topic(self,id1,id2):
        
        return str(id1) + str(id2) # PLACEHOLDER!!!!
    
    ##Here you define the rest of the class logic:
    
    def load_nn_model(self,id):
        
        prob_model_instance_dir =  "CLIENT_" + id
        if(path.exists(prob_model_instance_dir) != True):
            os.mkdir(prob_model_instance_dir)
        
        with open(prob_model_instance_dir + "/nn_prob_model.pkl", 'rb') as model_file:
            nn_model = pickle.load(model_file)
            
        return nn_model


    def weights_init(self, m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform(m.weight.data)
            
    def train_model(self,set_size,challenge_size,xor_size,challenge_set,responses, client_id):

        batch_size = 200
        validation_set_size = int(set_size * 0.1)
        test_set_size = int(set_size * 0.2)

        max_iter = 3
        MaxNsteps = 200

        learning_rate = 0.01
        treshold_loss = 0.01
        accuracy_threshold = 0.98

        training_set_size = int(set_size * 0.7)
        # =============================================================================
        # PREPARING THE TRAINING AND TEST SETS:
        # =============================================================================
        x_train = np.array(challenge_set[0:training_set_size])
        x_train = torch.tensor(x_train,dtype=torch.float32)
        # x_train = torch.reshape(x_train,(1,x_train.shape[0],x_train.shape[1]))
        
        y_train = np.array(responses[0:training_set_size])
        y_train = torch.tensor(y_train,dtype=torch.float32)
        y_train = np.reshape(y_train,(y_train.shape[0],))
        
        x_val = np.array(challenge_set[training_set_size : training_set_size + validation_set_size ])

        x_val = torch.tensor(x_val,dtype=torch.float32)
        
        y_val = np.array(responses[training_set_size : training_set_size + validation_set_size ])
        y_val = torch.tensor(y_val,dtype=torch.float32)
        
        
        x_test = np.array(challenge_set[training_set_size + validation_set_size : training_set_size + validation_set_size + test_set_size ])
        x_test = torch.tensor(x_test,dtype=torch.float32)
        
        y_test = np.array(responses[training_set_size + validation_set_size : training_set_size + validation_set_size + test_set_size ])
        y_test = torch.tensor(y_test,dtype=torch.float32)
        y_test = np.reshape(y_test,(y_test.shape[0],))
    
        # =============================================================================
        # BUILDING THE NEURAL NETWORK
        # =============================================================================
        layers = [torch.nn.Linear(challenge_size + 1 , pow(2,(xor_size-1)),bias = True),
                    torch.nn.Tanh(),
                    torch.nn.Linear(pow(2,(xor_size-1)),pow(2,(xor_size)),bias = True),
                    torch.nn.Tanh(),
                    torch.nn.Linear(pow(2,(xor_size)),pow(2,(xor_size-1)),bias = True),
                    torch.nn.Tanh(),
                    torch.nn.Linear(pow(2,(xor_size-1)),1,bias = True),
                    torch.nn.Sigmoid()]
    
        new_model = torch.nn.Sequential(*layers)
        nn_model = new_model

       

        #prob_model_parameters = nn_model.parameters()
        # prob_model_size = 0
        # for param in nn_model.parameters(): #Calculating the size of the model in terms of number of weight values multiplied by 4 (as float32)
        #     if(len(param.shape) > 1):
        #         prob_model_size += (param.shape[0] * param.shape[1] * 4)
        
        losses = np.array([0],dtype=float)
        val_accs = np.array([0],dtype=float)
        loss_func = torch.nn.BCELoss()
        optimizer = torch.optim.Adam(nn_model.parameters(),lr=learning_rate)
        attempt = 0
        # =============================================================================
        # TRAINING THE MODEL:
        # =============================================================================
        while(attempt < max_iter):

            
            nn_model.apply(self.weights_init)

            
            loss = 100
            epoch = 0
            train_begin = time.time()
            print("Training Begins...")
            # for epoch in range(Nsteps):

            while (loss > treshold_loss):
                epoch_complete = False
                batch_start = 0
                while(epoch_complete == False):
                    
                    batch_step = batch_size
                    
                    if(batch_start + batch_size >= training_set_size):
                        epoch_complete = True
                        batch_step = training_set_size - batch_start
                    else:
                        batch_start += batch_size
                    # print(batch_start)    
                    x_train_slice = x_train[batch_start:batch_start+batch_step]
                    y_train_slice = y_train[batch_start:batch_start+batch_step]
                    output = nn_model(x_train_slice)

                    #print("Y_train shape is: " + str(y_train_slice.shape))
                    #print("output shape is: " + str(output.shape))
                    
                    output = output.flatten()
                    loss = loss_func(output,y_train_slice)
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    
        
                if(epoch%2 == 0):
                    step = int(epoch/2)
                    
                    val_outputs = nn_model(x_val)
                    val_outputs = torch.floor(val_outputs + 0.5)
                    val_acc = 0
                    for nt in range(validation_set_size):
                        if(val_outputs[nt] == y_val[nt]):
                            val_acc += 1    
                    val_acc = val_acc / validation_set_size    
                    
                    val_accs[step] = val_acc
                    
                    
                    losses[step] = loss.item()
                    
                    
                    print("TL is = %r , Step = %d => loss = %.3f & validation acc = %.3f" % (False, epoch, loss, val_acc))
                    
                epoch += 1
                    
                if (epoch >= MaxNsteps):
                    print("Reached maximum epoch at %d. Model did not reach loss value %f"%(MaxNsteps,treshold_loss))
                    break
                else:
                    if(epoch%2 == 0):
                        val_accs = np.append(val_accs,[0])
                        losses = np.append(losses,[0])
                    # if(loss > treshold_loss):
                    #     losses = np.append(losses,[0])
        
            val_accs = val_accs[0:len(val_accs)-1]
            losses = losses[0:len(losses) -1]
            train_end = time.time()
            tot = int(train_end - train_begin)
            print("Time of training in seconds: %d" %(tot))
            
            # model_parameters_trained_list = list(nn_model.parameters())
            # for  parami in range(len(model_parameters_trained_list)):
            #     model_parameters_trained_list[parami] = model_parameters_trained_list[parami].data.numpy()
            
            
            # losses = losses[0:epoch]
            # =============================================================================
            # COMPUTING THE TEST ACCURACY:
            # =============================================================================
            # num_tests = int((1-training_set_proportion) * set_size)
            num_tests = test_set_size
            # nn_model = nn_model.to('cpu')
            test_outputs = nn_model(x_test)
            test_outputs = torch.floor(test_outputs + 0.5)
            acc = 0
            for nt in range(num_tests):
                if(test_outputs[nt] == y_test[nt]):
                    acc += 1    
            acc = acc / num_tests    
            print("Test accuarcy is: %.3f in %d tests"%(acc, num_tests))
            
            # =============================================================================
            # MEASURING TEST ACCURACY WHETHER IT FITS WITH THE EXPECTATIONS OR NOT
            # =============================================================================
            if(acc >= accuracy_threshold):
                print("Achieved accuracy is good. Saving the model data.")
                break
            else:
                if(attempt >= max_iter):               
                    print("Maximum case iteration reached. Saving the latest model.")
                else:
                    attempt +=1
                    print("Achieved accuracy is not good. Saving the latest model.")

        # =============================================================================
        # SAVING MODEL DATA
        # =============================================================================
        
        prob_model_instance_dir =  "CLIENT_" + client_id
        
        if(path.exists(prob_model_instance_dir) != True):
            os.mkdir(prob_model_instance_dir)
        
        with open(prob_model_instance_dir + "/nn_prob_model.pkl", 'wb') as output:
            pickle.dump(nn_model, output, pickle.HIGHEST_PROTOCOL)

        prob_model_instance_dir = prob_model_instance_dir + "/dataset_" + str(set_size)
        if(path.exists(prob_model_instance_dir) != True):
            os.makedirs(prob_model_instance_dir)
            
        prob_model_instance_dir = prob_model_instance_dir + "/training_Set_size" + str(training_set_size)
        if(path.exists(prob_model_instance_dir) != True):
            os.makedirs(prob_model_instance_dir)
            
        #Saving the information :
        pd.DataFrame(losses).to_csv(prob_model_instance_dir + "/losses.csv")
        pd.DataFrame(val_accs).to_csv(prob_model_instance_dir + "/val_accs.csv")
        
        stats = "Time of Training in seconds: " + str(tot) + "\n" +\
                "Train CRP size: " + str(training_set_size) + "\n" +\
                "Test CRP size: " + str(test_set_size) + "\n" +\
                "Test Accuracy: " + str(acc) + "\n" +\
                "LR: " + str(learning_rate) + "\n" +\
                "Number of attempts of re-training: " + str(attempt) +"\n" +\
                "Transfer Learning On: " + str(False)
                
        with open(prob_model_instance_dir + "/stats.txt",'w') as stat_file:
            stat_file.write(stats)

        return acc            
    ##___________________________________________________


##Sample Program logic:

userID = input("Enter UserID: ")
print("User with ID=" + userID +" is created.")
exec_program = TTP_Client                             (myID = userID,
                                                       broker_ip = 'localhost',
                                                       broker_port = 1883,
                                                       introduction_topic='client_introduction',
                                                       controller_executable_topic='controller_executable',
                                                       controller_echo_topic="echo",
                                                       start_loop=False)

while(True):
    output = exec_program.base_loop() # Restoration Cap is 10
    if(output == -1):
        print("User with ID=" + userID +" is re-created.")
        exec_program = TTP_Client                             (myID = userID,
                                                       broker_ip = 'localhost',
                                                       broker_port = 1883,
                                                       introduction_topic='client_introduction',
                                                       controller_executable_topic='controller_executable',
                                                       controller_echo_topic="echo",
                                                       start_loop=False)

        exec_program.echo_msg("Client " + exec_program.id + " is re-initialized...")
    

##____________________