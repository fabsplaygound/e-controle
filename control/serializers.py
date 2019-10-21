from django.contrib.auth import get_user_model

from rest_framework import serializers

from utils.serializers import DateTimeFieldWihTZ

from .models import Control, Question, QuestionFile, Questionnaire, ResponseFile, Theme


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Control
        fields = ('id', 'title', 'depositing_organization', 'reference_code')


class ControlUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Control
        fields = ('id', 'title', 'depositing_organization')


class ResponseFileSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    creation_date = DateTimeFieldWihTZ(source='created', format='%a %d %B %Y')
    creation_time = DateTimeFieldWihTZ(source='created', format='%X')

    class Meta:
        model = ResponseFile
        fields = ('id', 'url', 'basename', 'created', 'creation_date', 'creation_time', 'author', 'is_deleted', 'question')


class ResponseFileTrashSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseFile
        fields = ('id', 'is_deleted')


class QuestionFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionFile
        fields = ('id', 'url', 'basename', 'file', 'question')


class QuestionSerializer(serializers.ModelSerializer):
    response_files = ResponseFileSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'description', 'response_files', 'theme')


class ThemeSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Theme
        fields = ('id', 'title', 'questionnaire', 'questions')
        # not serialized : order


class QuestionnaireSerializer(serializers.ModelSerializer):
    themes = ThemeSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True, required=False)

    class Meta:
        model = Questionnaire
        fields = ('id', 'title', 'sent_date', 'end_date', 'description', 'control', 'themes', 'is_draft', 'author',
                  'title_display')
        extra_kwargs = {'control': {'required': True}}
        # not serialized (yet) : file, order


class QuestionUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Question
        fields = ('id', 'description')


class ThemeUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    questions = QuestionUpdateSerializer(many=True, required=False)

    class Meta:
        model = Theme
        fields = ('id', 'title', 'questions')


class QuestionnaireUpdateSerializer(serializers.ModelSerializer):
    themes = ThemeUpdateSerializer(many=True, required=False)

    class Meta:
        model = Questionnaire
        fields = ('id', 'title', 'sent_date', 'end_date', 'description', 'control', 'themes', 'is_draft')
        extra_kwargs = {
            'control': {
                'required': True,
                'allow_null': False,
            }
        }


# Serializers for displaying questionnaire_list.html
class QuestionnaireListUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'id',)


class QuestionnaireListQuestionnaireSerializer(serializers.ModelSerializer):
    author = QuestionnaireListUserSerializer(read_only=True, required=False)

    class Meta:
        model = Questionnaire
        fields = ('id', 'title', 'title_display', 'url', 'is_draft', 'sent_date', 'end_date', 'author_id', 'author')


class QuestionnaireListControlSerializer(serializers.ModelSerializer):
    questionnaires = QuestionnaireListQuestionnaireSerializer(many=True, read_only=True)

    class Meta:
        model = Control
        fields = ('id', 'title', 'depositing_organization', 'reference_code', 'questionnaires')


