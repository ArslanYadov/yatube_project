# Generated by Django 2.2.19 on 2022-06-13 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20220613_2138'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['created'], 'verbose_name': 'Подписку', 'verbose_name_plural': 'Подписки'},
        ),
    ]