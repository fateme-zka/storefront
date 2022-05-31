from django.contrib import admin, messages
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models import Count, Q

from .models import *


# filter classes
class UnitPriceFilter(admin.SimpleListFilter):
    title = 'unit price'
    parameter_name = 'unit_price_range'

    def lookups(self, request, model_admin):
        return [
            ('<25', 'less than 25'),
            ('>=25&<50', '25 to 50'),
            ('>=50&<75', '50 to 75'),
            ('>=75', 'more than 75')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<25':
            return queryset.filter(unit_price__lt=25)
        elif self.value() == '>=25&<50':
            return queryset.filter(Q(unit_price__range=(25, 50)) | Q(unit_price=25))
        elif self.value() == '>=50&<75':
            return queryset.filter(Q(unit_price__range=(50, 75)) | Q(unit_price=50))
        elif self.value() == '>=75':
            return queryset.filter(Q(unit_price__gt=75) | Q(unit_price=75))


# Collection Admin
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    ordering = ['title']
    search_fields = ['title']


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status', 'collection']
    list_per_page = 10
    list_editable = ['unit_price']
    list_filter = [UnitPriceFilter]
    ordering = ['unit_price']
    search_fields = ['title']
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }

    def inventory_status(self, product):
        if product.inventory < 7:
            return 'Low'
        return 'Ok'


# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['pk', 'first_name', 'last_name', 'membership', 'orders_count']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    def orders_count(self, customer):
        url = (
                reverse('admin:store_order_changelist')
                + "?"
                + urlencode({
            'customer__id': str(customer.id)
        })
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            customer.orders_count
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


# OrderItem Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    autocomplete_fields = ['product']
    extra = 0
    min_num = 1


# order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    actions = ['payment_completed']
    list_display = ['placed_at', 'payment_status', 'customer_full_name']
    list_per_page = 10
    list_select_related = ['customer']
    # fields = ['payment_status','customer']
    autocomplete_fields = ['customer']

    # @admin.display('first_name','last_name')
    def customer_full_name(self, order):
        return f"{order.customer.first_name} {order.customer.last_name}"

    @admin.action(description='Payment Completed')
    def payment_completed(self, request, queryset):
        completed_count = queryset.update(payment_status='C')
        self.message_user(
            request,
            f"{completed_count} orders payment completed.",
            messages.SUCCESS
        )
