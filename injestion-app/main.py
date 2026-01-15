from minio import Minio
import os


# https://englishjobsearch.ch/in/zurich/data_engineer?page=2 
# Make it ....

# Initialize client with service account credentials
client = Minio(
    os.getenv("MINIO_BRONZE_ENDPOINT"),
    access_key=os.getenv("ACCESS_KEY_BRONZE"),
    secret_key=os.getenv("SECRET_KEY_BRONZE"),
    secure=False  # Set True if using HTTPS
)

found = client.bucket_exists("bucket1")
print(found)

# Upload file
client.fput_object(
    "bucket1",
    "experiment.txt",
    "/app/Upload/experiment.txt"
)


# Download file
client.fget_object(
    "bucket1",
    "experiment.txt",
    "/app/Download/new_file.txt"
)
