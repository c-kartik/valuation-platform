"""Bounded, offline verification of reviewed primary-source preload selections.

Only named inline-XBRL facts and explicit prose ranges are supported. A new
disclosure shape fails rather than silently guessing a value or period.
"""
from decimal import Decimal, Context, localcontext
from html.parser import HTMLParser
import re
from xml.etree import ElementTree as ET

XI = '{http://www.xbrl.org/2003/instance}'
ISO = 'http://www.xbrl.org/2003/iso4217'


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def inline_document(body):
    if len(body) > 12 * 1024 * 1024 or b'<!ENTITY' in body.upper():
        raise ValueError('Unsupported primary document size/entities')
    from io import BytesIO
    namespaces = {}
    for _, pair in ET.iterparse(BytesIO(body), events=('start-ns',)):
        prefix, url = pair
        if prefix in namespaces and namespaces[prefix] != url:
            raise ValueError('Shadowed namespace requires extraction review')
        namespaces[prefix] = url
    root = ET.fromstring(body)
    return root, namespaces, {e.get('id'): e for e in root.iter() if e.tag == XI+'context'}, {e.get('id'): e for e in root.iter() if e.tag == XI+'unit'}


def inline_fact(document, selection):
    root, namespaces, contexts, units = document
    expected = selection['concept']
    prefix, local = expected.split(':', 1)
    namespace = namespaces.get(prefix)
    if not namespace:
        raise ValueError('Unknown selected concept namespace')
    matches = []
    with localcontext(Context(prec=50)):
        for e in root.iter():
            if not e.tag.endswith('}nonFraction') or ':' not in e.get('name', ''):
                continue
            p, name = e.get('name').split(':', 1)
            if name != local or namespaces.get(p) != namespace:
                continue
            c = contexts.get(e.get('contextRef'))
            if c is None or any(x.tag.endswith(('}explicitMember', '}typedMember')) for x in c.iter()):
                continue
            ident = c.findtext('.//'+XI+'identifier')
            start = c.findtext(XI+'period/'+XI+'startDate')
            end = c.findtext(XI+'period/'+XI+'endDate')
            if (ident is None or int(ident) != selection['cik'] or start != selection['start'] or end != selection['end']):
                continue
            unit = units.get(e.get('unitRef'))
            measures = list(unit) if unit is not None else []
            if len(measures) != 1 or measures[0].tag != XI+'measure':
                raise ValueError('Selected monetary fact has a non-simple unit')
            measure = measures[0].text.split(':')
            if len(measure) != 2 or measure[1] != 'USD' or namespaces.get(measure[0]) != ISO:
                raise ValueError('Selected monetary fact must be USD')
            text = ''.join(e.itertext()).strip().replace(',', '').replace('\xa0', '')
            if e.get('{http://www.w3.org/2001/XMLSchema-instance}nil', 'false') not in ('false', '0'):
                raise ValueError('Nil selected fact')
            fmt = e.get('format', '').split(':')[-1]
            if fmt not in ('numdotdecimal', 'num-dot-decimal', ''):
                raise ValueError('Unsupported inline number format')
            value = Decimal(0) if text in ('—', '–', '-') else Decimal(text.strip('()'))
            if e.get('sign') == '-' or text.startswith('('): value = -value
            value *= Decimal(10) ** int(e.get('scale', '0'))
            if not value.is_finite() or not e.get('id') or e.get('decimals') is None:
                raise ValueError('Finite tagged amount, precision and locator required')
            matches.append({'value': format(value, 'f'), 'precision': e.get('decimals'), 'locator': 'inline#'+e.get('id')})
    if not matches or len({(x['value'], x['precision']) for x in matches}) != 1:
        raise ValueError('Missing or competing exact primary facts: '+expected)
    return matches[0]


def prose_range(body, selection):
    text = Text(); text.feed(body.decode('utf-8'))
    plain = re.sub(r'\s+', ' ', ' '.join(text.parts))
    matches = list(re.finditer(selection['pattern'], plain, re.I))
    if len(matches) != 1:
        raise ValueError('Unique reviewed guidance passage required')
    match = matches[0]
    with localcontext(Context(prec=50)):
        value = Decimal(match.group(selection['group']).replace(',', '')) * Decimal(10) ** selection['scale']
    return {'value': format(value, 'f'), 'precision': selection['precision'], 'locator': match.group(0)}


def verify_observations(directory, sources, observations):
    """Legacy reviewed records remain supported; new mapped points replay exactly."""
    files = {s['id']: s['file'] for s in sources}
    documents = {}
    for row in observations:
        selection = row.get('extraction')
        if not selection:
            continue
        path = directory/'sources'/files[row['source']]
        if selection['kind'] == 'inline-xbrl-v1':
            if (any(selection[k] != row[k] for k in ('cik', 'start', 'end')) or
                    row['unit'] != 'USD' or row['dimensions'] != [] or row['scope'] != 'consolidated' or
                    row['definition'] != 'consolidated-reported'):
                raise ValueError('Inline selection identity differs from reviewed observation')
            if path not in documents: documents[path] = inline_document(path.read_bytes())
            point = inline_fact(documents[path], selection)
        elif selection['kind'] == 'prose-range-v1':
            point = prose_range(path.read_bytes(), selection)
        else:
            raise ValueError('Unsupported reviewed extraction kind')
        if any(point[k] != row[k] for k in ('value', 'precision', 'locator')):
            raise ValueError('Reviewed observation differs from primary source: '+row['key'])
