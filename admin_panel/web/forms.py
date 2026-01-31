from django import forms

class UserEditForm(forms.Form):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_active = forms.BooleanField(required=False, label="Active Status")
    is_premium = forms.BooleanField(required=False, label="Premium User")
    
    # Validation for balance handling
    balance = forms.DecimalField(
        required=True, 
        min_value=0, 
        help_text="Warning: Changing balance directly affects user funds."
    )
