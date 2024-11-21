# tehfiles
##### File storing and simple analytics

Simple API with ability to store uploaded files to storage and get simple analytics.

For local storage [MinIO](https://min.io/) is used. The good thing that you can use 
[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) with Minio,
so you can switch to AWS S3 if needed.

-------
## Usage

**First - we need setup** `.env` **file**, so please create `.env file with (leave postgres-related keys as is):

```
s3_local_access_key="s3_local_access_key"
s3_local_secret_key="s3_local_secret_key"

postgres_user="postgres"
postgres_password="postgres"
postgres_db="db"
```

And then run:
```commandline
export $(xargs <.env)
```

#### MinIO setup
Since we are using MinIO as our storage - the first thing is to setup a new bucket for our app.
Run:
```commandline
 docker compose up 
```
Now we can go to [MinIO UI](localhost:9001):

```
http://localhost:9001/login
```

To login please use creds from `.env`:
```
login -> s3_local_access_key 
pawd -> s3_local_secret_key
```

And go to [buckets/add-bucket](http://localhost:9001/buckets/add-bucket) to add new bucket with name: `default-bucket`.
Which is already in app settings. 

#### API 

After setting up new bucket in MinIO we can start using our API:
[API](http://localhost:9002/docs):
```
http://localhost:9002/docs
```

#### Limitations

The max upload size for files is set to 50 mb in settings. 
However, it can be changed via env var `max_upload_size`, the amount is in mb.

------

