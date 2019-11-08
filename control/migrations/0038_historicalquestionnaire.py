# Generated by Django 2.2.5 on 2019-11-08 09:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('control', '0037_update_questionnaire_editor'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalQuestionnaire',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='titre')),
                ('sent_date', models.DateField(blank=True, help_text='Date de transmission du questionnaire', null=True, verbose_name="date d'envoie")),
                ('end_date', models.DateField(blank=True, help_text='Date de réponse souhaitée', null=True, verbose_name='échéance')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('uploaded_file', models.TextField(blank=True, help_text='Si ce fichier est renseigné, il sera proposé au téléchargement.Sinon, un fichier généré automatiquement sera disponible.', max_length=100, null=True, verbose_name='fichier du questionnaire')),
                ('generated_file', models.TextField(blank=True, help_text='Ce fichier est généré automatiquement quand le questionnaire est enregistré.', max_length=100, null=True, verbose_name='fichier du questionnaire généré automatiquement')),
                ('order', models.PositiveIntegerField(db_index=True, verbose_name='order')),
                ('is_draft', models.BooleanField(default=False, help_text='Ce questionnaire est-il encore au stade de brouillon?', verbose_name='brouillon')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('control', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='control.Control', verbose_name='controle')),
                ('editor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Questionnaire',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
