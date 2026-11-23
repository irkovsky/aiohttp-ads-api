from aiohttp import web

class HttpError(Exception):
    def __init__(self, status_code: int, message):
        self.status_code = status_code
        self.message = message
        
        
@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except HttpError as e:
        return web.json_response(
            {"error": e.message},
            status=e.status_code
        )
    except Exception as e:
        return web.json_response(
                    {"error": str(e)},
                    status=500
                )