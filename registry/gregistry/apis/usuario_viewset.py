from django.contrib.auth.models import User, Group
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    class Meta:
        model = User
        fields = ('id', 'email',  'groups')

class AuthViewSet(viewsets.ViewSet):

    @action(methods=['post'], detail=False, url_path='register')
    def register(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'El email y la contraseña son requeridos'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'El email ya está en uso'}, status=400)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        try:
            comprador_group = Group.objects.get(name='Comprador')
            user.groups.add(comprador_group)
        except Group.DoesNotExist:
            return Response({'error': 'El grupo "Comprador" no existe'}, status=400)

        return Response({
            'id': user.id,
            'email': user.email,
        }, status=201)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
