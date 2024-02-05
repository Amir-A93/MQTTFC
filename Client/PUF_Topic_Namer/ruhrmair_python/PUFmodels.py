from numpy import random, concatenate, array, prod, ones, sign, dot, empty

class linArbPUF:
    ''' linArbPUF provides methods to simulate the behaviour of a standard 
        Arbiter PUF (linear model)
        
        attributes:
        num_bits -- bit-length of the PUF
        delays -- runtime difference between the straight connections 
            (first half) and crossed connection (second half) in every switch
        parameter -- parameter vector of the linear model (D. Lim)
        
        methods:
    '''
        
    
    def __init__(self, num_bits, mean=0, stdev=1):
        self.num_bits = num_bits
        # dice runtime difference between upper and lower pathes (for crossed/uncrossed state)
        self.delays = random.normal(mean, stdev, 2 * num_bits)
        # construct parameter vector of linear model        
        self.parameter = concatenate((self.delays[:num_bits] - self.delays[num_bits:], array([0])))
        self.parameter[1:] += self.delays[:num_bits] + self.delays[num_bits:]
    def generate_challenge(self, numCRPs):
        challenges = random.randint(0, 2, [self.num_bits, numCRPs])      
        return challenges
    
    def calc_features(self, challenges):
        # calculate feature vector of linear model
        temp = [prod(1 - 2 * challenges[i:, :], 0) for i in range(self.num_bits)]
        features = concatenate((temp, ones((1, challenges.shape[1]))))
        return features
    
    def response(self, features):
        return dot(self.parameter, features)
    
    def bin_response(self, features):
        return sign(self.response(features))

class XORArbPUF:
    def __init__(self, num_bits, numXOR, type, mean=0, stdev=1):
        self.num_bits = num_bits
        self.numXOR = numXOR
        self.type = type
        # create indivudual ArbiterPUFs
        self.indiv_arbiter = []
        for arb in range(numXOR):
            self.indiv_arbiter.append(linArbPUF(num_bits, mean, stdev)) 
            
    '''
    def getParam(self):
        delays=empty([self.numXOR, 2*self.numBits])
        parameter=empty([self.numXOR, self.numBits+1])
        for i in range(self.numXOR):
            delays[i,:]=self.indivArbiter[i].delays
            parameter[i,:]=self.indivArbiter[i].parameter
        return (delays, parameter)

    def setParam(self,delays,parameter):
        for i in range(self.numXOR):
            self.indivArbiter[i].delays=delays[i,:]
            self.indivArbiter[i].parameter=parameter[i,:]
    '''
        
    def generate_challenge(self, numCRPs):
        challenges = empty([self.numXOR, self.num_bits, numCRPs])
        if self.type == 'equal':
            tempchallenge = random.randint(0, 2, [self.num_bits, numCRPs])
            for puf in range(self.numXOR):
                challenges[puf, :, :] = tempchallenge
        
        elif self.type == 'lightweight':
            tempchallenge = random.randint(0, 2, [self.num_bits, numCRPs])
            for puf in range(self.numXOR):
                rchallenge = 1 - 2 * concatenate((tempchallenge[puf:, :], tempchallenge[:puf, :]))
                challenges[puf, :, :] = 0.5 * (1 - concatenate((rchallenge[::2, :] * rchallenge[1::2, :],
                                                            rchallenge[self.num_bits / 2, :].reshape(-1, numCRPs),
                                                            rchallenge[1:-1:2, :]*rchallenge[2::2, :])))
                
        elif self.type == 'random':
             for puf in range(self.numXOR):
                challenges[puf, :, :] = random.randint(0, 2, [self.num_bits, numCRPs])
        else:
            print ('no mapping of for type ' + self.type + 'exist for XORPUFs')        
        return challenges
                
    def calc_features(self, challenges):
        features = empty([self.numXOR, self.num_bits + 1, challenges.shape[-1]])
        for puf in range(self.numXOR):
            features[puf, :, :] = concatenate(([prod(1 - 2 * challenges[puf, i:, :], 0) for i in range(self.num_bits)], ones((1, challenges.shape[-1]))))
        return features
    
    '''
    def calcKernel(self,features1,features2):
        #features1 known, features2 to be classified
        size1=features1.shape[-1]
        size2=features2.shape[-1]
        kernel=ones([size2,size1])
        for i in range(size2):
            for j in range(size1):
                for k in range(self.numXOR):
                    kernel[i,j]*=dot(swapaxes(features2,1,2)[k,i,:],features1[k,:,j])
        return kernel
    '''
    
    def indiv_responses(self,features):
        indiv_response = empty([self.numXOR, features.shape[-1]])
        for puf in range(self.numXOR):
            indiv_response[puf, :] = self.indiv_arbiter[puf].response(features[puf, :, :].squeeze())
        return sign(indiv_response)
    
    def response(self, features):
        indiv_response = empty([self.numXOR, features.shape[-1]])
        for puf in range(self.numXOR):
            indiv_response[puf, :] = self.indiv_arbiter[puf].response(features[puf, :, :].squeeze())
        response = prod(indiv_response, 0)
        return response
    
    def bin_response(self, features):
        return sign(self.response(features))
