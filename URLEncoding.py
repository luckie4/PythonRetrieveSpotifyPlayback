class urlencoding:
    def quote(s):
        always_safe = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz' '0123456789' '_.-'
        res = []
        for c in s:
            if c in always_safe:
                res.append(c)
                continue
            res.append('%%%x' % ord(c))
        return ''.join(res)

    def quote_plus(s):
        s = urlencoding.quote(s)
        if ' ' in s:
            s = s.replace(' ', '+')
        return s

    def urlencode(query):
        if isinstance(query, dict):
            query = query.items()
        li = []
        for k, v in query:
            if not isinstance(v, list):
                v = [v]
            for value in v:
                k = urlencoding.quote_plus(str(k))
                v = urlencoding.quote_plus(str(value))
                li.append(k + '=' + v)
        return '&'.join(li)
