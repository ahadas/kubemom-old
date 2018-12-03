# kubemom
This is a playground for making a python application that, on the one hand, receives metrics via prometheus and, on the other hand, publishes information to a kubernetes cluster.  
It is intended for introducing MOM (Memory Overcommitment Manager) application for KubeVirt.  

Build:  
`docker build -t mom .`

Run:  
`docker run --network="host" mom`
