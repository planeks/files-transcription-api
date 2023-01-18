from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from transcriber.forms import AudioFileSubmitForm
from transcriber.models import AudioFile
from transcriber.serializers import AudioFileUploadSerializer, UploadedFileSerializer, FileIdSerializer
from transcriber.services import AudioFileS3UploadService
from transcriber.tasks import transcribe_audio_file

s3_presigned_post_responses = {
    200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'acl': openapi.Schema(type=openapi.TYPE_STRING, title='acl'),
            'Content-Type': openapi.Schema(type=openapi.TYPE_STRING, title='Content-Type'),
            'key': openapi.Schema(type=openapi.TYPE_STRING, title='key'),
            'x-amz-algorithm': openapi.Schema(type=openapi.TYPE_STRING, title='x-amz-algorithm'),
            'x-amz-credential': openapi.Schema(type=openapi.TYPE_STRING, title='x-amz-credential'),
            'x-amz-date': openapi.Schema(type=openapi.TYPE_STRING, title='x-amz-date'),
            'policy': openapi.Schema(type=openapi.TYPE_STRING, title='policy'),
            'x-amz-signature': openapi.Schema(type=openapi.TYPE_STRING, title='x-amz-signature'),
        },
        required=[
            'acl', 'Content-Type', 'key', 'x-amz-algorithm', 'x-amz-credential',
            'x-amz-date', 'policy', 'x-amz-signature'
        ]
    )
}


@swagger_auto_schema(
    method='POST',
    operation_description=_('Retrieves presigned data for uploading files directly to S3.'),
    request_body=AudioFileUploadSerializer,
    responses=s3_presigned_post_responses
)
@api_view(['POST'])
def audio_file_upload_start_view(request):
    serializer = AudioFileUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    service = AudioFileS3UploadService()

    presigned_data = service.start(**serializer.validated_data)
    return Response(data=presigned_data)


@swagger_auto_schema(
    method='POST',
    operation_description=_('Updates audio file status after upload.'),
    request_body=UploadedFileSerializer,
    responses={200: openapi.Response('File Id', FileIdSerializer)}
)
@api_view(['POST'])
def audio_file_upload_finish_view(request):
    serializer = UploadedFileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    file_id = serializer.validated_data.get('id')
    file_status = serializer.validated_data.get('status')

    file = get_object_or_404(AudioFile, id=file_id)

    service = AudioFileS3UploadService()
    service.finish(file=file, status=file_status)

    response_serializer = FileIdSerializer({'id': file.id})
    return Response(data=response_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description=_('Runs audio file transcription process.'),
    request_body=FileIdSerializer,
    responses={200: openapi.Response('File Id', FileIdSerializer)}
)
@api_view(['POST'])
def transcribe_audio_file_view(request):
    serializer = FileIdSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    file_id = serializer.validated_data.get('id')
    file = get_object_or_404(AudioFile, id=file_id)

    task = transcribe_audio_file.delay(file.pk)
    file.transcription_job_id = task.id
    file.save()

    response_serializer = FileIdSerializer({'id': file.id})
    return Response(data=response_serializer.data, status=status.HTTP_200_OK)


def index(request):
    return render(request, 'index.html', {'form': AudioFileSubmitForm()})
