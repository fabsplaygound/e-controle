# Generated by Django 2.1.9 on 2019-07-16 07:42

from django.db import migrations, models


def set_unique_reference_code(apps, schema_editor):
    Control = apps.get_model('control', 'Control')
    for control in Control.objects.all():
        if not control.reference_code:
            control.reference_code = f'2019_CONTROLE_{control.id}'
            control.save()


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0030_auto_20190715_1545'),
    ]

    operations = [
        migrations.RunPython(
            set_unique_reference_code,
            reverse_code=lambda apps, schema_editor: None
        ),
        migrations.AlterField(
            model_name='control',
            name='reference_code',
            field=models.CharField(blank=True, help_text='Ce code est utilisé notamment pour le dossier de stockage des réponses', max_length=255, unique=True, verbose_name='code de référence'),
        ),
    ]
