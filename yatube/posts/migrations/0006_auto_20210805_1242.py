# Generated by Django 2.2.6 on 2021-08-05 09:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follow_text', to='posts.Post'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Избранный автор'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='uniq_follow'),
        ),
    ]
