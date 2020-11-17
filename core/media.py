import json
from datetime import datetime
from decimal import Decimal

from aiohttp import web
from aiohttp.helpers import sentinel


class DefaultJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            rep = o.isoformat()
            if rep.endswith('+00:00'):
                rep = rep[:-6] + 'Z'
            return rep
        if isinstance(o, Decimal):
            return float(o)


def json_response(data=sentinel, *, text=None, body=None, status=200,
                  reason=None, headers=None, content_type='application/json',
                  dumps=json.dumps):
    if data is not sentinel:
        if text or body:
            raise ValueError(
                "only one of data, text, or body should be specified"
            )
        else:
            text = dumps(data, cls=DefaultJSONEncoder)
    return web.Response(
        text=text, body=body, status=status, reason=reason,
        headers=headers, content_type=content_type
    )
