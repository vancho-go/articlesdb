from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserLoginForm, SearchForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from .forms import ArticleForm
from .models import Article
from django.contrib import messages
import datetime


@login_required
def article_list(request):
    form = SearchForm(request.GET)
    articles = Article.objects.all()

    if form.is_valid():
        term = form.cleaned_data.get('term')
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        year = form.cleaned_data.get('year')

        if term:
            articles = articles.filter(Q(term=term))
        if title:
            articles = articles.filter(Q(title_rus__icontains=title) | Q(title_eng__icontains=title))
        if author:
            articles = articles.filter(Q(author_rus__icontains=author) | Q(author_eng__icontains=author))
        if year:
            articles = articles.filter(publish_year=year)

    duplicate_ids = Article.objects.values('article_idfr').annotate(id_count=Count('article_idfr')).filter(
        id_count__gt=1)
    duplicate_ids = [item['article_idfr'] for item in duplicate_ids]

    return render(request, 'articles/article_list.html',
                  {'articles': articles, 'duplicate_ids': duplicate_ids, 'form': form})


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            if request.user.is_authenticated:
                article.user_ins = request.user
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'articles/article_form.html', {'form': form})

@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Проверка прав на редактирование
    if not request.user.is_superuser:
        if article.user_ins != request.user or not article.error_description or article.resolved:
            return redirect('article_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if form.cleaned_data.get('resolved'):
                article.error_description = ''
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'articles/article_form.html', {'form': form})


@login_required
def add_error_description(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Проверка прав на добавление ошибки
    if not request.user.is_superuser and article.user_ins == request.user:
        return redirect('article_list')

    if request.method == 'POST':
        error_description = request.POST.get('error_description')
        if error_description:
            article.error_description = error_description
            article.user_checker = request.user
            article.resolved = False
            article.checked_at = datetime.datetime.now()
            article.save()
            return redirect('article_list')
    return render(request, 'articles/add_error_description.html', {'article': article})



@user_passes_test(lambda u: u.is_superuser)
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        return redirect('article_list')
    return render(request, 'articles/article_confirm_delete.html', {'article': article})


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'articles/article_detail.html', {'article': article})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('article_list')
    else:
        form = UserRegisterForm()
    return render(request, 'articles/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('article_list')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'articles/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')
