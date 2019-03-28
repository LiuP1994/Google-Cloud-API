A Flask app using for the UK Police API.

The variable crimes holds a JSON-formatted response to our GET request.

we are using it to find out the statistics of crimes per each category of crime in each month.

after we get the count of crimes in each category, show it in the web by specify the date and type of category.

1.Set the region and zone for the new cluster
```
gcloud config set compute/zone europe-west2-b
export PROJECT_ID="$(gcloud config get-value project -q)"
```

2.create a Kubernetes cluster
```
gcloud container clusters create cassandra --num-nodes=3 --machine-type "n1-standard-2"
```

3.A Kubernetes service defines multiple sets of pods, allowing full systems to be deployed with one script.For this we will be using three files. The first will be a Headless service which will allow peer discovery i.e. the Cassandra pods will be able to find each other and form a ring. The second defines the Cassandra service itself, and the third is a Replication Controller which allows us to scale up and down the number of containers we want. Download these via the following commands:
```
wget -O cassandra-peer-service.yml http://tinyurl.com/yyxnephy
wget -O cassandra-service.yml http://tinyurl.com/y65czz8e
wget -O cassandra-replication-controller.yml http://tinyurl.com/y2crfsl8
```

4.now run our three components
```
kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml
```

5.Check that the single container is running correctly
```
kubectl get pods -l name=cassandra
```

6.and if so we can can scale up our number of nodes via our replication-controller:
```
kubectl scale rc cassandra --replicas=3
```

7.run cqlsh inside the container
```
kubectl exec -it <service name> cqlsh
```

8.build our keyspace
```
CREATE KEYSPACE crime WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 2};
```

9.Create the table for our service
```
CREATE TABLE crime.category(name text primary key,count int,month text)
```

10. then create our requirements.txt
```
pip
Flask
cassandra−driver
```

11.the Dockerfile
```
FROM python:3.7-alpine
WORKDIR /myapp
COPY . /myapp
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python", "app.py"]
```

12. build our image
```
docker build -t gcr.io/${PROJECT_ID}/crime:v1 .
```

13.Push it to the Google Repository
```
docker push gcr.io/${PROJECT_ID}/crime:v1
```

14.Run it as a service
```
kubectl run pokemon-app --image=gcr.io/${PROJECT_ID}/pokemon-app:v1 --port 8080
```

15.exposing the deploment to get an external IP
```
kubectl expose deployment pokemon-app --type=LoadBalancer --port 80 --target-port 8080
```

16.get the external IP
```
kubectl get services
```
