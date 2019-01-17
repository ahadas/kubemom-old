from kubernetes import client, config
from prometheus_client.parser import text_string_to_metric_families
import requests
import yaml

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

def get_vmi(owner_references):
    for owner_reference in owner_references:
        if owner_reference.controller:
            return owner_reference
    return None

print ('querying..')
v1 = client.CoreV1Api()
print("Listing pods and their respective VMIs:")
ret = v1.list_namespaced_pod('default', watch=False, label_selector='kubevirt.io=virt-launcher', field_selector='spec.nodeName=node02')
for i in ret.items:
    print("%s\t-> %s" % (i.metadata.name, get_vmi(i.metadata.owner_references).uid))

print("Find the virt-handler endpoint:")
ret = v1.list_namespaced_endpoints('kubevirt', label_selector='prometheus.kubevirt.io=')
for i in ret.items:
    for subset in i.subsets:
        if subset.ports[0].name == 'metrics':
            port = subset.ports[0].port
            print("%s", port)
            for address in subset.addresses:
                if address.node_name != 'node02':
                    continue
                if address.target_ref.name.startswith('virt-handler'):
                    ip = address.ip
                    print("%s", ip)

print ('connecting...')
url = "https://{0}:{1}/metrics".format(ip, port)
print (url)
metrics = requests.get(url, verify=False).text
print (metrics)

print ('connected')
for family in text_string_to_metric_families(metrics):
  for sample in family.samples:
    print("Name: {0} Labels: {1} Value: {2}".format(*sample))
