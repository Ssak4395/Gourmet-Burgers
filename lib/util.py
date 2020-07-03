# Utility functions go here
# ... if there even are any

import json
from flask import Response


def createResponse(status, obj={}, **kwargs):
    resp = dict(status=status)
    resp.update(obj)
    resp.update(kwargs)
    return resp


def createJSON(status, obj={}, **kwargs):
    return Response(response=json.dumps(createResponse(status, obj, **kwargs)),
                    status=200,
                    mimetype="application/json")
