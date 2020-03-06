from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Fieldset

class MyForm(forms.Form):
    userID = forms.CharField(min_length=22, label='', required=False,help_text='')
    userID.widget.attrs.update({'class': 'special'})
    userID.widget.attrs.update(align='center')

