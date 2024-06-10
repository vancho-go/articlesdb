from django.urls import path
from .views import article_list, article_create, article_update, article_delete, article_detail, add_error_description, register, user_login, user_logout

urlpatterns = [
    path('', article_list, name='article_list'),
    path('create/', article_create, name='article_create'),
    path('update/<int:pk>/', article_update, name='article_update'),
    path('delete/<int:pk>/', article_delete, name='article_delete'),
    path('detail/<int:pk>/', article_detail, name='article_detail'),
    path('add_error/<int:pk>/', add_error_description, name='add_error_description'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
