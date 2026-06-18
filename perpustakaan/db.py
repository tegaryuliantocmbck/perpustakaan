from django.db import connection

def query(sql, params=None, one=False):
    with connection.cursor() as c:
        c.execute(sql, params or [])
        cols = [d[0] for d in c.description]
        rows = [dict(zip(cols, r)) for r in c.fetchall()]
    return (rows[0] if rows else None) if one else rows

def execute(sql, params=None, returning=False):
    with connection.cursor() as c:
        c.execute(sql, params or [])
        if returning:
            return c.fetchone()
