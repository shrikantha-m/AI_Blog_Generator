# Generated by Django 5.0.4 on 2024-04-15 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog_Generator', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='youtube_link',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='youtube_title',
            field=models.CharField(max_length=300),
        ),
    ]
