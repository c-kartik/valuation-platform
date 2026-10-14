"""Independent displayed indirect-CFO checks, not a financial adjustment engine."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import re

from . import historical_inputs as h, retained_components as inspect, statement_delivery as documents

ROOTS = ('NetCashProvidedByUsedInOperatingActivities',
         'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
         'NetCashProvidedByUsedInOperatingActivitiesDiscontinuedOperations')
STARTS = ('NetIncomeLoss', 'ProfitLoss', 'IncomeLossFromContinuingOperations')
# Standard displayed income subtotals can follow a bridge from parent-attributable
# net income. They are not another adjustment to add alongside their own children.
INCOME_PARENTS=frozenset(('IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest',
    'NetIncomeLossAvailableToCommonStockholdersBasic','NetIncomeLossAttributableToParent'))
VERSION = 'displayed-cfo-reconciliation-v1'


def uncertainty(precision):
    if precision == 'INF': return Decimal(0)
    try: return Decimal(10) ** -int(precision) / 2
    except (ValueError, TypeError): raise h.InputError('Explicit numeric precision required')


def displayed(text, raw):
    token = text.replace('$','').replace(',','').replace(' ','').replace('\xa0','').replace('−','-')
    if token in ('—','–','-'):
        if raw != 0: raise h.InputError('Dash is not proof of an absent/zero fact')
        return Decimal(0)
    if token.startswith('(') and token.endswith(')'): token='-'+token[1:-1]
    try: value=Decimal(token)
    except InvalidOperation: raise h.InputError('Unbound displayed numeric cell')
    if not value.is_finite(): raise h.InputError('Nonfinite display')
    return value


def display_scale(exponent):
    exponent=int(exponent)
    return 10**exponent if exponent>=0 else Decimal(10)**exponent


def bind_inline(evidence, record, table, row, cell, item, period_kind='annual', bindings=None):
    """Bind visible sign independently of the taxonomy fact's debit/credit sign."""
    attrs=item['attrs']; name=attrs.get('name',''); context=attrs.get('contextref')
    if ':' not in name: raise h.InputError('Exact inline QName missing')
    prefix, concept=name.split(':',1); namespace=evidence.namespaces.get(prefix)
    ctx=evidence.contexts.get(context)
    if ctx is None:raise h.InputError('Context unavailable')
    if period_kind=='annual' and (ctx.start,ctx.end)!=(evidence.period.annual_start,evidence.period.annual_end):
        return None
    if period_kind=='instant' and (ctx.start is not None or ctx.end!=evidence.period.annual_end):return None
    if inspect.dimensions(ctx) or int(ctx.entity_identifier)!=evidence.period.cik or ctx.entity_identifier_scheme!='http://www.sec.gov/CIK':
        raise h.InputError('Exact nondimensional entity context required')
    facts=[(f,i) for f,i in evidence.facts if (f.namespace,f.concept,f.context_id)==(namespace,concept,context)]
    if not facts: raise h.InputError('Inline occurrence not in retained instance')
    usd=inspect.x.FilingXBRLQName('http://www.xbrl.org/2003/iso4217','USD')
    if any(f.is_nil or f.numeric_value is None or f.unit is None or f.unit.numerator_measures!=(usd,) or f.unit.denominator_measures for f,_ in facts):
        raise h.InputError('Nil/nonmonetary/non-USD row')
    values={f.numeric_value for f,_ in facts}
    if len(values)!=1: raise h.InputError('Conflicting same-population facts')
    fact=facts[0][0]; raw=fact.numeric_value
    if len({f.decimals for f,_ in facts})!=1:raise h.InputError('Conflicting occurrence precision')
    if attrs.get('decimals')!=fact.decimals:raise h.InputError('Independent displayed precision differs or is unavailable')
    documents.check_primary_binding(bindings or documents.primary_bindings(record),attrs,namespace,ctx,fact.unit)
    scale=display_scale(attrs.get('scale','0'))
    if attrs.get('sign') not in (None,'-'):raise h.InputError('Unsupported inline sign')
    lexical=displayed(item['text'],raw)*scale*(-1 if attrs.get('sign')=='-' else 1)
    if lexical!=raw:raise h.InputError('Inline signed representation disagrees with instance')
    value=displayed(cell['text'],raw)*scale
    if abs(value)!=abs(raw): raise h.InputError('Independent displayed amount/scale disagrees with instance')
    multiplier=1 if value==raw else -1
    primary=documents.receipt(record,evidence.period)
    locator=documents.canonical(dict(table=table,row=row,cell_name=name,context_id=context,
        display=cell['text'],scale=scale if type(scale) is int else str(scale),inline_sign=attrs.get('sign'),cash_sign_multiplier=multiplier))
    sources=tuple(h.SourceReference('statement-instance:'+str(i),evidence.period,evidence.instance,
        documents.canonical(dict(unit_id=f.unit_ref)),namespace,concept,context,i,ctx.start,ctx.end,'USD',
        str(f.numeric_value),f.decimals,()) for f,i in facts)
    sources += (h.SourceReference('statement-primary:'+str(table)+':'+str(row)+':'+concept,evidence.period,
        primary,locator,'','','',None,ctx.start,ctx.end,'USD',str(raw),fact.decimals,()),)
    uncertainty(fact.decimals)
    return dict(concept=concept,namespace=namespace,context_id=context,raw=str(raw),value=str(value),
        scale=1,display_scale=scale if type(scale) is int else str(scale),sign=multiplier,precision=fact.decimals,
        caption='',sources=sources,ordinal=facts[0][1],table=table,row=row)


def check_rows(rows, cfo, *, complete, non_overlapping, scope):
    """No residual-defined validation. Check an independently enumerated statement."""
    if not rows or not complete or not non_overlapping:
        return dict(status='PARTIAL',scope=scope,difference=None,tolerance=None,
                    reason='Complete non-overlapping displayed operand population not established')
    keys=[(r['namespace'],r['concept'],r['context_id']) for r in rows]
    if len(keys)!=len(set(keys)):raise h.InputError('Duplicated/overlapping displayed population')
    difference=sum((Decimal(r['value']) for r in rows),Decimal(0))-Decimal(cfo['value'])
    tolerance=sum((uncertainty(r['precision']) for r in (*rows,cfo)),Decimal(0))
    return dict(status='SUPPORTED' if abs(difference)<=tolerance else 'FAILED',scope=scope,
        difference=str(difference),tolerance=str(tolerance),
        precision_rule='Sum of half-unit rounding intervals for every independently displayed operand and CFO; INF is exact.',
        reason='Independent complete display arithmetic, not CFO-minus-residual equality')


def movement_overlap(rows):
    from . import retained_working_capital as movements
    concepts={r['concept'] for r in rows if r['namespace'].startswith('http://fasb.org/us-gaap/')}
    overlaps=[(r.concept,child) for r in movements.RULES for child in r.possible_children
              if r.concept in concepts and child in concepts]
    if 'IncreaseDecreaseInOperatingCapital' in concepts:
        overlaps.extend(('IncreaseDecreaseInOperatingCapital',r.concept) for r in movements.RULES
            if r.concept in concepts and r.concept!='IncreaseDecreaseInOperatingCapital')
    return overlaps


def inspect_statement(evidence, record):
    if record is None:return dict(version=VERSION,status='NOT_ASSESSED',reason='Exact primary body/receipt unavailable',populations=[])
    identity=dict(cik=evidence.period.cik,accession=evidence.period.accession,annual_start=str(evidence.period.annual_start),annual_end=str(evidence.period.annual_end))
    documents.verify_primary(record,identity)
    bindings=documents.primary_bindings(record)
    populations=[]
    for ti, table in enumerate(documents.parse(record)):
        bound=[]; failures=[]
        for ri, row in enumerate(table):
            caption=' '.join(c['text'] for c in row if not c['facts']).strip()
            entries=[]
            for cell in row:
                for item in cell['facts']:
                    try: value=bind_inline(evidence,record,ti,ri,cell,item,bindings=bindings)
                    except (h.InputError,ValueError) as exc:
                        entries.append(dict(error=str(exc),failed_concept=item['attrs'].get('name','').split(':')[-1]));continue
                    if value:
                        value['caption']=caption;entries.append(value)
            bound.append(entries)
        ends=[(i,r) for i,rr in enumerate(bound) for r in rr if r.get('concept') in ROOTS]
        if not ends:
            errors=[r for rr in bound for r in rr if r.get('failed_concept') in ROOTS]
            if errors:populations.append(dict(table=ti,status='PARTIAL',reason='CFO source binding invalid',requirements=errors,rows=[]))
            continue
        # A single current scope per table. Multiple scope totals require an
        # independently evidenced hierarchy; they are not a leaf-row sum.
        if len(ends)!=1:
            populations.append(dict(table=ti,status='PARTIAL',reason='Multiple/parent CFO populations; hierarchy unresolved',rows=[]));continue
        end,cfo=ends[0]
        starts=[(i,r) for i,rr in enumerate(bound[:end]) for r in rr if r.get('concept') in STARTS]
        if len(starts)!=1:
            populations.append(dict(table=ti,status='PARTIAL',reason='Unique reported starting subtotal unavailable',rows=[]));continue
        begin,start=starts[0]; rows=[]; complete=True
        scope='CONSOLIDATED' if cfo['concept']==ROOTS[0] else 'CONTINUING' if cfo['concept']==ROOTS[1] else 'DISCONTINUED'
        if not cfo['namespace'].startswith('http://fasb.org/us-gaap/'):
            complete=False;failures.append('Extension CFO scope is unreviewed, not accepted from its local name')
        if (scope!='CONSOLIDATED')!=(start['concept']=='IncomeLossFromContinuingOperations'):complete=False;failures.append('Starting/CFO scope requires separate evidence')
        for ri in range(begin,end):
            entries=bound[ri]
            if len(entries)>1 or any('error' in r for r in entries):complete=False;failures.append('Multiple/unbound current monetary populations at row '+str(ri));continue
            if entries:
                r=entries[0]
                if ri!=begin and (r['concept'] in INCOME_PARENTS or r['concept'].startswith('NetCashProvidedByUsed') or re.search(r'\btotal\b|\bnet cash\b',r['caption'],re.I)):
                    complete=False;failures.append('Possible intermediate parent subtotal at row '+str(ri))
                from . import retained_working_capital as movements
                r['role']='starting_subtotal' if ri==begin else 'displayed_movement' if r['namespace'].startswith('http://fasb.org/us-gaap/') and r['concept'] in {rule.concept for rule in movements.RULES} else 'displayed_adjustment'
                rows.append(r)
            elif any(c['facts'] for c in table[ri]) or any(re.fullmatch(r'\(?[\d,]+(?:\.\d+)?\)?',c['text'].replace('$','').strip()) for c in table[ri][1:]):
                complete=False;failures.append('Missing eligible current amount at displayed row '+str(ri))
        keys=[(r['namespace'],r['concept'],r['context_id']) for r in rows]
        if len(keys)!=len(set(keys)):complete=False;failures.append('Repeated parent/component population; no sum')
        overlap=movement_overlap(rows)
        if overlap:complete=False;failures.append('Reported movement parent/children coexist; no demonstrated non-overlap: '+repr(overlap))
        result=check_rows(rows,cfo,complete=complete,non_overlapping=len(keys)==len(set(keys)),scope=scope)
        populations.append(dict(result,table=ti,rows=rows,cfo=cfo,requirements=failures,
            evidence=dict(url=record['url'],sha256=record['sha256'],path=record['path'],locator=record['locator']),
            relationship='Displayed row sequence between unique starting subtotal and reported CFO; intermediate subtotal populations fail closed.'))
    status=('NOT_ASSESSED' if not populations else 'FAILED' if any(p['status']=='FAILED' for p in populations)
        else 'SUPPORTED' if len(populations)==1 and populations[0]['status']=='SUPPORTED' else 'PARTIAL')
    return dict(version=VERSION,status=status,populations=populations,
        reason=None if status=='SUPPORTED' else 'Missing, conflicting or incomplete independently displayed reconciliation; no residual proof')
