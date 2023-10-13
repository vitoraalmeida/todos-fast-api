import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import Base, User
from fastapi_zero.security import get_password_hash


class UserFactory(factory.Factory):
    # classe para configurar a fabrica
    class Meta:
        # especifica para qual modelo a fabrica vai criar objetos
        model = User   # modelo de banco de dados

    # sequencia de id que são incrementados a cada chamada da fabrica
    id = factory.Sequence(lambda n: n)
    username = factory.LazyAttribute(lambda obj: f'test{obj.id}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = ''


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    # instancia o driver do banco de dados sqlite
    engine = create_engine(
        'sqlite:///:memory:',
        # permite compartilhar a conexão com o banco entre
        # diferentes threads sem gerar erro
        connect_args={'check_same_thread': False},
        # reutiliza a mesma conexão para todas as solicitações
        poolclass=StaticPool,
    )
    # cria as tabelas registradas no banco de testes
    Base.metadata.create_all(engine)
    # Cria uma fabrica de sessões com o banco
    Session = sessionmaker(bind=engine)
    # Injeta a sessão no teste que solicita a fixture
    yield Session()
    # após o fim de cada teste, elimina todos os dados e
    # tabelas criadas durante os testes
    Base.metadata.drop_all(engine)


# fixture para criar um usuário a fim de podermos testar o caso
# em que fazemos o get na aplicação contendo um usuário já registrado
@pytest.fixture
def user(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user


# fixture para criar um usuário a mais no sistema para testar
# contextos de ação com mais usuários
@pytest.fixture
def other_user(session):
    user = UserFactory()

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = 'testtest'

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']
