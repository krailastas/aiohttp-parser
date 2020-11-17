from aiohttp import web


@web.middleware
async def auth_token(request, handler):
    auth_header = request.headers.get('Authorization')
    auth = auth_header.split(' ') if auth_header else []

    if request.method == "OPTIONS" and 'Authorization' not in request.headers:
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'PATCH, PUT, GET, POST, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Authorization, content-language, X-CSRFToken, Accept, Origin, X-Requested-With, X-File-Name, Content-Type, Cache-Control'
        }
        return web.Response(headers=headers)

    if len(auth) == 2 and auth[0].lower() == 'token' and auth[1]:
        pool = request.app['pool']
        async with pool.acquire() as conn:
            async with conn.transaction():
                sql_q = 'select exists(select * from authtoken where key=$1)'
                exists = await conn.fetchval(sql_q, auth[1])
                if not exists:
                    raise web.HTTPForbidden(
                        reason='Invalid authorization token'
                    )
    else:
        raise web.HTTPForbidden(reason='Invalid authorization header')
    return await handler(request)
