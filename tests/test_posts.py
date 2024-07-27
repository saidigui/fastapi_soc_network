from typing import List
from app import schemas
import pytest


def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")

    def validate(post):
        return schemas.PostOut(**post)
    posts_map = map(validate, response.json())
    posts_list = list(posts_map)

    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200


def test_unauthorized_user_get_all_posts(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == 401

def test_unauthorized_user_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_get_one_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/2004")
    assert response.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**response.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert response.status_code == 200

@pytest.mark.parametrize("title, content, published", [
    ("awesome 1 title", "awesome 1 content", True),
    ("awesome 2 title", "awesome 2 content", False),
    ("awesome 3 title", "awesome 3 content", True),
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    response = authorized_client.post("/posts/", 
                                      json={"title": title, "content": content, "published": published})
    created_post = schemas.Post(**response.json())
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']
    assert response.status_code == 201

def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    response = authorized_client.post("/posts/", 
                                      json={"title": "arbitrary title" , "content": "arbitrary content"})
    created_post = schemas.Post(**response.json())
    assert created_post.title == "arbitrary title"
    assert created_post.content == "arbitrary content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']
    assert response.status_code == 201

def test_unauthorized_user_create_post(client, test_user, test_posts):
    response = client.post("/posts/", json={"title": "arbitrary title" , "content": "arbitrary content"})
    assert response.status_code == 401

def test_unauthorized_user_delete_post(client, test_user, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_delete_post_success(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204

def test_delete_post_not_exist(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/8000")
    assert response.status_code == 404

def test_delete_other_user_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403

def test_update_post(authorized_client, test_user, test_posts):
    data = {"title": "updated title", "content": "updated content", "id": test_posts[0].id}
    response = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.Post(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_user, test_user_bis, test_posts):
    data = {"title": "updated title", "content": "updated content", "id": test_posts[3].id}
    response = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert response.status_code == 403

def test_unauthorized_user_update_post(client, test_user, test_posts):
    response = client.put(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_update_post_not_exist(authorized_client, test_user, test_posts):
    data = {"title": "updated title", "content": "updated content", "id": test_posts[3].id}
    response = authorized_client.put(f"/posts/8000", json=data)
    assert response.status_code == 404