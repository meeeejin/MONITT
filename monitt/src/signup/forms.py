from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

        
class MyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super(MyRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
        return user
    
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("The username already exists. Please try another one.")
 
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields did not match.")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(MyRegistrationForm,self).__init__(*args,**kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control','placeholder':'Username', 'type':'text'})
        self.fields['email'].widget.attrs.update({'class':'form-control','placeholder':'Email','type':'email'})
        self.fields['password1'].widget.attrs.update({'class':'form-control','placeholder':'Password','type':'password'})
        self.fields['password2'].widget.attrs.update({'class':'form-control','placeholder':'Confirm password','type':'password'})