from fastapi import FastAPI

from onetimesecret.routes import route


app = FastAPI(title="One Time Secret")
app.include_router(route)


