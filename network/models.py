from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class NetworkNode(models.Model):
    """
    Базовая модель для всех узлов сети по продаже электроники.
    Представляет иерархическую структуру с тремя уровнями:
    - Завод (уровень 0)
    - Розничная сеть (уровень 1)
    - Индивидуальный предприниматель (уровень 2)
    """
    NODE_TYPES = [
        ('factory', 'Завод'),
        ('retail', 'Розничная сеть'),
        ('entrepreneur', 'Индивидуальный предприниматель'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название')
    # Контактная информация
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=255, verbose_name='Улица')
    house_number = models.CharField(max_length=20, verbose_name='Номер дома')
    
    # Тип узла сети
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, verbose_name='Тип узла')
    
    # Связь с поставщиком (null=True для заводов, которые не имеют поставщиков)
    supplier = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='clients',
        verbose_name='Поставщик'
    )
    
    # Задолженность перед поставщиком
    debt = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name='Задолженность перед поставщиком'
    )
    
    # Автоматическое заполнение времени создания
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    
    def __str__(self):
        return f"{self.name} ({self.get_node_type_display()})"
    
    def get_hierarchy_level(self):
        """
        Определение уровня иерархии узла.
        Завод всегда находится на уровне 0.
        """
        if self.node_type == 'factory':
            return 0
            
        if not self.supplier:
            return 0
            
        level = 1
        current = self.supplier
        
        while current.supplier:
            level += 1
            current = current.supplier
            
        return level
    
    def clean(self):
        """
        Проверка корректности иерархии.
        Завод не должен иметь поставщика.
        """
        if self.node_type == 'factory' and self.supplier:
            raise ValidationError({'supplier': _('Завод не может иметь поставщика')})
        
        # Проверяем цикличность связей
        if self.supplier:
            current = self.supplier
            while current:
                if current == self:
                    raise ValidationError({'supplier': _('Обнаружена циклическая зависимость в цепочке поставщиков')})
                current = current.supplier
    
    class Meta:
        verbose_name = 'Узел сети'
        verbose_name_plural = 'Узлы сети'


class Product(models.Model):
    """
    Модель для продуктов, которые есть у узлов сети.
    """
    name = models.CharField(max_length=255, verbose_name='Название')
    model = models.CharField(max_length=100, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')
    
    # Связь с узлом сети
    network_node = models.ForeignKey(
        NetworkNode, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name='Узел сети'
    )
    
    def __str__(self):
        return f"{self.name} ({self.model})"
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'