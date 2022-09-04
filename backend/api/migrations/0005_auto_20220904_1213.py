# Generated by Django 2.2.16 on 2022-09-04 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20220904_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=10, verbose_name='Ед.измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=20, unique=True, verbose_name='Имя ингредиента'),
        ),
    ]
