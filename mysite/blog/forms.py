from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    # Sender's name
    name = forms.CharField(max_length=25)
    # Sender's email address
    email = forms.EmailField()
    # Recipient's email address
    to = forms.EmailField()
    # Optional message to include in the email
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class SearchForm(forms.Form):
    query = forms.CharField()