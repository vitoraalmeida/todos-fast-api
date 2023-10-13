from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import Message, UserList, UserPublic, UserSchema
from fastapi_zero.security import get_current_user, get_password_hash

# para casos sem banco de dados
# database = []

# Anotação de tipos. Facilita declaração da função e o fastapi continua
# conseguindo detectar que é injeção de dependência.
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', response_model=UserPublic, status_code=201)
def create_user(user: UserSchema, session: Session):
    # verifica se já há um usuário igual
    db_user = session.scalar(select(User).where(User.email == user.email))
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get('/', response_model=UserList)
def read_users(session: Session, skip: int = 0, limit: int = 100):
    # offset = permite pular um numero específico de registros
    # limit = máximo de registros a serem retornados
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    # obriga que um token valido seja passado
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(status_code=401, detail='Not enough permissions')

    current_user.username = user.username
    current_user.password = user.password
    current_user.email = user.email
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session, current_user: CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(status_code=401, detail='Not enough permissions')

    session.delete(current_user)
    session.commit()

    return {'detail': 'User deleted'}


# in memory

# @app.get('/users/', status_code=200, response_model=UserList)
# def read_users():
#    return {'users': database}

# @app.put('/users/{user_id}', response_model=UserPublic)
# def update_user(user_id: int, user: UserSchema):
#    if user_id > len(database) or user_id < 1:
#        raise HTTPException(status_code=404, detail='User not found')
#    user_with_id = UserDB(**user.model_dump(), id=user_id)
#    database[user_id - 1] = user_with_id
#
#    return user_with_id

# @app.delete('/users/{user_id}', response_model=Message)
# def delete_user(user_id: int):
#    if user_id > len(database) or user_id < 1:
#        raise HTTPException(status_code=404, detail='User not found')
#    del database[user_id - 1]
#    return {'detail': 'User deleted'}


# @app.post('/users/', status_code=201, response_model=UserPublic)
# def create_user(user: UserSchema, session: Session = Depends(get_session):
# Cria a instância de um UserDB
# **user.model_dump() desestrutura o valor do dicionário retornado pelo
# model_dump() representando o objeto
# Assim o objeto é criado reaproveitando o modelo User
# que o userdb herda
# user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
# database.append(user_with_id)
# return user_with_id
