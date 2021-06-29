# Generated by Django 3.2 on 2021-06-29 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_alter_user_home_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='home_address',
            field=models.CharField(blank=True, help_text="<ul>\n                  <li>Address for receiving the Polar fitness tracker. It can be any address within Finland where you would like to receive the fitness tracker. (Don't fill if you already have one.)</li>\n                  <li>The size of the fitness tracker is M/L, which means wrist circumference 155–210 mm.</li>\n                  </ul>", max_length=50, verbose_name='home address'),
        ),
    ]
