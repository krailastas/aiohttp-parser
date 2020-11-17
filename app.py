import asyncio
import asyncpg
from aiohttp import web
from routes import setup_routes

import aiohttp_cors

from aiojobs.aiohttp import setup
from middlewares.auth import auth_token
import config


async def init_app():
    app = web.Application(middlewares=[auth_token])
    app['pool'] = await asyncpg.create_pool(config.DATABASE['default'])
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })
    setup_routes(app, cors)
    app['config'] = config
    setup(app)
    return app

loop = asyncio.get_event_loop()
app = loop.run_until_complete(init_app())
web.run_app(app)
