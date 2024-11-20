# tehfiles
##### File storing and simple analytics

Simple API with ability to store uploaded files in storage and retrieve simple analytics.

For local storage [MinIO](https://min.io/) is used. The good thing that you can use 
[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) with Minio,
so you can switch to AWS S3 if needed.
-------
## Usage

First - we can setup `.env` file, but in this case let's just use env vars in `docker-compose.yaml`

#### MinIO setup
Since we are using MinIO as our storage - the first thing is to setup a new bucket for our app.
Run:
```commandline
 docker compose up minio 
```
Now we can go to [MinIO UI](localhost:9001):

```
http://localhost:9001/login
```

To login please use creds from `docker-compose.yaml`:
```
MINIO_ROOT_USER: s3_local_access_key
MINIO_ROOT_PASSWORD: s3_local_secret_key
```

And go to [buckets/add-bucket](http://localhost:9001/buckets/add-bucket) to add new bucket with name: `default-bucket`.
Which is already in app settings. 

#### Run 

After setting up new bucket in MinIO we can start our API along with other services:

```commandline
 docker compose up
```
And after services have started - try our [API](http://localhost:9002/docs):
```
http://localhost:9002/docs
```