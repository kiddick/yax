from collections import OrderedDict

SPOIDOC = """
<!DOCTYPE html>
<meta charset='utf-8'>
<html>

<head>
    <title></title>
    <script type="text/javascript">
    function spoiler(el, t) {{
        var inner = el.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0]
        if (inner.style.display != '') {{
            inner.style.display = '';
            el.innerText = '';
            el.value = t;
        }} else {{
            inner.style.display = 'none';
            el.innerText = '';
            el.value = '+';
        }}
    }}
    </script>
</head>
    {}
<body>
</body>
</html>
"""


j = OrderedDict([
    (('caption', 'str1str2str34'), OrderedDict([
        ('str1', ['str', '1']),
        ('str2', ['str', '2']),
        ('str34', ['str', '3', '4'])
    ]))
])


OPEN = """
<div class="spoil">
    <div class="smallfont">
        <input value="+" class="input-button" onclick="spoiler(this, '-');" type="button">
    </div>
    <div class="alt2">
        <div style="display: none; padding-left: 2.5em;">
"""


CLOSE = """
        </div>
    </div>
</div>
"""


def bold(inner):
    return '<b>{}</b>'.format(inner)


def italic(inner):
    return '<i>{}</i>'.format(inner)


def rex(d, open_, close_):
    if isinstance(d, (dict, OrderedDict)):
        for k in d:
            if isinstance(k, tuple):
                yield open_ + italic(bold(k[0])) + '<br>' + '{0}{1}{2}#######'.format(open_, k[1], close_)
            else:
                yield open_ + k
            for sub in rex(d[k], open_, close_):
                yield sub
            yield close_
    elif isinstance(d, (list, tuple)):
        d = ['{0}{1}{2}'.format(open_, el, close_) for el in d]
        yield open_ + ' '.join(d) + close_


def render(path, data):
    with open(path, 'w') as _xhtml:
        _xhtml.write(
            SPOIDOC.format(
                '\n'.join(list(rex(data, OPEN, CLOSE))))
        )

# render('tests.html', j)
