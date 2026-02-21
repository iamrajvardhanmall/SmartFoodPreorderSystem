"""
forms.py — All Django forms for the Smart Food Stall Pre-Ordering System.

Forms:
  - StudentRegistrationForm : Custom user registration
  - OrderForm               : Placing a new food order
  - FoodItemForm            : Admin: add/edit food items
  - TimeSlotForm            : Admin: add/edit time slots
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, FoodItem, TimeSlot, FoodStall, StallOwner

class StudentRegistrationForm(UserCreationForm):
    email      = forms.EmailField(required=True,
                     widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}))
    first_name = forms.CharField(max_length=50, required=True,
                     widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=50, required=True,
                     widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Repeat password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ['food_item', 'quantity', 'time_slot', 'special_instructions']
        widgets = {
            'food_item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1, 'max': 10, 'value': 1
            }),
            'time_slot': forms.Select(attrs={'class': 'form-select', 'id': 'id_time_slot'}),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'E.g., No onions, extra spicy…'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = FoodItem.objects.filter(is_available=True).select_related('stall')
        self.fields['food_item'].queryset = qs
        self.fields['food_item'].label_from_instance = (
            lambda obj: f"[{obj.stall.name if obj.stall else 'General'}]  {obj.name}  —  ₹{obj.price}"
        )
        self.fields['time_slot'].queryset = TimeSlot.objects.filter(is_active=True)
        # Add helpful labels
        self.fields['food_item'].empty_label  = '— Select a Food Item (from any stall) —'
        self.fields['time_slot'].empty_label  = '— Select a Time Slot —'

    def clean_time_slot(self):
        slot = self.cleaned_data.get('time_slot')
        if slot and slot.is_full():
            raise forms.ValidationError(
                f"'{slot.slot_name}' is full. Please choose a different time slot."
            )
        return slot

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        if qty > 10:
            raise forms.ValidationError("Maximum 10 items per order.")
        return qty


class FoodItemForm(forms.ModelForm):

    class Meta:
        model  = FoodItem
        fields = ['stall', 'name', 'description', 'price', 'available_qty', 'is_available', 'image']
        widgets = {
            'stall':         forms.Select(attrs={'class': 'form-select'}),
            'name':          forms.TextInput(attrs={'class': 'form-control'}),
            'description':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price':         forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50'}),
            'available_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stall'].queryset = FoodStall.objects.filter(is_active=True)
        self.fields['stall'].empty_label = '— Select a Stall —'

class FoodStallForm(forms.ModelForm):

    class Meta:
        model  = FoodStall
        fields = ['name', 'description', 'location', 'is_active', 'image']
        widgets = {
            'name':        forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., Stall A - South Indian'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location':    forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., Block B, Near Library'
            }),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StallOwnerCreationForm(forms.Form):
    username   = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Login username'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last name (optional)'}))
    password   = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))
    stall      = forms.ModelChoiceField(
        queryset=FoodStall.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='— Select a Stall —'
    )

    def clean_username(self):
        uname = self.cleaned_data['username']
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError('Username already taken.')
        return uname

    def save(self):
        user = User.objects.create_user(
            username   = self.cleaned_data['username'],
            password   = self.cleaned_data['password'],
            first_name = self.cleaned_data['first_name'],
            last_name  = self.cleaned_data.get('last_name', ''),
        )
        owner = StallOwner.objects.create(
            user  = user,
            stall = self.cleaned_data['stall'],
        )
        return owner


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model  = TimeSlot
        fields = ['slot_name', 'max_capacity', 'is_active']
        widgets = {
            'slot_name':    forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., 10:30 AM - 10:45 AM'
            }),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active':    forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
