from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from transcriber.models import AudioFile


class FileIdSerializer(serializers.Serializer):
    id = serializers.IntegerField(label=_('Audio file id'))


class AudioFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ('file_name', 'file_type', 'user_email')

    def validate_file_type(self, value):
        if value.startswith('audio/') or value == 'application/ogg':
            return value
        raise ValidationError(_('Given file type doesn\'t belong to an audio file type.'))


class UploadedFileSerializer(FileIdSerializer):
    status = serializers.ChoiceField(choices=[AudioFile.UPLOADED, AudioFile.FAILED])
