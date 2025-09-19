from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tweets.models import Tweet

from .models import User

admin.site.register(User, UserAdmin)
admin.site.register(Tweet)
