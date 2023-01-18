from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from transcriber.models import AudioFile


class AudioFileAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _('User information'),
            {'fields': ('user_email',)}
        ),
        (
            _('Audio information'),
            {'fields': ('file', 'file_name_original', 'file_name', 'file_type', 'upload_time')}
        ),
        (
            _('Transcription information'),
            {'fields': ('transcription', 'transcription_start', 'transcription_end', 'status')}
        )
    )

    readonly_fields = (
        'file', 'file_name_original', 'file_name', 'file_type',
        'upload_time', 'transcription_start', 'transcription_end',
        'status', 'transcription', 'user_email'
    )


admin.site.register(AudioFile, AudioFileAdmin)
