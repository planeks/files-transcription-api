# Files Transcription Api

## About the project

Project provides audio files transcription with different file formats and languages. Full list of 
supported languages can be found [here](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html). 
Audio transcription is sent directly to an email box of given email address. Considering the fact that it's based on 
AWS S3 and AWS Transcribe it does not require many resources.

## Running the project on the local machine

Copy the `dev.env` file to the `.env` file in the same directory.

```shell
$ cp dev.env .env
```

Open the `.env` file in your editor and specify the settings:

```shell
PYTHONENCODING=utf8
COMPOSE_IMAGES_PREFIX=files-transcriber
DEBUG=1
CONFIGURATION=dev
DJANGO_LOG_LEVEL=INFO
SECRET_KEY="<secret_key>"
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=db
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpassword
REDIS_URL=redis://redis:6379/0
SITE_URL=http://127.0.0.1:8000
EMAIL_HOST=mailhog
EMAIL_PORT=1025

AWS_S3_ACCESS_KEY_ID=<AWS_S3_ACCESS_KEY_ID>
AWS_S3_SECRET_ACCESS_KEY=<AWS_S3_SECRET_ACCESS_KEY>
AWS_STORAGE_BUCKET_NAME=<AWS_STORAGE_BUCKET_NAME>
AWS_S3_REGION_NAME=<AWS_S3_REGION_NAME>
AWS_PRESIGNED_EXPIRY=10
```

Use the following command to build the containers:

```shell
$ docker-compose -f docker-compose.dev.yml build
```

Use the next command to run the project in detached mode:

```shell
$ docker-compose -f docker-compose.dev.yml up -d
```

Use next command to run `bash` inside the container to create Django superuser:

```shell
$ docker-compose -f docker-compose.dev.yml exec django bash
```

## Example of usage

Transcription can be performed using web UI on http://localhost:8000 or using given REST API. 
Steps for transcription using REST API are following:

1. Start file upload
2. Perform file upload directly to S3
3. Submit file upload to the server
4. Start file transcription

### Start file upload

Retrieve presigned post data from AWS to perform direct upload.

`POST /start-file-upload/`

#### Request

```json
{
  "file_name": "example.wav",
  "file_type": "audio/x-wav",
  "user_email": "user@example.com"
}
```

#### Response

```json
{
  "id": 1,
  "url": "https://files-transcription-bucket.s3.amazonaws.com/",
  "fields": {
    "acl": "private",
    "Content-Type": "audio/x-wav",
    "key": "audio_files/24f191d63dd840a8afbd6598a5efb8cf.wav",
    "x-amz-algorithm": "AWS4-HMAC-SHA256",
    "x-amz-credential": "AKJA323131H23JKAH31/20230111/eu-north-1/s3/aws4_request",
    "x-amz-date": "20230111T083476Z",
    "policy": "eyJleHBpcmF0aW9uIjogIjIwMjMtMDEtMTFUMDg6mRpd...",
    "x-amz-signature": "daf2g3aahajaf08jhahaha..."
  }
}
```

Here id is identifier of audio file in system which will be used later.

### Perform file upload directly to S3

Upload the file directly to S3 using url from presigned data as POST endpoint and given payload 
from the response and file as request body. Example can be found here:

`/src/transcriber/templates/index.html (line: 152)`

### Submit file upload to the server

After the successful response from S3 audio file upload should be submitted to the server before 
the actual transcription.

`POST /finish-file-upload/`

#### Request

```json
{
  "id": 1,
  "status": "uploaded"
}
```

#### Response

```json
{
  "id": 1
}
```

### Start file transcription

Audio file can be transcribed after the upload confirmation. Transcription will take some time and transcription 
results will be sent to the provided user email.

`POST /start-file-transcription/`

#### Request

```json
{
  "id": 1
}
```

#### Response

```json
{
  "id": 1
}
```
