from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    '''Global error handling middleware'''
    try:
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={'error': e.detail}
        )
    except Exception as e:
        logger.error(f'Unhandled exception: {str(e)}')
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={'error': 'Internal server error'}
        )
