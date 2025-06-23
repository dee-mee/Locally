from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator

from .models import Customer

class CustomerForm(forms.ModelForm):
    """Form for creating and updating customers"""
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator(message=_("Enter a valid email address."))],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('customer@example.com')
        })
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    
    phone = forms.CharField(
        required=False,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('+1234567890')
        })
    )
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'customer_type',
            'company_name', 'tax_number', 'address', 'city', 'state',
            'postal_code', 'country', 'notes', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First Name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Last Name')
            }),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Company Name')
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tax ID / VAT')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Street Address')
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('City')
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('State / Province / Region')
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Postal / Zip Code')
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Country')
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Additional notes about this customer...')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make first name required
        self.fields['first_name'].required = True
        
        # Set initial value for is_active if creating a new customer
        if not self.instance.pk:
            self.fields['is_active'].initial = True
    
    def clean_email(self):
        """Ensure email is unique if provided"""
        email = self.cleaned_data.get('email')
        if not email:
            return email
            
        qs = Customer.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise forms.ValidationError(_('A customer with this email already exists.'))
            
        return email.lower()
    
    def clean_phone(self):
        """Format phone number"""
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return phone
            
        # Remove any non-digit characters except leading +
        phone = ''.join(c for c in phone if c == '+' or c.isdigit())
        return phone
