from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.shortcuts import get_object_or_404
from company.models import *
from company.forms import *
from django.views.generic.edit import UpdateView
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from django.http import HttpResponse
import inspect, os.path

from django.http import FileResponse

# Create your views here.


def index(request):

    return render(request, 'index.html')


class BBLoginView(LoginView):
    template_name = 'profile/login.html'



@login_required
def profile(request):

    return render(request, 'profile/profile.html', locals())


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'profile/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'profile/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)



class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'profile/password_change.html'
    success_url = reverse_lazy('profile')
    success_message = 'Пароль изменен'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'profile/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('register_done')


class RegisterDoneView(TemplateView):
    template_name = 'profile/register_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'profile/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'profile/user_is_activated.html'
    else:
        template = 'profile/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

def about_this(request):

    return render(request, 'about_this.html', locals())



@login_required
def upload_documet(request):
    if request.method == "POST":
        form = UploadDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()
            u_d = User_Document()
            u_d.id_user = AdvUser.objects.get(pk=request.user.pk)
            u_d.id_document = Documet.objects.get(pk=doc.id)
            u_d.author_id = request.user.pk
            u_d.save()

            return render(request, 'profile/profile.html')
        else:
            return render(request, 'actions/upload_document.html', locals())
    else:
        form = UploadDocumentForm()
    return render(request, 'actions/upload_document.html', locals())


@login_required
def view_documents(request):
    form = Documet.objects.filter(user_document__id_user=request.user.id)
    all_sign = sign.objects.filter(author_id=request.user.id)
    id_doc_where_sign = [i.document_id for i in all_sign]
    return render(request, 'actions/view_documents.html', locals())


@login_required
def send_on_signature(request):
    doc = Documet.objects.filter(user_document__id_user=request.user.id)
    users = AdvUser.objects.all().filter(is_superuser=False)
    choices_doc = [("%s" % d['id'], "%s" % d['title']) for d in doc.values('id', 'title')]
    author_choice = [("%s" % u['id'], "%s" % (u['last_name'] + ' ' + u['first_name'])) for u in
                     AdvUser.objects.all().values('id', 'first_name', 'last_name')]
    form_sign = SendOnSignature.form_class(doc_choices=choices_doc, author_choice=author_choice)
    if request.POST:
        if int(request.POST['doc_id']) in [i.id for i in doc]:
            u_d = User_Document()
            u_d.id_document = Documet.objects.get(pk=int(request.POST['doc_id']))
            u_d.id_user = AdvUser.objects.get(pk=int(request.POST['author']))
            u_d.save()
            messages.add_message(request, 25, 'Документ успешно отправлен')
            return render(request, 'profile/profile.html')
        else:
            messages.add_message(request, 50, 'Ага. Отправил этот запрос в отдел ИБ')
            return render(request, 'actions/send_on_singature.html', {'doc':doc, 'users':users})
    return render(request, 'actions/send_on_singature.html', locals())


def mail(request):
    pass


@login_required
def check_on_signature(request):
    doc = Documet.objects.filter(user_document__id_user=request.user)
    favorite_choices_doc = [("%s" % d['id'], "%s" % d['title']) for d in doc.values('id', 'title')]
    author_choice = [("%s" % u['id'], "%s" % (u['last_name'] + ' ' + u['first_name'])) for u in AdvUser.objects.all().values('id', 'first_name', 'last_name')]
    form_sign = CheckSignature.form_class(favorite_choices= favorite_choices_doc, author_choice=author_choice)
    if request.POST:
        file_sign = UploadFileForm(request.POST,request.FILES)
        if file_sign.is_valid():
            if int(request.POST['doc_id']) in [i.id for i in doc]:
                user_owner_sign = AdvUser.objects.get(pk=request.POST['author'])
                key_public = RSA.import_key(user_owner_sign.public_key.encode('utf-8'))
                file_doc = open(Documet.objects.get(pk=int(request.POST['doc_id'])).file.path, 'rb').read()
                with open(request.user.username + '_sign' + '.txt', 'wb') as destination:
                    for chunk in request.FILES['file'].chunks():
                        destination.write(chunk)
                file_sign = open(request.user.username + '_sign' + '.txt', 'rb').read()
                h = SHA256.new(file_doc)
                try:
                    pkcs1_15.new(key_public).verify(h, file_sign)
                    messages.add_message(request, 25, 'Документ действительно подписан сотрудником: ' + user_owner_sign.last_name +  ' ' + user_owner_sign.first_name)
                except (ValueError, TypeError):
                    messages.add_message(request, 50, 'Неверная подпись')
                os.remove(os.path.abspath(request.user.username + '_sign' + '.txt'))
                return render(request, 'actions/check_on_singature.html', locals())
            else:
                messages.add_message(request, 50, 'Ага. Отправил этот запрос в отдел ИБ')
                return render(request, 'profile/profile.html', locals())

    return render(request, 'actions/check_on_singature.html', locals())

@login_required
def create_keys(request):
    user_model = AdvUser.objects.get(pk=request.user.pk)
    if user_model.public_key:
        messages.add_message(request, 50, 'Вы уже сформировали ключи')
        return render(request, 'profile/profile.html')
    else:
        key = RSA.generate(2048)
        private_key = key.export_key()
        user_model.public_key = key.publickey().export_key().decode('UTF-8')
        user_model.save()
        response = HttpResponse(private_key, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(request.user.username + '_sign.txt')
        return response


@login_required
def sign_doc(request, id_doc):
    doc = Documet.objects.filter(user_document__id_user=request.user.id)
    form = UploadFileForm()
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if int(id_doc) in [i.id for i in doc]:
                docum_need_sign = doc.get(pk=id_doc).file.path
                message = open(doc.get(id=id_doc).file.path, 'rb').read()
                with open(request.user.username + '.txt', 'wb') as destination:
                    for chunk in request.FILES['file'].chunks():
                        destination.write(chunk)
                key = RSA.import_key(open(request.user.username + '.txt').read())
                h = SHA256.new(message)
                signer = pkcs1_15.new(key)
                signature = signer.sign(h)
                file_out = open("media/signature/" + docum_need_sign.split("\\")[-1] + ".pem", "wb")
                file_out.write(signature)
                file_out.close()
                sign_model = sign()
                sign_model.document_id = id_doc
                sign_model.path_to_sign = "media/signature/" + docum_need_sign.split("\\")[-1] + ".pem"
                sign_model.author_id = request.user.id
                sign_model.author_name = str(request.user.last_name) + ' ' + str(request.user.first_name)
                sign_model.save()
                os.remove(os.path.abspath(request.user.username + '.txt'))
                return render(request, 'profile/profile.html', {})
            else:
                messages.add_message(request, 50, 'Подписываем документ к вам не относится. '
                                                  'Данный запрос был отправлен в отдел ИБ')
                return render(request, 'profile/profile.html', locals())
    return render(request, 'actions/sign_doc.html', locals())