from django import forms
from .models import Watchlist, Stock

class WatchlistForm(forms.ModelForm):
    stocks = forms.ModelMultipleChoiceField(
        queryset=Stock.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'})
    )

    class Meta:
        model = Watchlist
        fields = ['name', 'description', 'stocks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 