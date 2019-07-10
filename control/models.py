import os
import re

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from django_cleanup import cleanup
from docxtpl import DocxTemplate
from model_utils.models import TimeStampedModel
from ordered_model.models import OrderedModel


from .upload_path import questionnaire_file_path, question_file_path, response_file_path


class WithNumberingMixin(object):
    """
    Add an helper method for getting the numbering base on the order field.
    """

    @property
    def numbering(self):
        return self.order + 1
    numbering.fget.short_description = 'Numérotation'


class Control(models.Model):
    title = models.CharField("title", max_length=255)
    reference_code = models.CharField(
        verbose_name="code de référence", max_length=255, blank=True,
        help_text='Ce code est utilisé notamment pour le dossier de stockage des réponses')

    class Meta:
        verbose_name = "Controle"
        verbose_name_plural = "Controles"

    def __str__(self):
        return self.title

    def data(self):
        return {
            'id': self.id,
            'title': self.title,
        }

    @property
    def next_questionnaire_numbering(self):
        if not self.questionnaires.exists():
            return 1
        return self.questionnaires.last().numbering + 1


class Questionnaire(OrderedModel, WithNumberingMixin):
    title = models.CharField("titre", max_length=255)
    sent_date = models.DateField(
        verbose_name="date d'envoie", blank=True, null=True,
        help_text="Date de transmission du questionnaire")
    end_date = models.DateField(
        verbose_name="échéance", blank=True, null=True,
        help_text="Date de réponse souhaitée")
    description = models.TextField("description", blank=True)
    file = models.FileField(
        verbose_name="fichier", upload_to=questionnaire_file_path, null=True, blank=True,
        help_text=(
            "Si ce fichier est renseigné, il sera proposé au téléchargement."
            "Sinon, un fichier généré automatiquement sera disponible."))
    generated_file = models.FileField(
        verbose_name="fichier généré automatiquement", upload_to=questionnaire_file_path,
        null=True, blank=True,
        help_text=(
            "Ce fichier est généré automatiquement quand le questionnaire est enregistré."))
    control = models.ForeignKey(
        to='Control', verbose_name='controle', related_name='questionnaires',
        null=True, blank=True, on_delete=models.CASCADE)
    order_with_respect_to = 'control'
    order = models.PositiveIntegerField('order', db_index=True)
    is_draft = models.BooleanField(
        verbose_name="brouillon", default=False,
        help_text="Ce questionnaire est-il encore au stade de brouillon?")

    class Meta:
        ordering = ('control', 'order')
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaires"

    @property
    def url(self):
        return reverse('questionnaire-detail', args=[self.id])

    @property
    def file_url(self):
        return reverse('questionnaire-doc', args=[self.id])

    @property
    def basename(self):
        """
        Name of file, without path.
        """
        return os.path.basename(self.file.name)

    @property
    def title_display(self):
        return f"Questionnaire n°{self.numbering} - {self.title}"

    def __str__(self):
        return self.title_display

    def save(self, *args, **kwargs):
        doc = DocxTemplate("templates/ecc/questionnaire.docx")
        questionnaire = self
        context = {'questionnaire': questionnaire}
        doc.render(context)
        filename = f'{slugify(questionnaire.title)}.docx'
        # Why do we need both relative and absolte path?
        # For django's FileField, we need a relative path from the root of the MEDIA_ROOT.
        # For saving the file via DocxTemplate, we need to absolute path.
        relative_path = questionnaire_file_path(questionnaire, filename)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        doc.save(absolute_path)
        self.generated_file = relative_path
        super().save(*args, **kwargs)


class Theme(OrderedModel, WithNumberingMixin):
    title = models.CharField("titre", max_length=255)
    questionnaire = models.ForeignKey(
        to='Questionnaire', verbose_name='questionnaire', related_name='themes',
        null=True, blank=True, on_delete=models.CASCADE)
    order_with_respect_to = 'questionnaire'

    class Meta:
        ordering = ('questionnaire', 'order')
        verbose_name = "Thème"
        verbose_name_plural = "Thèmes"

    def __str__(self):
        return self.title


class Question(OrderedModel, WithNumberingMixin):
    description = models.TextField("description")
    theme = models.ForeignKey(
        'theme', verbose_name='thème', related_name='questions',
        null=True, blank=True, on_delete=models.CASCADE)
    order_with_respect_to = 'theme'

    class Meta:
        ordering = ('theme', 'order')
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.description


class QuestionFile(OrderedModel):
    question = models.ForeignKey(
        to='Question', verbose_name='question', related_name='question_files',
        on_delete=models.CASCADE)
    file = models.FileField(verbose_name="fichier", upload_to=question_file_path)
    order_with_respect_to = 'question'

    class Meta:
        ordering = ('question', 'order')
        verbose_name = 'Question: Fichier Attaché'
        verbose_name_plural = 'Question: Fichiers Attachés'

    @property
    def url(self):
        return reverse('send-question-file', args=[self.id])

    @property
    def basename(self):
        """
        Name of file, without path.
        """
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.file.name


@cleanup.ignore
class ResponseFile(TimeStampedModel):
    question = models.ForeignKey(
        to='Question', verbose_name='question', related_name='response_files',
        on_delete=models.CASCADE)
    file = models.FileField(verbose_name="fichier", upload_to=response_file_path)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='response_files', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Réponse: Fichier Attaché'
        verbose_name_plural = 'Réponse: Fichiers Attachés'

    @property
    def url(self):
        return reverse('send-response-file', args=[self.id])

    def strip_prefix(self, basename):
        """
        Remove the suffix found in filename 'Q01-T02-01-'.
        """
        return re.sub(r'Q\d+-T\d+-\d+-', '', basename)

    @property
    def basename(self):
        """
        Name of file, without path and without name prefix.
        """
        basename = os.path.basename(self.file.name)
        return self.strip_prefix(basename)

    def __str__(self):
        return self.file.name
