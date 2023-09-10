from django import forms
from.models import * 
class FacebookPageMappingForm(forms.ModelForm):
    class Meta:
        model = FacebookPage
        fields = ['users']

    users = forms.ModelMultipleChoiceField(
        queryset=CustomUserTypes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
