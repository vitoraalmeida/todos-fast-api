from fastapi_zero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


# o teste anterior cria o usuário, por isso o teste é bem sucedido
# def test_read_users(client):
#    response = client.get('/users/')
#    assert response.status_code == 200
#    assert response.json() == {
#        'users': [
#            {
#                'username': 'alice',
#                'email': 'alice@example.com',
#                'id': 1,
#            }
#        ]
#    }
def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == 200
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


# usando other_user para simular um usuário indevido tentando
# alterar outro
def test_update_user_unauthorized(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not enough permissions'}


# não faz sentido quando só é possível atualizar um usuário
# quando o usuário atual é o mesmo que será atualizado
# adicionar caso em que um user admin tente atualizar, assim
# podemos chegar no caso em que o usuário não existe
# def test_update_inexistent_user(client, user, token):
#    response = client.put(
#        '/users/2',
#        headers={'Authorization': f'Bearer {token}'},
#        json={
#            'username': 'bob',
#            'email': 'bob@example.com',
#            'password': 'mynewpassword',
#        },
#    )
#
#    assert response.status_code == 404
#    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200
    assert response.json() == {'detail': 'User deleted'}


def test_delete_user_unauthorized(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not enough permissions'}


# não faz sentido quando só é possível deletar um usuário
# quando o usuário atual é o mesmo que será deletado
# adicionar caso em que um user admin tente deletar, assim
# podemos chegar no caso em que o usuário não existe
# def test_delete_inexistent_user(client, user):
#    response = client.delete('/users/2')
#
#    assert response.status_code == 404
#    assert response.json() == {'detail': 'User not found'}
