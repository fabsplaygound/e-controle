from actstream.models import Action
from django.shortcuts import reverse
from pytest import mark
from rest_framework.test import APIClient

from control.models import ResponseFile
from tests import factories, utils


pytestmark = mark.django_db
client = APIClient()


def get_response_file(user, id):
    return utils.get_resource(client, user, 'response-file', id)


def trash_response_file(user, id, payload):
    utils.login(client, user=user)
    url = reverse('response-file-trash', args=[id])
    response = client.put(url, payload)
    return response


########## get

def test_can_get_response_file_if_control_is_associated_with_the_user():
    response_file = factories.ResponseFileFactory()
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)

    response = get_response_file(user, response_file.id)

    assert response.status_code == 200


def test_cannot_get_response_file_if_control_is_not_associated_with_the_user():
    response_file = factories.ResponseFileFactory()
    control = factories.ControlFactory()
    user = utils.make_audited_user(control)

    response = get_response_file(user, response_file.id)

    assert 400 <= response.status_code <= 499


def test_cannot_get_response_file_if_user_not_logged_in():
    response_file = factories.ResponseFileFactory()
    response = utils.get_resource_without_login(client, 'response-file', response_file.id)
    assert response.status_code == 403


########## write methods

def run_test_response_file_api_is_readonly(user, response_file):
    payload = {"id": response_file.id}
    utils.login(client, user=user)

    # no create
    response = utils.create_resource_without_login(client, 'response-file', payload)
    assert response.status_code == 405  # method not allowed

    # no update
    response = utils.update_resource_without_login(client, 'response-file', payload)
    assert response.status_code == 405  # method not allowed

    # no patch
    url = reverse('api:response-file-detail', args=[payload['id']])
    response = client.patch(url, payload, format='json')
    assert response.status_code == 405  # method not allowed


def test_response_file_api_is_readonly_for_audited():
    response_file = factories.ResponseFileFactory()
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    run_test_response_file_api_is_readonly(user, response_file)


def test_response_file_api_is_readonly_for_inspector():
    response_file = factories.ResponseFileFactory()
    user = utils.make_inspector_user(response_file.question.theme.questionnaire.control)
    run_test_response_file_api_is_readonly(user, response_file)


########## trash

def test_cannot_trash_response_file_if_user_not_logged_in():
    response_file = factories.ResponseFileFactory()
    url = reverse('response-file-trash', args=[response_file.id])
    response = client.get(url)
    assert response.status_code == 403


def test_cannot_trash_response_file_if_control_is_not_associated_with_the_user():
    response_file = factories.ResponseFileFactory()
    control = factories.ControlFactory()
    user = utils.make_audited_user(control)
    payload = { "is_deleted": "true" }

    response = trash_response_file(user, response_file.id, payload)

    assert 400 <= response.status_code <= 499


def test_can_trash_response_file_if_control_is_associated_with_the_user():
    response_file = factories.ResponseFileFactory()
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    payload = { "is_deleted": "true" }
    count_before = ResponseFile.objects.count()
    assert not ResponseFile.objects.get(id=response_file.id).is_deleted

    response = trash_response_file(user, response_file.id, payload)

    assert response.status_code == 200
    count_after = ResponseFile.objects.count()
    assert count_before == count_after
    assert ResponseFile.objects.get(id=response_file.id).is_deleted


def test_trashing_logs_an_action():
    response_file = factories.ResponseFileFactory()
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    payload = { "is_deleted": "true" }
    assert not Action.objects.filter(verb__contains="trashed response-file").exists()
    trash_response_file(user, response_file.id, payload)
    assert Action.objects.filter(verb__contains="trashed response-file").exists()
    action = Action.objects.filter(verb__contains="trashed response-file").last()
    assert action.actor_object_id == str(user.id)
    assert action.target_object_id == str(response_file.id)


def test_trashing_moves_the_file_on_disk():
    response_file = factories.ResponseFileFactory()
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    payload = { "is_deleted": "true" }

    path_before = response_file.file.path
    assert 'CORBEILLE' not in path_before

    trash_response_file(user, response_file.id, payload)

    path_after = ResponseFile.objects.get(id=response_file.id).file.path
    assert path_after != path_before
    assert 'CORBEILLE' in path_after


def test_trashing_keeps_the_same_basename():
    response_file = factories.ResponseFileFactory()
    basename_before = response_file.basename
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    payload = { "is_deleted": "true" }

    trash_response_file(user, response_file.id, payload)

    basename_after = ResponseFile.objects.get(id=response_file.id).basename
    assert basename_after == basename_before


def test_cannot_retrash_a_trashed_file():
    response_file = factories.ResponseFileFactory(is_deleted=True)
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    payload = { "is_deleted": "true" }

    response = trash_response_file(user, response_file.id, payload)

    assert 400 <= response.status_code < 500
    assert ResponseFile.objects.get(id=response_file.id).is_deleted


def test_cannot_untrash_a_file():
    response_file = factories.ResponseFileFactory(is_deleted=True)
    user = utils.make_audited_user(response_file.question.theme.questionnaire.control)
    payload = { "is_deleted": "false" }

    response = trash_response_file(user, response_file.id, payload)

    assert 400 <= response.status_code < 500
    assert ResponseFile.objects.get(id=response_file.id).is_deleted
