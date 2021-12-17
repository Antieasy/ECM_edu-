from django.db import models
from django.dispatch import Signal
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.core.signing import Signer
from SED1.settings import ALLOWED_HOSTS
import os
import time
from hashlib import sha1
from django.core.validators import FileExtensionValidator
from django.utils.timezone import now
# Create your models here.





class AdvUser(AbstractUser):
    public_key = models.TextField(blank=True, null=True, verbose_name='Публичный ключ')
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    class Meta(AbstractUser.Meta):
        pass




user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)


signer = Signer()


def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    context = {'user': user.username,
               'host': host,
               'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject,body_text)

def content_file_name(instance, filename):
    global ext
    ext = '.' + filename.split('.')[-1]
    filename = sha1(str(time.time()).encode('utf-8')).hexdigest() + ext
    # file = '../media/avatar/' + instance.username + '.jpg'
    # path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file)
    #
    # try:
    #     os.remove(path)
    # except FileNotFoundError:
    #     file = '../media/avatar/' + instance.username + '.png'
    #     path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file)
    #
    #     try:
    #         os.remove(path)
    #     except FileNotFoundError:
    #         pass
    return os.path.join('Documents', filename)

class Documet(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название документа')
    about = models.TextField(verbose_name='Описание документа')
    file = models.FileField(upload_to=content_file_name, validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])])
    date = models.DateTimeField(default=now, editable=False, blank=True, verbose_name='Время загрузки документа')
    author_id = models.IntegerField(blank=True, null=True, verbose_name='ID владельца документа')
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

class User_Document(models.Model):
    id_user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Имеет отношение к этому документу')
    id_document = models.ForeignKey(Documet, on_delete=models.CASCADE, verbose_name='Документ')


    class Meta:
        verbose_name = "Пользователь-Документ"
        verbose_name_plural = "Пользователи-Документы"


class sign(models.Model):
    document = models.ForeignKey(Documet, on_delete=models.CASCADE, verbose_name='Документ')
    path_to_sign = models.FileField(upload_to='signature/', verbose_name='Подпись')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор подписи')
    author_name = models.CharField(max_length=50, verbose_name='Фамилия Имя автора подписи')
    date = models.DateTimeField(default=now, editable=False, blank=True, verbose_name='Время подписи')

    def __str__(self):
        return self.document.title

    class Meta:
        verbose_name = "Подпись"
        verbose_name_plural = "Подписи"
