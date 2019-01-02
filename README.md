# kubemom
This is a playground for making a python application that, on the one hand, receives metrics via prometheus and, on the other hand, publishes information to a kubernetes cluster.  
It is intended for introducing MOM (Memory Overcommitment Manager) application for KubeVirt. More information can be found [here](Wiki.md).

Build:  
`sudo docker build -t mom .`

Run:  
`sudo docker run --network="host" mom`
