from django import forms

from transcriber.models import AudioFile
from transcriber.widgets import FileDragAndDropWidget


class AudioFileSubmitForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        fields = ('user_email', 'file')
        widgets = {
            'file': FileDragAndDropWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True
