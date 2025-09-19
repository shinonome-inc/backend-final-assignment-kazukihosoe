from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tweets.models import Tweet, Like

from .models import User, Connection

admin.site.register(User, UserAdmin)
admin.site.register(Tweet)
admin.site.register(Like)
admin.site.register(Connection)
