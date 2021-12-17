from django.contrib import admin
from .models import *
# Register your models here.
def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с оповещениями отправлены')
send_activation_notifications.short_description = 'Отправка писем с ' +   'оповещениями об активации'




class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # list_filter = (NonactivatedFilter,)
    # fields = (('username', 'email'), ('first_name', 'last_name'), ('send_messages', 'is_active', 'is_activated'),
    #           ('is_staff', 'is_superuser'), 'groups', 'user_permissions', ('last_login', 'date_joined'))
    exclude = ['']
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)
    def __str__(self):
        return "Пользователь %s " % (self.username)


admin.site.register(AdvUser,AdvUserAdmin)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'title', 'about')
    search_fields = ('title', 'about')
    exclude = ['']

    def __str__(self):
        return "%s " % (self.title)

admin.site.register(Documet, DocumentAdmin)

class User_DocumentAdmin(admin.ModelAdmin):
    list_display = ('id_document', 'id_user')
    search_fields = ('id_document', 'id_user')
    exclude = ['']

admin.site.register(User_Document, User_DocumentAdmin)


class SignAdmin(admin.ModelAdmin):

    class Meta:
        model = sign


admin.site.register(sign, SignAdmin)
