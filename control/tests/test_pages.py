from pytest import mark

from django.shortcuts import reverse

from tests import factories, utils


pytestmark = mark.django_db


def test_download_file_works_if_the_control_is_associated_with_the_user(client):
    response_file = factories.ResponseFileFactory()
    user = response_file.author
    user.profile.control = response_file.question.theme.questionnaire.control
    user.profile.save()
    utils.login(client, user=response_file.author)
    url = reverse('send-response-file', args=[response_file.id])
    response = client.get(url)
    assert response.status_code == 200


def test_download_file_fails_if_the_control_is_not_associated_with_the_user(client):
    response_file = factories.ResponseFileFactory()
    user = response_file.author
    unautorized_control = factories.ControlFactory()
    assert unautorized_control != response_file.question.theme.questionnaire.control
    user.profile.control = unautorized_control
    user.profile.save()
    utils.login(client, user=response_file.author)
    url = reverse('send-response-file', args=[response_file.id])
    response = client.get(url)
    assert response.status_code != 200
