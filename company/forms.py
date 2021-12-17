from django import forms
from .models import *
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView



class RegisterUserForm(forms.ModelForm):
    username = forms.CharField(label='Логин', help_text = 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.' )
    email = forms.EmailField(required=True, label='Aдpec Электронной почты')
    password1 = forms.CharField(label='Пapoль',
         widget=forms.PasswordInput, help_text = password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пapoль (повторно)',
    widget=forms.PasswordInput, help_text='Введите тот же самый пароль для проверки')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают',code=' password _ mismatch ')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')


class UploadDocumentForm(forms.ModelForm):

    class Meta:

        model = Documet
        fields = ('title', 'about', 'file')


class UserDocumentForm(forms.ModelForm):

    class Meta:

        model = User_Document
        fields = ('id_user', 'id_document')


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('email', 'first_name', 'last_name')


class UploadFileForm(forms.Form):
    file = forms.FileField()


class CheckSignatureForm(forms.Form):
    doc_id = forms.ChoiceField(choices=[], label='Какой документ проверить?')
    author = forms.ChoiceField(choices=[], label='Чья это подпись?')
    file = forms.FileField(help_text='Вам необходимо загрузить подпись выбраного человека с расширением .pem',
                           label='Загрузить подпись')

    def __init__(self, *args, **kwargs):
        """Populating the choices of  the favorite_choices field using the favorites_choices kwargs"""

        favorites_choices = kwargs.pop('favorite_choices')
        author_choices = kwargs.pop('author_choice')

        super().__init__(*args, **kwargs)

        self.fields['doc_id'].choices = favorites_choices
        self.fields['author'].choices = author_choices

class CheckSignature(FormView):
    form_class = CheckSignatureForm

    def get_form_kwargs(self):
        """Passing the 'choices' from your view to the form __init__ method"""

        kwargs = super().get_form_kwargs()

        return kwargs

    def form_valid(self, form_class):
        form_class.save()
        return super(CheckSignature, self).form_valid(form_class)


class SendOnSignatureForm(forms.Form):
    doc_id = forms.ChoiceField(choices=[], label='Какой документ отправить')
    author = forms.ChoiceField(choices=[], label='Кому отправить')


    def __init__(self, *args, **kwargs):
        """Populating the choices of  the favorite_choices field using the favorites_choices kwargs"""

        doc_choices = kwargs.pop('doc_choices')
        author_choices = kwargs.pop('author_choice')

        super().__init__(*args, **kwargs)

        self.fields['doc_id'].choices = doc_choices
        self.fields['author'].choices = author_choices

class SendOnSignature(FormView):
    form_class = SendOnSignatureForm

    def get_form_kwargs(self):
        """Passing the 'choices' from your view to the form __init__ method"""

        kwargs = super().get_form_kwargs()

        return kwargs

    def form_valid(self, form_class):
        form_class.save()
        return super(SendOnSignature, self).form_valid(form_class)
