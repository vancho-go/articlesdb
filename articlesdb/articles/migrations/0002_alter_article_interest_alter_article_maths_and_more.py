# Generated by Django 5.0.6 on 2024-06-08 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='interest',
            field=models.CharField(default='Unknown', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='maths',
            field=models.CharField(default='Unknown', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='problems_solution',
            field=models.CharField(default='Unknown', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='term_desc',
            field=models.CharField(default='Unknown', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='usage_context',
            field=models.CharField(default='Unknown', max_length=1024),
            preserve_default=False,
        ),
    ]
