"""Reusable reported-population selection; no issuer approval or equity bridge.

Completeness is confined to the expressly reported population. A recognized lease
total is not complete borrowing scope; cash is not excess/unrestricted cash.
"""
from dataclasses import replace
from decimal import Decimal
from html.parser import HTMLParser
import re
import hashlib
import json

from . import historical_inputs as h, statement_delivery as docs
from . import cfo_statement_reconciliation as statement, retained_components as inspection

VERSION='reported-bridge-population-v1'
IMPROVED_VERSION='reported-bridge-population-v2'
FAMILIES=(h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES,h.Field.SHARES)
POPULATIONS=frozenset(('CashAndCashEquivalentsAtCarryingValue','MarketableSecuritiesCurrent',
    'CashCashEquivalentsAndMarketableSecurities','ShortTermInvestments','LongTermDebt','DebtInstrumentCarryingAmount',
    'FinanceLeaseLiability','FinanceLeaseLiabilityCurrent','FinanceLeaseLiabilityNoncurrent',
    'OperatingLeaseLiability','OperatingLeaseLiabilityCurrent','OperatingLeaseLiabilityNoncurrent'))


def monetary_rows(e,record,improved=False):
    bindings=docs.primary_bindings(record);tables=[];errors=[]
    for ti,table in enumerate(docs.parse(record,improved=improved)):
        rows=[]
        for ri,row in enumerate(table):
            caption=' '.join(c['text'] for c in row if not c['facts']).strip()
            for cell in row:
                for item in cell['facts']:
                    try:v=statement.bind_inline(e,record,ti,ri,cell,item,'instant',bindings,reviewed_display=improved)
                    except (h.InputError,ValueError) as exc:
                        context=e.contexts.get(item['attrs'].get('contextref'))
                        if context is None or (context.start is None and context.end==e.period.annual_end and not inspection.dimensions(context)):
                            errors.append(dict(table=ti,row=ri,name=item['attrs'].get('name'),reason=str(exc)))
                        continue
                    if v:v['caption']=caption;rows.append(v)
        tables.append(rows)
    return tables,errors


def value(row,field,role,scope, *, operand=False):
    return h.InputValue('usable-bridge:'+role+':'+str(row['ordinal']),field,row['sources'][0].period,
        row['sources'][0].end,Decimal(row['value']),'USD',1,row['sign'],row['precision'],role,
        h.Origin.REPORTED,h.Quality.SUPPORTED,scope,h.Scope.CONSOLIDATED_REPORTED,
        h.Completeness.COMPLETE,h.Review.REVIEWED,row['sources'],None,None,(),
        'Exact independently displayed standard population; not excess cash, net debt or valuation approval.',
        ('usable_bridge_version:1','reported_population_only'),(),None,(role,))


def unique(rows,concept,field,role,scope):
    found=[r for r in rows if r['concept']==concept and r['namespace'].startswith('http://fasb.org/us-gaap/')]
    if not found:return None
    if len({(r['value'],r['precision']) for r in found})!=1:return None
    # Keep every confirming primary/instance occurrence, deduplicated by identity.
    sources={s.source_id+':'+s.receipt.artifact.sha256:s for r in found for s in r['sources']}
    source_ids={};refs=[]
    for s in sources.values():
        key=s.source_id
        if key in source_ids and source_ids[key]!=s:key+=':'+s.receipt.artifact.sha256[:16]
        refs.append(replace(s,source_id=key));source_ids[key]=s
    return replace(value(found[0],field,role,scope),sources=tuple(refs))


def reviewed_current_scope(e,record):
    """Reuse an existing exact pilot note review, never extend it to other years.

    Broad ShortTermInvestments is not made universally liquid by this join.
    """
    from . import pilot_cash_investments as existing
    raw=existing.EVIDENCE_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=existing.EVIDENCE_SHA256:raise h.InputError('Existing reviewed note identity changed')
    matches=[v for v in json.loads(raw)['periods'] if v['period']['accession']==e.period.accession and
        v['primary_url']==record['url'] and v['primary_sha256']==record['sha256'] and
        v['instance_sha256']==e.instance.artifact.sha256]
    if len(matches)!=1:return None
    parser=existing._Tags();parser.feed(record['body'].decode());text=' '.join(' '.join(parser.parts).split())
    excerpts=[n['text'] for n in matches[0]['scope_notes'] if 'highly liquid nature' in n['text'] and 'available for current operations' in n['text']]
    if len(excerpts)!=1 or excerpts[0] not in text:return None
    return dict(review='docs/pilot-cash-investment-evidence.json',review_sha256=existing.EVIDENCE_SHA256,
        accession=e.period.accession,excerpt=excerpts[0],basis='Existing exact reviewed highly-liquid current investment note; not excess cash.')


def total(operands,field,role,scope):
    if not operands or any(v.value is None or v.completeness is not h.Completeness.COMPLETE for v in operands):
        raise h.InputError('Incomplete population cannot be totaled')
    if len({v.as_of for v in operands})!=1 or len({v.unit for v in operands})!=1:
        raise h.InputError('Date/unit mismatch in total')
    keys=[k for v in operands for k in v.coverage_keys]
    if len(keys)!=len(set(keys)) or any(not v.coverage_keys for v in operands):raise h.InputError('Overlapping population')
    root=operands[0]
    f=h.Formula(VERSION+':'+role,1,h.FormulaKind.COMPONENT_TOTAL,' + '.join(v.input_id for v in operands),
        tuple(v.input_id for v in operands),False,True,True,
        tuple(s.source_id for v in operands for s in v.sources if s.occurrence_ordinal is None))
    return replace(root,input_id='usable-bridge:'+role,role=role,scope=scope,
        value=sum((v.value for v in operands),Decimal(0)),sign=1,precision='derived_from_explicit_reported_precision',
        origin=h.Origin.DERIVED,sources=(),formula=f,coverage_keys=(role,),
        selection_rationale='Complete expressly defined partition, same date/unit, independent displayed evidence; no parent plus child sum.')


def inspect(e,record,version=VERSION):
    if version not in (VERSION,IMPROVED_VERSION):raise h.InputError('Unknown bridge inspection version')
    improved=version==IMPROVED_VERSION
    inputs=[];requirements=[];proofs=[]
    if record is None:return (),dict(version=version,status='UNRESOLVED',requirements=['Exact independent primary body/receipt unavailable'],populations=[])
    docs.verify_primary(record,dict(cik=e.period.cik,accession=e.period.accession,annual_start=str(e.period.annual_start),annual_end=str(e.period.annual_end)))
    tables,errors=monetary_rows(e,record,improved);allrows=[r for t in tables for r in t]
    reviewed=reviewed_current_scope(e,record)
    invalid={v['name'].split(':')[-1] for v in errors if v['name']}
    # An invalid competing nondimensional population cannot be dropped to make
    # the remaining one look independently complete.
    allrows=[r for r in allrows if r['concept'] not in invalid]
    tables=[[r for r in t if r['concept'] not in invalid] for t in tables]
    balance=[t for t in tables if {'Assets','LiabilitiesAndStockholdersEquity'}.issubset({r['concept'] for r in t})]
    candidates=[]
    for table in balance:
        ends=[r['row'] for r in table if r['concept']=='AssetsCurrent']
        if len(set(ends))!=1:continue
        current=[r for r in table if r['row']<ends[0]]
        cash=unique(current,'CashAndCashEquivalentsAtCarryingValue',FAMILIES[0],'cash_equivalents_reported',
                    'Reported cash and cash equivalents; not restricted/excess cash certification.')
        market=unique(current,'MarketableSecuritiesCurrent',FAMILIES[0],'current_marketable_reported',
                      'Separately displayed current marketable securities, not long-term/strategic investments.')
        short=None
        if market is None and reviewed:
            short=unique(current,'ShortTermInvestments',FAMILIES[0],'current_liquid_investments_reviewed',
                'Exact prior reviewed current highly-liquid investment note; not long-term/strategic/excess cash.')
            if short:
                scope_source=replace(short.sources[-1],source_id='reviewed-current-scope:'+short.input_id,
                    locator=docs.canonical(reviewed))
                market=replace(short,sources=(*short.sources,scope_source))
        parent=unique(current,'CashCashEquivalentsAndMarketableSecurities',FAMILIES[0],'reported_current_liquidity',
                      'Expressly reported cash/equivalents/current marketable parent in current-assets panel.')
        if parent:candidates.append((parent,()))
        elif cash and market and (short is not None or not any(r['concept']=='ShortTermInvestments' for r in current)):
            candidates.append((total((cash,market),FAMILIES[0],'reported_current_liquidity',
                'Cash/equivalents plus separately displayed current marketable securities; current-assets sibling populations, not excess/unrestricted cash.'),(cash,market)))
    if len(candidates)==1:
        root,children=candidates[0];inputs.extend((*children,root));proofs.append(dict(role=root.role,
            basis='Main balance-sheet current-assets sibling partition or reported current parent',
            source_table_candidates=len(candidates),scope=root.scope))
    else:requirements.append('Complete reported cash/current liquid-investment population is missing/conflicting; other/restricted/strategic populations not treated as zero.')
    # Pure borrowing total requires an explicit total caption; a long-term-only
    # caption, principal/fair value or combined capital-lease parent cannot substitute.
    borrowing=[r for r in allrows if r['namespace'].startswith('http://fasb.org/us-gaap/') and r['concept'] in ('DebtInstrumentCarryingAmount','LongTermDebt')
               and re.match(r'^total (?:debt|borrowings)\b',r['caption'],re.I)
               and not re.search(r'fair value|principal|capital lease|finance lease',r['caption'],re.I)]
    if borrowing and len({(r['value'],r['concept'],r['precision']) for r in borrowing})==1:
        v=unique(borrowing,borrowing[0]['concept'],FAMILIES[1],'reported_borrowing_total',
                 'Explicit reported total-debt caption; carrying/principal basis and complete short-term/lease inclusion remain unproved.')
        if v:inputs.append(replace(v,quality=h.Quality.LIMITED,scope_status=h.Scope.UNKNOWN,
            completeness=h.Completeness.PARTIAL,
            flags=v.flags+('borrowing_finance_lease_overlap_unknown','borrowing_basis_and_full_population_unproved'),
            unresolved_requirements=('Reported caption/tag alone does not establish carrying basis or complete borrowing scope; do not add finance leases.',)))
    elif improved and borrowing:
        # Newly bound competing captions cannot erase a previously supported
        # partial observation or change its stable analyst target identity.
        # Reuse v1 inspection solely for that physical-source identity join.
        prior,_=inspect(e,record,VERSION)
        prior=[v for v in prior if v.role=='reported_borrowing_total']
        keys=lambda v:{(s.receipt.artifact.sha256,s.namespace,s.concept,s.context_id,s.occurrence_ordinal) for s in v.sources if s.occurrence_ordinal is not None}
        groups={}
        for row in borrowing:groups.setdefault((row['value'],row['concept'],row['precision']),[]).append(row)
        for group in groups.values():
            v=unique(group,group[0]['concept'],FAMILIES[1],'reported_borrowing_total',
                'Competing independently displayed borrowing caption; carrying/principal basis and complete inclusion are unresolved.')
            matches=[old for old in prior if keys(old)&keys(v)]
            if len(matches)==1:v=replace(v,input_id=matches[0].input_id)
            inputs.append(replace(v,quality=h.Quality.LIMITED,scope_status=h.Scope.UNKNOWN,completeness=h.Completeness.PARTIAL,
                flags=v.flags+('borrowing_finance_lease_overlap_unknown','borrowing_basis_and_full_population_unproved','competing_borrowing_populations'),
                unresolved_requirements=('Competing reported borrowing captions retained separately; no selection, carrying-basis equivalence, aggregation or lease addition approved.',)))
        requirements.append('Competing borrowing captions retained, including prior physical-source targets; basis/inclusion unresolved, no total selected.')
    else:requirements.append('Complete reported borrowing total not established; long-term/current components are retained without assuming absent borrowing is zero.')
    for prefix,label in (('Finance','finance'),('Operating','operating')):
        role='reported_'+label+'_lease_liability'
        parent=unique(allrows,prefix+'LeaseLiability',FAMILIES[1],role,
                      'Recognized discounted '+label+' lease liability, not undiscounted payments or lease cash service.')
        if parent:inputs.append(parent)
        else:
            partitions=[]
            for table in tables:
                a=unique(table,prefix+'LeaseLiabilityCurrent',FAMILIES[1],role+':current','Reported current recognized '+label+' lease liabilities.')
                b=unique(table,prefix+'LeaseLiabilityNoncurrent',FAMILIES[1],role+':noncurrent','Reported noncurrent recognized '+label+' lease liabilities.')
                if a and b:
                    partitions.append((a,b))
            if len(partitions)==1:
                a,b=partitions[0]
                inputs.extend((a,b,total((a,b),FAMILIES[1],role,
                    'Current/noncurrent recognized '+label+' lease partition in the same disclosure; no addition to debt.')))
            else:requirements.append('Recognized '+label+' lease total/unique complete partition unestablished; absence is not zero.')
    share_record=record['filing_primary'] if improved and record.get('document_type') in ('EX-13','EX-13.1') else record
    shares,share_proof=inspect_shares(e,share_record,improved=improved)
    inputs.extend(shares);proofs.append(share_proof)
    requirements.extend(share_proof['requirements'])
    # Invalid primary bindings remain visible. They cannot establish a population
    # and must be dispositioned alongside retained alternatives in the parent.
    if errors:requirements.append('Invalid independent primary bindings retained in proof; not accepted as component values.')
    return tuple(inputs),dict(version=version,status='PARTIAL' if requirements else 'REPORTED_POPULATIONS',
        requirements=requirements,populations=proofs,invalid_bindings=errors,source=dict(url=record['url'],sha256=record['sha256'],path=record['path'],locator=record['locator']),
        candidates=[r for t in tables for r in t if r['concept'] in POPULATIONS],
        limitations=['Reported population selection is not financial sufficiency or an economic lease convention.',
                    'Long-term, strategic, restricted and overlapping original observations remain separate.',
                    'Issuer share completeness requires separate cover/date/class evidence.'])


def inspect_shares(e,record,improved=False):
    """Accept only an independently labelled nondimensional cover-page total.

    Class observations stay in the original ledger; this interface never infers
    their equivalence or complete coverage. No sum is authorized by equal dates.
    """
    class Cover(HTMLParser):
        def __init__(self):super().__init__();self.parts=[];self.active=None;self.facts=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='ix:nonfraction' and attrs.get('name')=='dei:EntityCommonStockSharesOutstanding':
                self.active=dict(attrs=attrs,text=[],before=' '.join(self.parts)[-300:],part_index=len(self.parts))
        def handle_data(self,text):
            self.parts.append(text)
            if self.active is not None:self.active['text'].append(text)
        def handle_endtag(self,tag):
            if tag=='ix:nonfraction' and self.active is not None:
                self.active['text']=''.join(self.active['text']);self.facts.append(self.active);self.active=None
    parser=Cover();parser.feed(record['body'].decode());parser.close()
    facts=[(f,i) for f,i in e.facts if f.concept=='EntityCommonStockSharesOutstanding'
           and f.namespace==e.namespaces.get('dei')]
    dimensions={inspection.dimensions(e.contexts[f.context_id]) for f,_ in facts}
    reasons=[];values=[]
    if any(dimensions):reasons.append('Classed share observations exist; complete issuer class coverage not independently established; no sum or nondimensional substitution.')
    else:
        own=docs.primary_bindings(record)
        for item in parser.facts:
            attrs=item['attrs'];ctx=e.contexts.get(attrs.get('contextref'))
            if ctx is None or ctx.start is not None or inspection.dimensions(ctx):continue
            if int(ctx.entity_identifier)!=e.period.cik or ctx.entity_identifier_scheme!='http://www.sec.gov/CIK':continue
            caption=item['before'].lower()
            after=' '.join(parser.parts[item['part_index']:])[:240] if improved else ''
            if improved:caption+=' '+after.lower()
            pattern=r'(?:shares of (?:the registrant.s )?common stock|common stock[^.]{0,160}(?:outstanding|as of))'
            if improved:pattern=r'(?:shares of (?:the registrant.s )?common stock|common stock.{0,160}(?:outstanding|as of)|shares outstanding of the registrant.s common stock)'
            if not re.search(pattern,caption) or re.search(r'\bclass [abc]\b',caption):
                reasons.append('Cover caption does not establish unclassed issuer common shares.');continue
            matches=[(f,i) for f,i in facts if f.context_id==attrs.get('contextref')]
            if not matches or len({(f.numeric_value,f.decimals) for f,_ in matches})!=1:reasons.append('Share values/precision conflicting.');continue
            f=matches[0][0]
            try:
                if f.is_nil or f.numeric_value is None or f.numeric_value<0 or f.unit is None:raise h.InputError('Invalid share fact')
                if attrs.get('sign') is not None or attrs.get('decimals')!=f.decimals:raise h.InputError('Share sign/precision binding differs')
                measures=f.unit.numerator_measures
                if len(measures)!=1 or (measures[0].namespace,measures[0].local_name)!=('http://www.xbrl.org/2003/instance','shares') or f.unit.denominator_measures:raise h.InputError('Share unit mismatch')
                docs.check_primary_binding(own,attrs,f.namespace,ctx,f.unit)
                if statement.displayed(item['text'],f.numeric_value)*statement.display_scale(attrs.get('scale','0'))!=f.numeric_value:raise h.InputError('Displayed shares differ')
                statement.uncertainty(f.decimals)
                sources=tuple(h.SourceReference('share-instance:'+str(i),e.period,e.instance,
                    docs.canonical(dict(unit_id=g.unit_ref)),g.namespace,g.concept,g.context_id,i,None,ctx.end,'shares',str(g.numeric_value),g.decimals,()) for g,i in matches)
                location=dict(name=attrs['name'],context=attrs['contextref'],caption=item['before'],display=item['text'])
                if improved:location['following_caption']=after
                sources+=(h.SourceReference('share-primary:'+ctx.context_id if hasattr(ctx,'context_id') else 'share-primary:'+attrs['contextref'],
                    e.period,docs.receipt(record,e.period),docs.canonical(location),
                    '','','',None,None,ctx.end,'shares',str(f.numeric_value),f.decimals,()),)
                values.append(h.InputValue('usable-bridge:issuer-common-shares:'+str(matches[0][1]),h.Field.SHARES,e.period,ctx.end,
                    f.numeric_value,'shares',1,1,f.decimals,'issuer_common_shares',h.Origin.REPORTED,h.Quality.SUPPORTED,
                    'Independently labelled unclassed cover common shares at actual reported observation date; not diluted/weighted shares.',
                    h.Scope.CONSOLIDATED_REPORTED,h.Completeness.COMPLETE,h.Review.REVIEWED,sources,None,None,(),
                    'Exact nondimensional common-share cover population and instance agree; actual date preserved.',
                    ('usable_bridge_version:1','reported_population_only'),(),None,('issuer_common_shares',)))
            except (h.InputError,ValueError) as exc:reasons.append(str(exc))
    # Multiple independently displayed occurrences are not silently selected even
    # when their numbers match; retain source candidates for explicit review.
    if improved and len(values)>1 and not reasons:
        identities={(v.as_of,v.value,v.precision,tuple((s.namespace,s.concept,s.context_id,s.unit) for s in v.sources if s.occurrence_ordinal is not None)) for v in values}
        if len(identities)==1:
            refs={s.source_id:s for v in values for s in v.sources}
            values=[replace(values[0],sources=tuple(refs.values()),selection_rationale='Confirming occurrences of the same explicitly unclassed date/context/unit population; no class summation.')]
    accepted=tuple(values) if len(values)==1 and not reasons else ()
    if not accepted and not reasons:reasons.append('Exact unclassed issuer-share cover population unavailable; absence is not zero.')
    if len(values)>1:reasons.append('Multiple cover populations require reviewed date/class coverage; no precedence.')
    return accepted,dict(role='issuer_common_shares',requirements=list(dict.fromkeys(reasons)),
        candidates=[dict(as_of=str(v.as_of),value=str(v.value),precision=v.precision,input_id=v.input_id) for v in values],
        class_dimensions=[list(v) for v in sorted(dimensions)])
