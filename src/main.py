
from dotenv import load_dotenv
from fastapi import FastAPI

from src.core.libs.mailing.template_factory import TemplateFactory

from .modules import load_routers
from .core.db import get_db


app = FastAPI()


@app.on_event("startup")
async def startup_db():
    await get_db()
    TemplateFactory.on_load_templates()


routers = load_routers()
for router in routers:

    app.include_router(router)


load_dotenv()
