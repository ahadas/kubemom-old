from kubernetes import client, config
from prometheus_client.parser import text_string_to_metric_families
import requests

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

#v1 = client.CoreV1Api()
#print("Listing pods with their IPs:")
#ret = v1.list_pod_for_all_namespaces(watch=False)
#for i in ret.items:
#    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

print ('connecting...')
metrics = requests.get("http://127.0.0.1:9101/metrics").text

print ('connected')
for family in text_string_to_metric_families(metrics):
  for sample in family.samples:
    print("Name: {0} Labels: {1} Value: {2}".format(*sample))

