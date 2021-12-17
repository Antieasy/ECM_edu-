"""SED1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from company.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name="register_done"),
    path('accounts/register/', RegisterUserView.as_view(), name="register"),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/profile/new_document/', upload_documet, name='upload_document'),
    path('accounts/profile/view_documents/', view_documents, name='view_documents'),
    path('accounts/profile/sign_document/<int:id_doc>', sign_doc, name='sign_document'),
    path('accounts/profile/create_keys/', create_keys, name='create_keys'),
    path('accounts/profile/send_documents/', send_on_signature, name='send_on_signature'),
    path('accounts/profile/check_documents/', check_on_signature, name='check_on_signature'),
    path('about', about_this, name='about')
]

if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

# Эта строка опциональна и будет добавлять url'ы только при DEBUG = True

urlpatterns += staticfiles_urlpatterns()