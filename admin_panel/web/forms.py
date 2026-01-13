from django import forms

class UserEditForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    is_active = forms.BooleanField(required=False, label="Active Status")
    is_premium = forms.BooleanField(required=False, label="Premium User")
    
    # Validation for balance handling
    balance = forms.DecimalField(
        required=True, 
        min_value=0, 
        help_text="Warning: Changing balance directly affects user funds."
    )
