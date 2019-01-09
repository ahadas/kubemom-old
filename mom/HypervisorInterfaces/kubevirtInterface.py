import logging
from kubernetes import client, config
from mom.HypervisorInterfaces.HypervisorInterface import *

class kubevirtInterface(HypervisorInterface):

    def __init__(self, configs):
        config.load_kube_config()
        self._logger = logging.getLogger('mom.kubevirtInterface')
        self.v1 = client.CoreV1Api()

    def get_vmi(self, owner_references):
        for owner_reference in owner_references:
            if owner_reference.controller:
                return owner_reference
        return None

    def getVmList(self):
        print("Listing pods with their IPs:")
        virt_launcher_label = 'kubevirt.io=virt-launcher'
        node = 'spec.nodeName=node02'
        ret = self.v1.list_namespaced_pod('default',
                                          watch=False,
                                          label_selector=virt_launcher_label,
                                          field_selector=node)
        vmIds = []
        for pod in ret.items:
            vmi = self.get_vmi(pod.metadata.owner_references)
            vmIds.append(vmi.uid)
            #print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        self._logger.info('VM List: %s', vmIds)
        return vmIds

def instance(config):
    return kubevirtInterface(config)
