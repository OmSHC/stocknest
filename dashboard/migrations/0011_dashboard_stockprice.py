from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_watchlistcolumn_watchlistdisplaysettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardStockPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('open_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('high_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('low_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('close_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('volume', models.BigIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dashboard_stockprice',
                'ordering': ['-date'],
                'indexes': [
                    models.Index(fields=['symbol', 'date'], name='dashboard_s_symbol_date_idx'),
                    models.Index(fields=['date'], name='dashboard_s_date_idx'),
                ],
                'unique_together': {('symbol', 'date')},
            },
        ),
    ] 