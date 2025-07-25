# Generated by Django 3.2 on 2025-05-21 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Valor', '0001_initial'),
        ('Mes', '0001_initial'),
        ('Anio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoArticulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articulo', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TipoPrecio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='VentaParticipacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acumulado_total', models.CharField(max_length=200)),
                ('participacion_total', models.CharField(max_length=200)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Anio.anio')),
                ('mes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Mes.mes')),
                ('tipoPrecio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Supermercado.tipoprecio')),
                ('valor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Valor.valor')),
            ],
        ),
        migrations.CreateModel(
            name='VentaArticulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.CharField(max_length=200)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Anio.anio')),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Supermercado.tipoarticulo')),
                ('mes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Mes.mes')),
                ('tipoPrecio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Supermercado.tipoprecio')),
                ('valor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Valor.valor')),
            ],
        ),
        migrations.CreateModel(
            name='Variacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variacion_interanual', models.CharField(max_length=200)),
                ('variacion_intermensual', models.CharField(max_length=200)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Anio.anio')),
                ('mes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Mes.mes')),
                ('tipoPrecio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Supermercado.tipoprecio')),
                ('valor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Valor.valor')),
            ],
        ),
        migrations.CreateModel(
            name='Total',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('venta_total', models.CharField(max_length=200)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Anio.anio')),
                ('mes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Mes.mes')),
                ('tipoPrecio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Supermercado.tipoprecio')),
                ('valor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Valor.valor')),
            ],
        ),
        migrations.CreateModel(
            name='Indicadores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_operaciones', models.CharField(max_length=200)),
                ('variacion_interanual', models.CharField(max_length=200)),
                ('variacion_intermensual', models.CharField(max_length=200)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Anio.anio')),
                ('mes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Mes.mes')),
                ('valor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='Valor.valor')),
            ],
        ),
    ]
