from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'model', 'release_date']


class NetworkNodeSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.SerializerMethodField()
    
    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'node_type', 'email', 'country', 'city', 
            'street', 'house_number', 'supplier', 'debt', 
            'created_at', 'products', 'hierarchy_level'
        ]
        read_only_fields = ['debt', 'created_at']
        
    def get_hierarchy_level(self, obj):
        return obj.get_hierarchy_level()


class NetworkNodeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления узлов сети 
    с запретом обновления поля задолженности.
    """
    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'node_type', 'email', 'country', 'city', 
            'street', 'house_number', 'supplier'
        ]
    
    def validate(self, data):
        """
        Проверка на циклические ссылки и корректность иерархии.
        """
        instance = getattr(self, 'instance', None)
        
        # Если обновляем существующий объект
        if instance:
            supplier = data.get('supplier', instance.supplier)
            node_type = data.get('node_type', instance.node_type)
        else:
            supplier = data.get('supplier')
            node_type = data.get('node_type')
        
        # Проверка для заводов
        if node_type == 'factory' and supplier:
            raise serializers.ValidationError(
                {'supplier': 'Завод не может иметь поставщика'}
            )
        
        # Проверка на циклические ссылки
        if supplier:
            current = supplier
            while current:
                if instance and current.id == instance.id:
                    raise serializers.ValidationError(
                        {'supplier': 'Обнаружена циклическая зависимость в цепочке поставщиков'}
                    )
                current = current.supplier
        
        return data