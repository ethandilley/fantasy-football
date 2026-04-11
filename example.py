import json
import gzip
import io
from minio import Minio

data = {
    "user": "alice",
    "score": 42,
    "tags": ["a", "b", "c"]
}

# --- 1. Convert dict -> JSON bytes ---
json_bytes = json.dumps(data).encode("utf-8")

# --- 2. Compress with gzip (in-memory) ---
buf = io.BytesIO()
with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
    gz.write(json_bytes)

buf.seek(0)
compressed_data = buf.read()

# --- 3. MinIO client ---
client = Minio(
    "play.min.io:9000",   # change to your endpoint
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    secure=False
)

bucket = "my-bucket"
object_name = "data/my_dict.json.gz"

# Ensure bucket exists
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

# --- 4. Upload ---
client.put_object(
    bucket_name=bucket,
    object_name=object_name,
    data=io.BytesIO(compressed_data),
    length=len(compressed_data),
    content_type="application/gzip"
)

print("Uploaded!")
