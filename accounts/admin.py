from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tweets.models import Like, Tweet

from .models import Connection, User

admin.site.register(User, UserAdmin)
admin.site.register(Tweet)
admin.site.register(Like)
admin.site.register(Connection)
