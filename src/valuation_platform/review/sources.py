"""Immutable source-bound data types. None of these declarations grants approval."""
from dataclasses import dataclass, asdict
from datetime import date, datetime
from decimal import Decimal
import hashlib,json
from pathlib import Path

@dataclass(frozen=True)
class MarketOpening:
    ticker: str
    price: Decimal
    session_date: date
    observed_at: datetime
    retrieved_at: datetime
    source_url: str
    source_id: str
    delay: str
    fallback: str
    share_class: str
    adjustment: str = 'UNADJUSTED'
    timezone: str = 'America/New_York'
    currency: str = 'USD'
    split_compatible: bool = False

    def __post_init__(self):
        if self.ticker not in ('META','GOOGL','AAPL'):raise ValueError('Unsupported company')
        if type(self.price) is not Decimal or not self.price.is_finite() or self.price<=0:raise ValueError('Positive Decimal opening price required')
        if self.adjustment!='UNADJUSTED' or self.timezone!='America/New_York' or self.currency!='USD':raise ValueError('Unsupported price/unit/timezone convention')
        if self.observed_at.tzinfo is None or self.retrieved_at.tzinfo is None:raise ValueError('Aware timestamps required')
        if self.observed_at>self.retrieved_at:raise ValueError('Future observation')
        if self.session_date!=self.observed_at.astimezone(__import__('zoneinfo').ZoneInfo(self.timezone)).date():raise ValueError('Session date mismatch')
        if not self.source_url.startswith('https://api.massive.com/') or not self.source_id or not self.delay:raise ValueError('Source and delay required')
        if type(self.split_compatible) is not bool:raise ValueError('Explicit split status required')

    def to_dict(self):
        return {k:str(v) if isinstance(v,Decimal) else v.isoformat() if isinstance(v,(date,datetime)) else v for k,v in asdict(self).items()}

    @classmethod
    def from_dict(cls,value):
        if type(value) is not dict:raise ValueError('Market snapshot required')
        d=dict(value);d['price']=Decimal(d['price']);d['session_date']=date.fromisoformat(d['session_date'])
        for k in ('observed_at','retrieved_at'):d[k]=datetime.fromisoformat(d[k])
        return cls(**d)

@dataclass(frozen=True)
class ReportedObservation:
    field: str
    concept: str
    amount: Decimal
    unit: str
    start: date | None
    end: date
    accession: str
    filed: date
    source_reference: str
    precision: str | None

    @classmethod
    def from_dict(cls,value):
        if value.get('classification')!='REPORTED' or type(value.get('amount'))is not str or type(value.get('scale'))is not int or value['scale']!=1:raise ValueError('Explicit reported amount/unit/scale required')
        amount=Decimal(value['amount'])
        if not amount.is_finite() or value['unit']not in ('USD','shares'):raise ValueError('Finite supported observation required')
        start=date.fromisoformat(value['start'])if value['start']else None;end=date.fromisoformat(value['end'])
        if start and start>end:raise ValueError('Invalid observation period')
        if not value['source_reference'].startswith('https://data.sec.gov/api/xbrl/companyfacts/'):raise ValueError('SEC observation reference required')
        return cls(value['field'],value['concept'],amount,value['unit'],start,end,value['accession'],date.fromisoformat(value['filed']),value['source_reference'],value['precision'])

@dataclass(frozen=True)
class FinancialContext:
    company: str
    cik: int
    financials_through: date
    filed: date
    accepted_at: datetime | None
    checked_at: datetime
    observations: tuple[ReportedObservation, ...]
    source_json: str
    snapshot_id: str

    @classmethod
    def read(cls,path:Path):
        raw=path.read_bytes();doc=json.loads(raw)
        companies={'META':1326801,'GOOGL':1652044,'AAPL':320193}
        if doc['schema_version']!='investor-financial-context-v1' or companies.get(doc['company'])!=doc['cik'] or doc['valuation_anchor_approved']is not False or doc['information_cutoff']is not None:raise ValueError('Invalid context or implied approval')
        end=date.fromisoformat(doc['financials_through']);filed=date.fromisoformat(doc['filed']);checked=datetime.fromisoformat(doc['checked_at']);accepted=datetime.fromisoformat(doc['accepted_at'].replace('Z','+00:00'))if doc['accepted_at']else None
        if checked.tzinfo is None or accepted and (accepted.tzinfo is None or accepted>checked):raise ValueError('Invalid publication/check chronology')
        observations=tuple(ReportedObservation.from_dict(item)for item in doc['observations'])
        if any(o.accession!=doc['accession']for o in observations):raise ValueError('Observation filing mismatch')
        for source in doc['sources']:
            if not source['url'].startswith('https://data.sec.gov/')or len(source['sha256'])!=64 or any(c not in '0123456789abcdef'for c in source['sha256']):raise ValueError('SEC source receipt required')
            timestamp=datetime.fromisoformat(source['checked_at'])
            if timestamp.tzinfo is None or timestamp>checked:raise ValueError('Source check chronology mismatch')
        return cls(doc['company'],doc['cik'],end,filed,accepted,checked,observations,raw.decode(),hashlib.sha256(raw).hexdigest())

    def to_dict(self):return {**json.loads(self.source_json),'snapshot_id':self.snapshot_id}
