from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)
  email = serializers.EmailField()
  
  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'password')
    
class UserViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  
  @action(detail=False, methods=['post'], url_path='register')
  def register(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    if User.objects.filter(username=username).exists():
      return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
      return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
    
    User.objects.create_user(username=username, email=email, password=password)
    return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['get'], url_path='me')
  def me(self, request):
    serializer = self.get_serializer(request.user)
    return Response(serializer.data)