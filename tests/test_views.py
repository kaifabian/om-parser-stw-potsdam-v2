# -*- encoding: utf-8 -*-
import pytest

from response_util import meal_names
from stw_potsdam import views

# noinspection PyUnresolvedReferences
# pytest fixtures are linked via parameter names of test methods
from stub_api import api_offline, api_online_one_shot


def test_health_check(client):
    response = client.get('/health_check')
    assert response.status_code == 200
    assert response.data == 'OK'


def test_index(client):
    response = client.get('/').json
    canteen_url = response.get('griebnitzsee', None)
    assert canteen_url, 'Known canteen in index response'

    canteen = client.get(canteen_url)
    assert canteen.status_code == 200, 'Canteen URL is reachable'


@pytest.mark.parametrize('url', ['/canteens/spam', '/canteens/spam/meta', '/canteens/spam/menu'])
def test_canteen_not_found(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert "Canteen 'spam' not found" in response.data


@pytest.mark.xfail(strict=True)
def test_canteen_menu_api_unavailable(client, api_offline):
    _request_check_meals(client)


def test_canteen_menu_request(client, api_online_one_shot):
    _request_check_meals(client)


def test_canteen_menu_cached(client, api_online_one_shot):
    _request_check_meals(client)
    _request_check_meals(client)


@pytest.mark.xfail(strict=True)
def test_canteen_menu_second_request_indeed_fails(client, api_online_one_shot):
    _request_check_meals(client)
    views.cache.clear()
    _request_check_meals(client)


def _request_check_meals(client):
    response = client.get('/canteens/griebnitzsee/menu')

    assert response.status_code == 200
    meals = meal_names(response.data)
    assert meals[0] == u"Gefüllter Germknödel \nmit Vanillesauce und Mohnzucker"


@pytest.fixture
def client():
    views.app.config['TESTING'] = True
    return views.app.test_client()


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    views.cache.clear()