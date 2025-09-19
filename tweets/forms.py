from django import forms

from .models import Tweet


class CreateForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ('title', 'content')
