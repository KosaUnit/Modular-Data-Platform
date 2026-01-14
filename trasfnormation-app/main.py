from minio import Minio
import os

# Initialize client with service account credentials
client_bronze = Minio(
    os.getenv("MINIO_BRONZE_ENDPOINT"),
    access_key=os.getenv("ACCESS_KEY_BRONZE"),
    secret_key=os.getenv("SECRET_KEY_BRONZE"),
    secure=False  # Set True if using HTTPS
)

client_gold = Minio(
    os.getenv("MINIO_GOLD_ENDPOINT"),
    access_key=os.getenv("ACCESS_KEY_GOLD"),
    secret_key=os.getenv("SECRET_KEY_GOLD"),
    secure=False  # Set True if using HTTPS
)

bronze_bucket = "bucket1"
gold_bucket = "my-gold-bucket"


try:
    result = client_bronze.bucket_exists(bronze_bucket)
    if not result:
        print(f"❌ Bucket '{bronze_bucket}' not found")
        # Now what? Exit? Continue?
except Exception as e:
    print(f"❌ Connection failed: {e}")
    # Handle connection errors differently?

try:
    result = client_gold.bucket_exists(gold_bucket)
    if not result:
        print(f"❌ Bucket '{gold_bucket}' not found")
        # Now what? Exit? Continue?
except Exception as e:
    print(f"❌ Connection failed: {e}")
    # Handle connection errors differently?


# To do: 
# link to use https://docs.min.io/enterprise/aistor-object-store/developers/sdk/python/api/
# fetch all objects 
# do some simple transofrmation idk add + 1 
# push to the gold bucket




# Upload file
client_bronze.fput_object(
    "bucket1",
    "experiment.txt",
    "/app/Upload/experiment.txt"
)


# Download file
client_bronze.fget_object(
    "bucket1",
    "experiment.txt",
    "/app/Download/new_file.txt"
)
