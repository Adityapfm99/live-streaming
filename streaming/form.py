from django import forms

from streaming.models import Payment

class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('bank_transfer', 'Bank Transfer'),
        ('virtual_account', 'Virtual Account'),
        ('qris', 'QRIS'),
        ('gateway', 'Payment Gateway')
    ]
    
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)

    

class PaymentForm(forms.ModelForm):
    email = forms.EmailField(required=False) 

    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'email']