from django import forms

class GoogleSheetForm(forms.Form):
    sheet_link = forms.URLField(label='Google Sheets Link', max_length=200)
