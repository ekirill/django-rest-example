# Generated by Django 2.0.4 on 2018-04-24 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False, verbose_name='Account ID')),
                ('owner', models.CharField(max_length=200, verbose_name='Account owner ID')),
                ('balance', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Balance')),
                (
                    'currency',
                    models.CharField(
                        choices=[('PHP', 'PHP'), ('USD', 'USD'), ('EUR', 'EUR')],
                        max_length=5, verbose_name='Currency'
                    )
                ),
            ],
            options={
                'verbose_name': 'Account',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'direction',
                    models.CharField(
                        choices=[('incoming', 'incoming'), ('outgoing', 'outgoing')], max_length=64,
                        verbose_name='Payment direction')
                ),
                ('amount', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Amount')),
                (
                    'currency',
                    models.CharField(
                        choices=[('PHP', 'PHP'), ('USD', 'USD'), ('EUR', 'EUR')],
                        max_length=5, verbose_name='Currency'
                    )
                ),
                (
                    'from_account',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='from_payments',
                        to='core.Account', verbose_name='Payment source account'
                    )
                ),
                (
                    'to_account',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='to_payments', to='core.Account', verbose_name='Payment destination account'
                    )
                ),
            ],
            options={
                'verbose_name': 'Payment',
            },
        ),
    ]
