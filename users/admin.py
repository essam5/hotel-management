from django.contrib import admin
from django.contrib.auth.models import User 

# Register your models here.

# Register the User model
admin.site.unregister(User)  # Unregister the default User model
@admin.register(User)  # Register it again to customize the User admin panel
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    