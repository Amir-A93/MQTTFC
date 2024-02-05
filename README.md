MQTT Fleet Control is an infrastructure to supervise network components (real and virtual) through MQTT.
A user interface as well as a programming interface is provided to assist the supervision.
A templace user Executable Class is provided as well that can be inheritted.
Current Client Class chain is: MQTTFC base class -> MQTTFC Premetheus --> MQTTFC TTC.
NOTE: PUF topic namer was provided for private topic naming and lightweight message encryption. Ignore this class if you don't want to use PUF.
NOTE: please do not augment this repo with application specific implementations.
