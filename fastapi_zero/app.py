from fastapi import FastAPI

from fastapi_zero.routers import auth, todos, users

app = FastAPI()

# inclui as rotas especificar para cada caso de uso
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/')
def read_root():
    return {'message': 'Olá Mundo!'}
