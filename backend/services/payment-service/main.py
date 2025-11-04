from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from shared.config.settings import settings
from shared.utils.database import init_db
from shared.middleware.error_handler import error_handler_middleware
from .routes import router

app = FastAPI(
    title='Chariot Payment Service',
    version='1.0.0',
    description='Payment processing with USDT and Paystack integration'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.middleware('http')(error_handler_middleware)
app.include_router(router)

@app.on_event('startup')
async def startup():
    init_db()

@app.get('/health')
async def health():
    return {'status': 'healthy', 'service': 'payment'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8005)
