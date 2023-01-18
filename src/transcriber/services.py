import time

import boto3
from botocore.exceptions import ClientError
import pandas as pd
from django.conf import settings
from django.db import transaction

from transcriber.exceptions import TranscriptionFailureException
from transcriber.models import AudioFile, get_audio_file_upload_path
from transcriber.utils import generate_unique_file_name


def get_aws_client(service_name):
    return boto3.client(
        service_name=service_name,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )


def generate_presigned_s3_post(file_path, file_type):
    s3_client = get_aws_client('s3')

    acl = settings.AWS_DEFAULT_ACL
    expires_in = settings.AWS_PRESIGNED_EXPIRY

    presigned_data = s3_client.generate_presigned_post(
        settings.AWS_STORAGE_BUCKET_NAME,
        file_path,
        Fields={'acl': acl, 'Content-Type': file_type},
        Conditions=[{'acl': acl}, {'Content-Type': file_type}],
        ExpiresIn=expires_in,
    )
    return presigned_data


class AudioFileS3UploadService:
    @transaction.atomic
    def start(self, file_name: str, file_type: str, user_email: str):
        """Starts file upload by getting presigned data from S3 for direct upload."""

        audio_file = AudioFile(
            file_name_original=file_name,
            file_name=generate_unique_file_name(file_name),
            file_type=file_type,
            user_email=user_email
        )
        audio_file.save()

        upload_path = get_audio_file_upload_path(audio_file, audio_file.file_name)

        audio_file.file = audio_file.file.field.attr_class(audio_file, audio_file.file.field, upload_path)
        audio_file.save()

        presigned_data = generate_presigned_s3_post(file_path=upload_path, file_type=audio_file.file_type)
        return {'id': audio_file.pk, **presigned_data}

    def finish(self, file, status):
        file.status = status
        file.save()
        return file


class AudioFileS3TranscriptionService:
    def transcribe_file(self, audio_file):
        """Starts transcription job using aws transcribe client an audio file stored in S3."""

        transcribe_client = get_aws_client('transcribe')
        job_name = str(audio_file.transcription_job_id)

        try:
            transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': audio_file.file.url.split('?')[0]},
                IdentifyLanguage=True
            )
        except ClientError:
            raise TranscriptionFailureException('Failed to start transcription job')
        return self._wait_transcription(job_name, transcribe_client)

    def _wait_transcription(self, job_name, transcribe_client):
        """Waits for job transcription result."""

        while True:
            job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = job['TranscriptionJob']['TranscriptionJobStatus']

            if job_status == 'COMPLETED':
                transcription_result_url = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcription = self._retrieve_transcription(transcription_result_url)
                print(f'Transcription job: {job_name} complete.')
                return transcription
            elif job_status == 'FAILED':
                raise TranscriptionFailureException('Transcription failed')

            print(f'Waiting for transcription job: {job_name} to complete.')
            time.sleep(5)

    def _retrieve_transcription(self, result_url):
        """Retrieves transcription result from given result url."""

        retry_n = 10
        while retry_n > 0:
            retry_n -= 1
            try:
                data = pd.read_json(result_url)
                transcript = data['results']['transcripts'][0]['transcript']
                if transcript:
                    transcript = transcript[0].capitalize() + transcript[1:]
                return transcript
            except:
                time.sleep(1)
        raise TranscriptionFailureException('Result retrieval failed')
