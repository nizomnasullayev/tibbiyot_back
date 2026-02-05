from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoint.user_router import router as users_router
from app.endpoint.auth_router import router as auth_router
from app.endpoint.carousel_router import router as carousel_router
from app.endpoint.product_router import router as product_router
from app.endpoint.category_router import router as category_router
from app.endpoint.order_router import router as order_router
from fastapi.staticfiles import StaticFiles


# alembic upgrade head

# alembic revision --autogenerate -m "describe change"
# alembic upgrade head


app = FastAPI()


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(carousel_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)