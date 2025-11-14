from django import forms
from .models import Member, Payment
from datetime import date


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'phone', 'admission_date', 'plan_months', 'fee_amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'plan_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1, 'required': True}),
            'fee_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01, 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # New member
            self.fields['admission_date'].initial = date.today()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'paid_on']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01, 'required': True}),
            'paid_on': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)
        if member:
            self.fields['amount'].initial = member.fee_amount
        self.fields['paid_on'].initial = date.today()

