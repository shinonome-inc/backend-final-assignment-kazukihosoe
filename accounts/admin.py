from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from tweets.models import Tweet

admin.site.register(User, UserAdmin)
admin.site.register(Tweet)
