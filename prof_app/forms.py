from django import forms
from .models import ClassModel

class ClassForm(forms.ModelForm):
    class Meta:
        model = ClassModel
        fields = ['name', 'subject']
