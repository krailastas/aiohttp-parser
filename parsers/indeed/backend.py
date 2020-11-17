import asyncio
import aiohttp
import asyncpg

from bs4 import BeautifulSoup

import config


BASE_URL = 'https://www.indeed.com'
PAGINATION_LIMIT = 20  # pages
RETRY = 3   # times
TIMEOUT = 3     # seconds


async def produce(client, queue, start_url):
    i = 0
    #: it's used to avoid duplication while shifting the pagination.
    seen = []
    pages = None

    while pages is None or i < pages:
        next_url = f'{ start_url }&start={ i * 50 }'
        resp = await client.get(next_url)

        if resp.status != 200:
            break

        html = BeautifulSoup((await resp.read()), 'lxml')
        if not html.body:
            break

        if pages is None:
            # Define number of pages
            p = [
                int(pn.text) for pn in html.find_all('span', {'class': 'pn'})
                if pn.text.isdigit()
            ]

            max_page = 1 if not p else max(p)
            if 1 <= max_page <= PAGINATION_LIMIT:
                pages = max_page
            elif max_page > PAGINATION_LIMIT:
                pages = PAGINATION_LIMIT
            else:
                break

        links = html.find_all(
            'a', {'class': 'turnstileLink', 'data-tn-element': 'jobTitle'},
            href=True
        )
        for link in links:
            detailed_url = f'{ BASE_URL }{ link["href"] }'
            if detailed_url not in seen:
                await queue.put(detailed_url)
                seen.append(detailed_url)
        i += 1
        # Fall asleep for awhile so that to avoid the rate throttling
        await asyncio.sleep(1)


async def consume(db_pool, client, queue, task_id):
    while True:
        # Wait for an item from the producer
        url = await queue.get()
        desc, title = None, None

        i = 0
        while i < RETRY:
            resp = await client.get(url)
            if resp.status == 200:
                html = BeautifulSoup((await resp.text()), 'lxml')
                if not html.body:
                    break
                _t = html.find(
                    'h3', {'class': 'jobsearch-JobInfoHeader-title'}
                )
                if _t and _t.text:
                    title = _t.text

                    _d = html.find(
                        'div', {'class': 'jobsearch-JobComponent-description'}
                    )
                    if _d and _d.text:
                        desc = _d.text
                break
            else:
                i += 1
                await asyncio.sleep(TIMEOUT)

        if desc:
            headers = {
                'Content-Type': 'application/json',
                'key': config.SCORE_KEY
            }
            resp = await client.post(
                f'{ config.SCORE_SERVICE }/score', json={'text': desc},
                headers=headers
            )
            if resp.status == 200:
                async with db_pool.acquire() as db_conn:
                    sql_q = '''
                    INSERT INTO job (
                        "desc", "score", "task_id", "title", "url"
                    )
                    VALUES ($1, $2, $3, $4, $5)
                    '''
                    score = await resp.json()
                    await db_conn.execute(
                        sql_q, desc, score['value'], task_id, title, url
                    )

        queue.task_done()


async def parse(task_id, q, workers=10):
    start_url = f'https://www.indeed.com/jobs?as_cmp={ q["company"] }&limit=50&sort=date' # NOQA
    if q['loc']:
        start_url += f'&l={ q["loc"] }'

    if len(start_url) > 244:
        # The URL has exceeded the length limit.
        return

    queue = asyncio.Queue()
    db_pool = await asyncpg.create_pool(config.DATABASE['default'])

    kw_session = {
        'connector': aiohttp.TCPConnector(limit_per_host=workers)
    }
    try:
        async with aiohttp.ClientSession(**kw_session) as client:
            # Schedule background consumers.
            tasks = [
                asyncio.ensure_future(consume(db_pool, client, queue, task_id))
                for i in range(workers)
            ]

            await produce(client, queue, start_url)

            # Wait until the queue reaches emptiness.
            await queue.join()

            for task in tasks:
                task.cancel()

            async with db_pool.acquire() as conn:
                await conn.execute(
                    'UPDATE task SET status=2 WHERE id=$1', task_id
                )
    finally:
        await db_pool.close()
