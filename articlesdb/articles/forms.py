from django import forms
from .models import Article
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
import requests

# required_fields = ['publish_year', 'link', 'usage_context', 'maths', 'article_idfr', 'problems_solution', 'term', 'term_desc', 'interest']

class SearchForm(forms.Form):
    term = forms.CharField(required=False, label='Термин')
    title = forms.CharField(required=False, label='Название статьи')
    author = forms.CharField(required=False, label='Автор')
    year = forms.IntegerField(required=False, label='Год публикации')


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['user_ins', 'user_checker']

    def clean(self):
        cleaned_data = super().clean()
        title_rus = cleaned_data.get('title_rus')
        title_eng = cleaned_data.get('title_eng')
        term = cleaned_data.get('term')
        link = cleaned_data.get('link')
        author_rus = cleaned_data.get('author_rus')
        author_eng = cleaned_data.get('author_eng')
        keyword_rus = cleaned_data.get('keyword_rus')
        keyword_eng = cleaned_data.get('keyword_eng')
        article_idfr = cleaned_data.get('article_idfr')

        # Название статьи должно содержать термин
        if term and (term not in (title_rus or '') and term not in (title_eng or '')):
            raise ValidationError('Название статьи должно содержать термин.')

        # Проверка на цифры в имени автора
        if author_rus and re.search(r'\d', author_rus):
            raise ValidationError('Имя автора на русском не должно содержать цифры.')
        if author_eng and re.search(r'\d', author_eng):
            raise ValidationError('Имя автора на английском не должно содержать цифры.')

        # Проверка ссылки
        if link:
            try:
                response = requests.get(link, timeout=1)
                if response.status_code != 200:
                    raise ValidationError('Ссылка недоступна.')
            except requests.exceptions.RequestException:
                pass  # Пропускаем проверку, если нет интернета

            allowed_domains = ['elibrary.ru', 'cyberleninka.ru', 'sciencedirect.com', 'openalex.org']
            if not any(domain in link for domain in allowed_domains):
                raise ValidationError('Ссылка должна вести на один из допустимых сайтов: elibrary.ru, cyberleninka.ru, sciencedirect.com, openalex.org.')

        # Валидация идентификатора
        if article_idfr:
            if link and 'elibrary.ru' in link and not re.match(r'^EDN\d+$', article_idfr):
                raise ValidationError('Идентификатор должен быть формата EDN для E-library.')
            elif link and any(domain in link for domain in ['cyberleninka.ru', 'sciencedirect.com', 'openalex.org']) and not re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', article_idfr, re.I):
                raise ValidationError('Идентификатор должен быть формата DOI для Cyberleninka, ScienceDirect или OpenAlex.')

        # Обязательные поля
        required_fields = ['publish_year', 'link', 'usage_context', 'maths', 'article_idfr', 'problems_solution', 'term', 'term_desc', 'interest']
        for field in required_fields:
            if not cleaned_data.get(field):
                raise ValidationError(f'Поле {field} не может быть пустым.')

        # Одно из двух полей обязательно должно быть не пустым
        if not (title_rus or title_eng):
            raise ValidationError('Должно быть заполнено хотя бы одно из полей: Название статьи на русском или Название статьи на английском.')
        if not (author_rus or author_eng):
            raise ValidationError('Должно быть заполнено хотя бы одно из полей: Имя автора на русском или Имя автора на английском.')
        if not (keyword_rus or keyword_eng):
            raise ValidationError('Должно быть заполнено хотя бы одно из полей: Ключевое слово на русском или Ключевое слово на английском.')

        return cleaned_data


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))