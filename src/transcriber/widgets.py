from django import forms


class FileDragAndDropWidget(forms.widgets.FileInput):
    template_name = 'widgets/drag_and_drop_widget.html'
