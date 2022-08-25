from boto3 import client
import settings
import io
import traceback
from botocore.client import Config
import requests

DEFAULT_S3_FOLDER = "medias"
BUCKET = "instagram-post-tracker"


def get_s3_client():
	# Get S3 bucket information from secret key/ID
	return client('s3', aws_access_key_id=settings.env.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.env.AWS_SECRET_ACCESS_KEY, config=Config(signature_version='s3v4'))


def upload_to_s3(url, filename_without_extension):
	s3 = get_s3_client()
	try:
		# Gets the file as an object
		r = requests.get(url, stream=True)
		ext = r.headers['content-type'].split('/')[-1] or ".jpeg"
		filename = f"{filename_without_extension}.{ext}"
		# urllib.request.urlretrieve(url, filename)

		# uploads the file to s3
		s3.upload_fileobj(io.BytesIO(r.content), BUCKET, f"{DEFAULT_S3_FOLDER}/{filename}")
		# print(f'File downloaded from {url} and uploaded to {DEFAULT_S3_FOLDER}/{filename}')
		bucket_location = s3.get_bucket_location(Bucket=BUCKET)
		return "https://{0}.s3-{1}.amazonaws.com/{2}/{3}".format(BUCKET, bucket_location['LocationConstraint'], DEFAULT_S3_FOLDER, filename)
	except Exception as e:
		print(str(e))
		print(traceback.format_exc())
		print(f"File not downloaded or not uploaded from {url}")
		return None


def delete_media_from_s3(media_url: str):
	# Remove media from S3
	media_file = '/'.join(media_url.split('/')[-2:])
	try:
		s3 = get_s3_client()
		s3.delete_object(Bucket=BUCKET, Key=media_file)
		print(f"{media_file} removed from bucket")
	except Exception as e:
		print(str(e))
		print(f"Cannot delete media {media_url}")
