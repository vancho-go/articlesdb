import datetime
import spacy
from nltk.stem import WordNetLemmatizer
import nltk
from django import forms
from .models import Article
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
import requests
import os

# required_fields = ['publish_year', 'link', 'usage_context', 'maths', 'article_idfr', 'problems_solution', 'term', 'term_desc', 'interest']
# python -m spacy download ru_core_news_sm
# python -m spacy download en_core_web_sm

# Установка пути для данных nltk
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

nltk.download('wordnet', download_dir=os.path.join(os.path.dirname(__file__), 'nltk_data'))
nltk.download('averaged_perceptron_tagger', download_dir=os.path.join(os.path.dirname(__file__), 'nltk_data'))

nlp_ru = spacy.load("ru_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()

TERM_CHOICES = [
    ('Цифровая трансформация', 'Цифровая трансформация'),
    ('Трансфер цифровой технологии', 'Трансфер цифровой технологии'),
    ('Цифровая технология', 'Цифровая технология'),
    ('Сквозная цифровая технология', 'Сквозная цифровая технология'),
    ('Прорывная технология', 'Прорывная технология'),
    ('Технология ближайшего будущего', 'Технология ближайшего будущего'),
    ('Постепенно внедряемая технология', 'Постепенно внедряемая технология'),
    ('Digital transformation', 'Digital transformation'),
    ('Transfer of digital technology', 'Transfer of digital technology'),
    ('Digital technology', 'Digital technology'),
    ('End-to-end digital technology', 'End-to-end digital technology'),
    ('Breakthrough technology', 'Breakthrough technology'),
    ('Near future technology', 'Near future technology'),
    ('Gradually introduced technology', 'Gradually introduced technology'),
]


def lemmatize_russian(text):
    doc = nlp_ru(text)
    lemmas = [token.lemma_ for token in doc]
    return ' '.join(lemmas)


def lemmatize_english(text):
    doc = nlp_en(text)
    lemmas = [token.lemma_ for token in doc]
    return ' '.join(lemmas)


class SearchForm(forms.Form):
    term = forms.ChoiceField(choices=TERM_CHOICES, required=False, label='Термин')
    title = forms.CharField(required=False, label='Название статьи')
    author = forms.CharField(required=False, label='Автор')
    year = forms.IntegerField(required=False, label='Год публикации')


class ArticleForm(forms.ModelForm):
    term = forms.ChoiceField(choices=TERM_CHOICES, label='Термин')

    class Meta:
        model = Article
        exclude = ['user_ins', 'user_checker', 'checked_at']
        labels = {
            'title_rus': 'Название статьи (на русском)',
            'title_eng': 'Название статьи (на английском)',
            'author_rus': 'Автор (на русском)',
            'author_eng': 'Автор (на английском)',
            'keyword_rus': 'Ключевое слово (на русском)',
            'keyword_eng': 'Ключевое слово (на английском)',
            'publish_year': 'Год публикации',
            'link': 'Ссылка на источник',
            'usage_context': 'Контекст использования',
            'maths': 'Математический аппарат',
            'article_idfr': 'Идентификатор статьи',
            'problems_solution': 'Решение задачи',
            'term_desc': 'Описание термина',
            'error_description': 'Описание ошибки',
            'resolved': 'Ошибка решена',
            'interest': 'В чьих интересах',
            'created_at': 'Дата создания',
            'updated_at': 'Дата обновления'
        }

    def clean_publish_year(self):
        publish_year = self.cleaned_data.get('publish_year')
        current_year = datetime.datetime.now().year
        if not (1000 <= publish_year <= current_year):
            raise ValidationError('Введите корректный год публикации.')
        return publish_year

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

        # Лемматизация названия статьи и термина
        title_rus_lemmas = lemmatize_russian(title_rus) if title_rus else ""
        title_eng_lemmas = lemmatize_english(title_eng) if title_eng else ""
        term_lemmas = lemmatize_russian(term) if any(char.isalpha() for char in term) else lemmatize_english(term)

        # Название статьи должно содержать термин
        if term and not (term_lemmas in title_rus_lemmas or term_lemmas in title_eng_lemmas):
            raise ValidationError(f'Название статьи должно содержать термин "{term}".')

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