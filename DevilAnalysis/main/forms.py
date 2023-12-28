from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Investment, Portfolio
from django.forms import ModelForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class BuyForm(ModelForm):

    class Meta:
        model = Investment
        fields = ["name", "purchase_price", "quantity", "portfolio"]



class SellForm(ModelForm):
    sell_price = forms.FloatField()

    class Meta:
        model = Investment
        fields = ["name", "quantity"]

class CreatePortfolioForm(ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name"]


class itemAnalysisForm(forms.Form):
    name = forms.CharField()


