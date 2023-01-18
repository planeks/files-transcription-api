import pathlib
from uuid import uuid4

from transcriber.models import AudioFile


def generate_unique_file_name(file_name):
    while True:
        extension = pathlib.Path(file_name).suffix
        unique_file_name = f"{uuid4().hex}{extension}"
        if not AudioFile.objects.filter(file_name=unique_file_name).exists():
            return f"{uuid4().hex}{extension}"
