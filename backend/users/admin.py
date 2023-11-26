from django.contrib import admin
#альт. метод хэша паролей - from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


#альтернативный метод хэша паролей - class UsersAdmin(UserAdmin):
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
    list_editable = ('is_active', 'password')
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
