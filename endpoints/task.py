from aiohttp import web
from aiojobs.aiohttp import spawn

from core.media import json_response
from models import TaskStatus
from schemas.task import TaskSchema
from dicttoxml import dicttoxml

from parsers.indeed.backend import parse


async def create_task(request):
    try:
        data = await request.json()
    except (ValueError, UnicodeDecodeError):
        raise web.HTTPBadRequest(
            reason='Request body is not valid \'application/json\''
        )

    d, errors = TaskSchema().load(data)
    if errors:
        raise web.HTTPBadRequest(reason='The schema validation failed.')

    async with request.app['pool'].acquire() as conn:
        async with conn.transaction():
            task_id = await conn.fetchval(
                'INSERT INTO task ("company_name", "location", "status") '
                'VALUES ($1, $2, $3) RETURNING id',
                d['company_name'], d['location'], TaskStatus.IN_PROGRESS.value
            )
            q = {'company': d['company_name'], 'loc': d['location']}
            await spawn(request, parse(task_id, q))
            return web.json_response({'id': task_id})


async def task_summary(request):
    async with request.app['pool'].acquire() as conn:
        async with conn.transaction():
            idx = int(request.match_info['id'])
            task = await conn.fetchrow('SELECT * FROM task WHERE id=$1', idx)
            if not task:
                raise web.HTTPNotFound(reason='Not found')

            sql_q = '''
            SELECT AVG(score), MAX(score), MIN(score), COUNT(*)
            FROM job where task_id=$1
            '''
            task_cnt = await conn.fetchrow(sql_q, idx)
            sql_q = 'SELECT id, title, score, "desc", url FROM job where task_id=$1'
            return json_response({
                'id': task['id'],
                'company_name': task['company_name'],
                'location': task['location'],
                'status': task['status'],
                'created_at': task['created_at'],
                'avg': task_cnt['avg'],
                'max': task_cnt['max'],
                'min': task_cnt['min'],
                'count': task_cnt['count'],
                'items': [
                    {'id': j['id'], 'title': j['title'], 'score': j['score'], 'description': j['desc'], 'url': j['url']}
                    for j in (await conn.fetch(sql_q, idx))
                ]
            })


async def detailed_info(request):
    async with request.app['pool'].acquire() as conn:
        async with conn.transaction():
            job = await conn.fetchrow('''
            SELECT job.id, job.task_id, job.title, job."desc", job.score,
            job.created_at, job.url, task.company_name, task."location"
            FROM job
            LEFT JOIN task ON task.id=job.task_id
            WHERE job.id=$1 ORDER BY job.title;
            ''', int(request.match_info['id']))
            if not job:
                raise web.HTTPNotFound(reason='Not found')

            return json_response({
                'id': job['id'],
                'task': {
                    'id': job['task_id'],
                    'company_name': job['company_name'],
                    'location': job['location']
                },
                'title': job['title'],
                'description': job['desc'],
                'score': job['score'],
                'created_at': job['created_at'],
                'url': job['url']
            })

   
async def list_tasks(request):
    async with request.app['pool'].acquire() as conn:
        async with conn.transaction():
            limit = request.rel_url.query.get('limit')
            limit = limit if limit and limit.isdigit() else 100
            offset = request.rel_url.query.get('offset')
            offset = offset if offset and offset.isdigit() else 0
            sql = """
                SELECT task.id, task.location, task.status, task.created_at,
                task.company_name, AVG(score), MAX(score), MIN(score), 
                COUNT(job.id) FROM task LEFT JOIN job ON task.id = job.task_id
                GROUP BY task.id HAVING COUNT(job.id) > 0 ORDER BY task.id DESC
                LIMIT {limit} OFFSET {offset}
            """.format(**{'limit': limit, 'offset': offset})
            tasks = await conn.fetch(sql)
            return json_response(
                [
                    {'id': t['id'], 
                    'company_name': t['company_name'],
                    'location': t['location'], 
                    'status': t['status'], 
                    'created_at': t['created_at'], 
                    'avg': t['avg'], 
                    'max': t['max'], 
                    'min': t['min'], 
                    'count': t['count']}
                    for t in tasks
                ]
            )
