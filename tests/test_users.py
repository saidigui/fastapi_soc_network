from jose import jwt
import pytest
from app import schemas
from app.config import settings

def test_root(client):
    response = client.get("/")
    assert response.json() == {"message": "Welcome to my API for Social Network deployment CI/CD test with GitHub Actions ..."}
    assert response.status_code == 200

def test_create_user(client):
    response = client.post("/users/", json={"email": "test@example.com", "password": "pass"})
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "test@example.com"
    assert response.status_code == 201
  
def test_login_user(test_user, client):
    response = client.post("/login", data={"username":  test_user["email"], "password":  test_user["password"]})
    logRes = schemas.Token(**response.json())
    
    payload = jwt.decode(logRes.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert logRes.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize("email, password, status_code",
                         [('a@a.com', 'wrongpass', 403),
                           ('b@b.com', 'wrongpassword', 403),
                         ('wrongemail', 'lplllpass', 403),
                         (None, 'lplllpass', 422)])

def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post("/login", data={"username":  email, "password":  password})
    assert response.status_code == status_code


