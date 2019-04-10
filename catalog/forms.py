from django import forms


class RateForm(forms.Form):
    user = forms.IntegerField(label='user')
    item = forms.IntegerField(label='item')
    rate = forms.IntegerField(label='rate')
