FROM python:3
ADD script.py /
ADD .kubeconfig /root/.kube/config
RUN pip install kubernetes
CMD [ "python", "./script.py" ]
