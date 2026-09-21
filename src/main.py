from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.LLMProviderFactory import LLMProviderFactory


app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()

    # MongoDB
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]

    # LLM Provider Factory
    app.state.llm_provider_factory = LLMProviderFactory(settings)

    # Generation client
    app.state.generation_client = (
        app.state.llm_provider_factory.create(
            provider=settings.GENERATION_BACKEND
        )
    )

    app.state.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID
    )

    # Embedding client
    app.state.embedding_client = (
        app.state.llm_provider_factory.create(
            provider=settings.EMBEDDING_BACKEND
        )
    )

    app.state.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )


@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_conn.close()


app.include_router(base.base_router)
app.include_router(data.data_router)