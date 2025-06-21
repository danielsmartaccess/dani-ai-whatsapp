from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('oraculo', '0003_create_whatsapp_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstagioFunil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('ordem', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Contato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('telefone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, null=True)),
                ('tags', models.CharField(max_length=255, blank=True)),
                ('ultima_interacao', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='ativo', max_length=50)),
                ('estagio_funil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='oraculo.estagiofunil')),
            ],
        ),
        migrations.CreateModel(
            name='Campanha',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True)),
                ('data_inicio', models.DateTimeField()),
                ('status', models.CharField(default='ativa', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SequenciaMensagem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.IntegerField()),
                ('conteudo', models.TextField()),
                ('atraso', models.DurationField(help_text='Atraso após mensagem anterior')),
                ('condicao_envio', models.JSONField(blank=True, default=dict)),
                ('campanha', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oraculo.campanha')),
            ],
        ),
    ]
