from django.contrib import admin
from django.urls import path, include
from articles.views import user_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('', include('articles.urls')),  # Перенаправление на приложение articles
    path('accounts/login/', user_login, name='login'),  # Перенаправление на кастомную страницу входа
]
