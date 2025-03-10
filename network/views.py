from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import NetworkNode
from .serializers import NetworkNodeSerializer, NetworkNodeCreateUpdateSerializer


class IsActiveUserPermission(permissions.BasePermission):
    """
    Разрешение для проверки, что пользователь активен.
    """
    message = 'Только активные сотрудники имеют доступ к API.'
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active


class NetworkNodeFilter(filters.FilterSet):
    """
    Фильтры для узлов сети.
    """
    country = filters.CharFilter(field_name='country', lookup_expr='icontains')
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    
    class Meta:
        model = NetworkNode
        fields = ['country', 'city', 'node_type']


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    API для CRUD операций с узлами сети.
    """
    queryset = NetworkNode.objects.all()
    permission_classes = [IsActiveUserPermission]
    filterset_class = NetworkNodeFilter
    
    def get_serializer_class(self):
        """
        Использование разных сериализаторов для чтения и записи.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return NetworkNodeCreateUpdateSerializer
        return NetworkNodeSerializer
    
    @action(detail=True, methods=['post'])
    def clear_debt(self, request, pk=None):
        """
        Очистка задолженности у выбранного узла.
        """
        node = self.get_object()
        node.debt = 0.00
        node.save()
        serializer = self.get_serializer(node)
        return Response(serializer.data)