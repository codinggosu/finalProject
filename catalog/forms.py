from django import forms
from django.forms import ModelForm, CharField, TextInput, ChoiceField


class RateForm(forms.Form):
    user = forms.IntegerField(label='user')
    item = forms.IntegerField(label='item')
    rate = forms.IntegerField(label='rate')



class ReviewForm(forms.Form):
    OPTIONS = (
    (1, '1점'),
    (2, '2점'),
    (3, '3점'),
    (4, '4점'),
    (5, '5점'),
    )
    # your_review = forms.CharField(label='Your Review', max_length=500, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))
    your_review = forms.CharField(label='Your Review', max_length=500, widget=forms.Textarea)
    your_rate = forms.ChoiceField(widget=forms.Select(), label='Your rate', choices=OPTIONS)
    # user = CharField(label='tempid', widget=TextInput(attrs={'type':'number'}))

    def clean_review_data(self):
        data = self.cleaned_data['your_review']
        return data
