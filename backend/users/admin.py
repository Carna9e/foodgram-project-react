from django.contrib import admin

from .models import Subscribe, User


class UsersAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.set_password(obj.password)
        obj.save()

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display: tuple = (
        'user',
        'author',
    )
    search_fields: tuple = (
        'user',
        'author'
    )
    empty_value_display: str = '-пусто-'


admin.site.register(User, UsersAdmin)
admin.site.register(Subscribe, SubscriptionAdmin)
