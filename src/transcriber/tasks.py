import datetime

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from core.utils import send_html_email
from transcriber.exceptions import TranscriptionFailureException
from transcriber.models import AudioFile
from transcriber.services import AudioFileS3TranscriptionService


@shared_task
def transcribe_audio_file(file_id):
    """Task which performs audio file transcription and sends email in case of successful transcription."""

    file = AudioFile.objects.get(pk=file_id)
    if file.status == AudioFile.FAILED:
        return

    file.status = AudioFile.IN_PROGRESS
    file.transcription_start = datetime.datetime.now(tz=timezone.utc)
    file.save()

    service = AudioFileS3TranscriptionService()
    try:
        transcription = service.transcribe_file(file)
        file.status = AudioFile.TRANSCRIBED
        file.transcription = transcription
        file.transcription_end = datetime.datetime.now(tz=timezone.utc)

        send_html_email(
            'File Transcription Result',
            [file.user_email],
            'email/transcription_success.html',
            'email/transcription_success.txt',
            {'file': file}
        )
    except TranscriptionFailureException:
        file.status = AudioFile.FAILED

        send_html_email(
            'File Transcription Failed',
            [file.user_email],
            'email/transcription_failure.html',
            'email/transcription_failure.txt',
            {'SITE_URL': settings.SITE_URL}
        )
    file.save()
