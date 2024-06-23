from django import forms

from streaming.models import Payment

class PaymentForm(forms.ModelForm):
    cc_number = forms.CharField(required=False)
    cc_name = forms.CharField(required=False)
    cc_cvv = forms.CharField(required=False)

    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'email', 'cc_number', 'cc_name', 'cc_cvv']

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")

        if payment_method == 'credit_card':
            if not cleaned_data.get("cc_number"):
                self.add_error('cc_number', 'Credit card number is required.')
            if not cleaned_data.get("cc_name"):
                self.add_error('cc_name', 'Name on credit card is required.')
            if not cleaned_data.get("cc_cvv"):
                self.add_error('cc_cvv', 'CVV is required.')
        return cleaned_data
    

class PaymentForm(forms.ModelForm):
    email = forms.EmailField(required=False) 

    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'email']