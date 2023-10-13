from sqlalchemy import select

from fastapi_zero.models import Todo, User


def test_create_user(session):
    new_user = User(username='alice', password='secret', email='teste@teste')
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user.username == 'alice'


def test_create_todo(session, user):
    todo = Todo(
        title='Test todo',
        description='Test desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    user = session.scalar(select(User).where(User.id == user.id))

    assert todo in user.todos
