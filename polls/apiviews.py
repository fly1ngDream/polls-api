from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

from .models import Poll, Choice
from .serializers import (
    PollSerializer,
    ChoiceSerializer,
    VoteSerializer,
    UserSerializer,
)


class PollList(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class PollDetail(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class ChoiceList(generics.ListCreateAPIView):
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs['pk'])
        return queryset
    serializer_class = ChoiceSerializer


    def post(self, request, pk):
        if request.user != Poll.objects.get(pk=pk).created_by:
            raise PermissionDenied
        else:
            choice_text = request.data.get('choice_text')
            data = {'choice_text': choice_text, 'poll': pk}
            serializer = ChoiceSerializer(data=data)
            if serializer.is_valid():
                choice = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateVote(generics.CreateAPIView):
    serializer_class = VoteSerializer

    def post(self, request, pk, choice_pk):
        voted_by = request.user.pk
        data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            vote = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def create(self, request):
        question = request.data.get('question')
        created_by = request.user.pk
        data = {'question': question, 'created_by': created_by}
        serializer = PollSerializer(data=data)
        if serializer.is_valid():
            poll = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk):
        if request.user != Poll.objects.get(pk=pk).created_by:
            raise PermissionDenied
        else:
            Poll.objects.get(pk=pk).delete()
            return Response({'detail': f"Poll {pk} was deleted"})


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({'token': user.auth_token.key})
        else:
            return Response({'error': 'Wrong Credentials'}, status=status.HTTP_400_BAD_REQUEST)
