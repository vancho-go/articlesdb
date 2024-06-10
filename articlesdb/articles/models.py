from django.db import models

from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    title_rus = models.CharField(max_length=256, null=True, blank=True)
    title_eng = models.CharField(max_length=256, null=True, blank=True)
    author_rus = models.CharField(max_length=256, null=True, blank=True)
    author_eng = models.CharField(max_length=256, null=True, blank=True)
    keyword_rus = models.CharField(max_length=256, null=True, blank=True)
    keyword_eng = models.CharField(max_length=256, null=True, blank=True)
    publish_year = models.IntegerField()
    link = models.URLField(max_length=2083)
    usage_context = models.CharField(max_length=1024)
    maths = models.CharField(max_length=256)
    article_idfr = models.CharField(max_length=256)
    problems_solution = models.CharField(max_length=1024)
    term = models.CharField(max_length=256)
    term_desc = models.CharField(max_length=1024)
    user_ins = models.ForeignKey(User, related_name='ins_articles', on_delete=models.CASCADE)
    user_checker = models.ForeignKey(User, related_name='checker_articles', on_delete=models.CASCADE, null=True, blank=True)
    error_description = models.TextField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    interest = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checked_at = models.DateTimeField(null=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=5, choices=[('admin', 'Admin'), ('user', 'User')])
