from django.contrib import admin

from .models import About, Category, Contact, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'featured')
    list_filter = ('category', 'featured')
    search_fields = ('name',)
    list_editable = ('price', 'featured')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_name', 'email', 'created')
    readonly_fields = ('created',)


admin.site.register(Category)
admin.site.register(About)
