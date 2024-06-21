from django import forms

from streaming.models import Payment

class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('virtual_account', 'Virtual Account'),
        ('credit_card', 'Credit Card')
    ]
    
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
    cc_number = forms.CharField(max_length=16, required=False)
    cc_name = forms.CharField(max_length=100, required=False)
    cc_cvv = forms.CharField(max_length=4, required=False)
    email = forms.EmailField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'credit_card':
            if not cleaned_data.get('cc_number'):
                self.add_error('cc_number', 'Credit card number is required.')
            if not cleaned_data.get('cc_name'):
                self.add_error('cc_name', 'Name on card is required.')
            if not cleaned_data.get('cc_cvv'):
                self.add_error('cc_cvv', 'CVV is required.')
        
        return cleaned_data
    

class PaymentForm(forms.ModelForm):
    email = forms.EmailField(required=False) 

    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'email']