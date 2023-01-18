from django.db import models
from django.utils.translation import gettext_lazy as _


def get_audio_file_upload_path(instance, filename):
    return f"audio_files/{instance.file_name}"


class AudioFile(models.Model):
    UPLOADING = 'uploading'
    UPLOADED = 'uploaded'
    IN_PROGRESS = 'in_progress'
    TRANSCRIBED = 'transcribed'
    FAILED = 'failed'

    TRANSCRIPTION_STATUSES = (
        (UPLOADING, _('Uploading')),
        (UPLOADED, _('Uploaded')),
        (IN_PROGRESS, _('In progress')),
        (TRANSCRIBED, _('Transcribed')),
        (FAILED, _('Failed'))
    )

    status = models.CharField(
        _('Transcription status'), max_length=11, choices=TRANSCRIPTION_STATUSES, default=UPLOADING
    )
    file = models.FileField(_('Audio file'), upload_to=get_audio_file_upload_path, blank=True, null=True)
    file_name_original = models.CharField(_('Original file name'), max_length=256)
    file_name = models.CharField(_('File name in S3 storage'), max_length=256, unique=True)
    file_type = models.CharField(_('File type'), max_length=256)
    user_email = models.EmailField(_('Email address'))
    upload_time = models.DateTimeField(_('Upload time'), auto_now_add=True)
    transcription = models.TextField(_('Transcription result'), null=True, blank=True)
    transcription_start = models.DateTimeField(_('Transcription start time'), null=True, blank=True)
    transcription_end = models.DateTimeField(_('Transcription end time'), null=True, blank=True)
    transcription_job_id = models.UUIDField(_('Celery transcription job id'), null=True, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.shortened_original_name} ({self.get_status_display()})'

    @property
    def shortened_original_name(self):
        original_name = self.file_name_original
        if len(str(self.file_name_original)) > 50:
            original_name = original_name[:50] + '...'
        return original_name

    @property
    def transcription_duration(self):
        return round((self.transcription_end - self.transcription_start).total_seconds(), 2)