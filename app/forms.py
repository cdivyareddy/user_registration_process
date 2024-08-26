from django import forms
from app.models import *
class userForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','password','email']
        widgets={
            'password':forms.PasswordInput()
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model=profile
        fields=['profile_pic','address']
    