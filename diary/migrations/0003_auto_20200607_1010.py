# Generated by Django 3.0.7 on 2020-06-07 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0002_hero_last_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='location',
            field=models.IntegerField(choices=[(1, 'Town'), (2, 'In road to Killing fields'), (3, 'Killing fields'), (4, 'In road to Town')], default=1),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipments', to='diary.Hero'),
        ),
        migrations.AlterField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='diary.Hero'),
        ),
    ]
