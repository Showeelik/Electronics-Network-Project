from django.contrib import admin
from django.utils.html import format_html
from .models import NetworkNode, Product


class ProductInline(admin.TabularInline):
    """
    Отображение продуктов внутри модели узла сети.
    """
    model = Product
    extra = 1


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'node_type', 
        'get_hierarchy_level', 
        'city', 
        'country', 
        'debt', 
        'supplier_link',
        'created_at'
    )
    
    list_filter = ('node_type', 'country', 'city')
    search_fields = ('name', 'email', 'city', 'country')
    
    inlines = [ProductInline]
    
    actions = ['clear_debt']
    
    def get_hierarchy_level(self, obj):
        """
        Получение уровня иерархии для отображения в админке.
        """
        return obj.get_hierarchy_level()
    
    get_hierarchy_level.short_description = 'Уровень иерархии'
    
    def supplier_link(self, obj):
        """
        Создание ссылки на поставщика.
        """
        if obj.supplier:
            url = f"/admin/network/networknode/{obj.supplier.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.supplier)
        return "-"
    
    supplier_link.short_description = 'Поставщик'
    
    def clear_debt(self, request, queryset):
        """
        Admin action для очистки задолженности у выбранных объектов.
        """
        updated = queryset.update(debt=0.00)
        if updated == 1:
            message = 'У одного узла очищена задолженность'
        else:
            message = f'У {updated} узлов очищена задолженность'
        self.message_user(request, message)
    
    clear_debt.short_description = 'Очистить задолженность перед поставщиком'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'release_date', 'network_node')
    list_filter = ('release_date',)
    search_fields = ('name', 'model')