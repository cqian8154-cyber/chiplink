from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from database import init_db
from routers import products, inquiries, orders, inventory, cart, alt

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="芯链商城 ChipLink",
    description="芯片贸易 B2B/B2C 电商平台",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(products.router,   prefix="/api/products",   tags=["产品"])
app.include_router(inquiries.router,  prefix="/api/inquiries",  tags=["询价"])
app.include_router(orders.router,     prefix="/api/orders",     tags=["订单"])
app.include_router(inventory.router,  prefix="/api/inventory",  tags=["库存"])
app.include_router(cart.router,       prefix="/api/cart",       tags=["购物车"])
app.include_router(alt.router,        prefix="/api/alt",        tags=["国产替代"])

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
