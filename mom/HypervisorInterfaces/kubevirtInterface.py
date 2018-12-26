import logging
from kubernetes import client, config
from mom.HypervisorInterfaces.HypervisorInterface import *

class libvirtInterface(HypervisorInterface):

    def __init__(self, configs):
        config.load_kube_config()

    def getVmList(self):
        v1 = client.CoreV1Api()
        print("Listing pods with their IPs:")
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

