from pytest import mark

from django.shortcuts import reverse

from rest_framework.test import APIClient

from tests import factories, utils


pytestmark = mark.django_db
client = APIClient()


def test_logged_in_user_can_list_users():
    factories.UserProfileFactory()
    user = factories.UserFactory()
    utils.login(client, user=user)
    url = reverse('api:user-list')
    response = client.get(url)
    assert response.status_code == 200