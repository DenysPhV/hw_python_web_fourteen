from unittest.mock import MagicMock, patch

from pytest import mark, fixture

from src.database.models import User
from src.services.auth import auth_service
from fastapi import status


@fixture(scope='function')
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@mark.usefixtures('mock_rate_limit')
def test_create_contact(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            json={"first_name": "John", "last_name": "Dow", "email": "user@example.com", "phone": "2877064128",
                  "birthday": "2023-04-23T15:28:13.286Z"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Dow"
        assert data["email"] == "user@example.com"
        assert data["id"] == 1
        assert "id" in data


@mark.usefixtures('mock_rate_limit')
def test_get_contacts_without_token(client):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.usefixtures('mock_rate_limit')
def test_get_contacts_with_token(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK


@mark.usefixtures('mock_rate_limit')
def test_get_one(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/1", headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Dow"
        assert data["email"] == "user@example.com"
        assert "id" in data


@mark.usefixtures('mock_rate_limit')
def test_get_one_error(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/100", headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"


@mark.usefixtures('mock_rate_limit')
def test_find_by_name(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/name/John', headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Dow"
        assert data["email"] == "user@example.com"


@mark.usefixtures('mock_rate_limit')
def test_find_by_name_error(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/name/Joe', headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"


@mark.usefixtures('mock_rate_limit')
def test_find_by_lastname(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/lastname/Dow', headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["last_name"] == "Dow"


@mark.usefixtures('mock_rate_limit')
def test_find_by_lastname_error(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/lastname/TEST', headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"


@mark.usefixtures('mock_rate_limit')
def test_find_by_email(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/email/user@example.com',
                              headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user@example.com"


@mark.usefixtures('mock_rate_limit')
def test_find_by_email_error(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/email/kuku@kuuu.com', headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"


@mark.usefixtures('mock_rate_limit')
def test_get_all(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.get('/api/contacts/find/birthday', headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK


@mark.usefixtures('mock_rate_limit')
def test_update(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.put("/api/contacts/1",
                              json={"first_name": "Pater", "last_name": "Dow", "email": "user@example.com",
                                    "phone": "2877064128", "birthday": "2023-04-23T15:28:13.286Z"},
                              headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Pater"


@mark.usefixtures('mock_rate_limit')
def test_update_error(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.put("/api/contacts/100",
                              json={"first_name": "Pater", "last_name": "Dow", "email": "user@example.com",
                                    "phone": "2877064128", "birthday": "2023-04-23T15:28:13.286Z"},
                              headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"


@mark.usefixtures('mock_rate_limit')
def test_delete(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.delete("/api/contacts/1", headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@mark.usefixtures('mock_rate_limit')
def test_delete_error(client, token):
    with patch.object(auth_service, 'redis_db') as r_mock:
        r_mock.get.return_value = None
        response = client.delete("/api/contacts/100", headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Not found"

