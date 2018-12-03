FROM python:3
ADD script.py /
ADD .kubeconfig /root/.kube/config
RUN pip install kubernetes
RUN pip install prometheus_client requests
CMD [ "python", "./script.py" ]
