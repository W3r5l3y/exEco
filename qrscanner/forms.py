from django import forms


class QRCodeUploadForm(forms.Form):
    image = forms.ImageField()
