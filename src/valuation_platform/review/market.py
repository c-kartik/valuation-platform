"""Documented Massive REST adapter; fail closed without explicit entitlement.

One bounded fetch per review; never called by a valuation worker. No persistent
cache, browser key, automatic subscription, or website scraping.
"""
from datetime import datetime,timedelta,time
from decimal import Decimal
import hashlib,json,os,urllib.request,urllib.error
from zoneinfo import ZoneInfo
from .sources import MarketOpening
NY=ZoneInfo('America/New_York')

class MarketUnavailable(ValueError):pass

class MassiveProvider:
    def __init__(self,key=None,permitted=False,delay=None,fetch=None):
        self.key=key;self.permitted=permitted;self.delay=delay;self.fetch=fetch or self._get
    @classmethod
    def configured(cls):
        return cls(os.environ.get('MASSIVE_API_KEY'),os.environ.get('MARKET_LOCAL_DISPLAY_ENTITLED')=='yes',os.environ.get('MASSIVE_DATA_DELAY'))
    def _get(self,path):
        request=urllib.request.Request('https://api.massive.com'+path,headers={'Authorization':'Bearer '+self.key,'Accept':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=8) as response:
                raw=response.read(512*1024+1)
                if len(raw)>512*1024:raise MarketUnavailable('Market response too large')
                return json.loads(raw,parse_float=Decimal)
        except urllib.error.HTTPError as exc:
            if exc.code==404:return {'status':'NOT_FOUND'}
            raise MarketUnavailable('Market source unavailable; retry explicitly') from None
        except Exception:raise MarketUnavailable('Market source unavailable; retry explicitly') from None
    def opening(self,ticker,now):
        if ticker not in ('META','GOOGL','AAPL'):raise MarketUnavailable('Unsupported company')
        if not self.key or not self.permitted or not self.delay:
            raise MarketUnavailable('Opening-price reference unavailable: configure a market-data key, permitted local-display entitlement and documented plan delay.')
        if now.tzinfo is None:raise ValueError('Aware check timestamp required')
        local=now.astimezone(NY);today=local.date()
        # At/after the regular open, try today's documented regular-session summary.
        if local.weekday()<5 and local.time()>=time(9,30):
            data=self.fetch(f'/v1/open-close/{ticker}/{today}?adjusted=false')
            if data.get('status')=='OK':return self.decode(ticker,data,now,'Latest available session',today)
        # Returned session bars establish dates (including weekends/holidays), not
        # regular-opening prices: fetch the documented open-close summary for that date.
        start=today-timedelta(days=14)
        bars=self.fetch(f'/v2/aggs/ticker/{ticker}/range/1/day/{start}/{today}?adjusted=false&sort=desc&limit=14')
        if bars.get('ticker')!=ticker or bars.get('adjusted') is not False:raise MarketUnavailable('Unexpected market series identity/adjustment')
        dates=sorted({datetime.fromtimestamp(int(x['t'])/1000,NY).date() for x in bars.get('results',[])},reverse=True)
        dates=[d for d in dates if d<today]
        if not dates:raise MarketUnavailable('No supported prior opening observation in bounded 14-day window')
        data=self.fetch(f'/v1/open-close/{ticker}/{dates[0]}?adjusted=false')
        return self.decode(ticker,data,now,'Previous available session; today’s regular opening observation unavailable',dates[0])
    def decode(self,ticker,data,now,fallback,expected_date=None):
        try:
            if data.get('status')!='OK' or data.get('symbol')!=ticker or data.get('adjusted',False) is not False:raise ValueError()
            # Explicit unadjusted=false request governs response; the daily summary
            # supplies regular open separately from preMarket/afterHours.
            from datetime import date
            day=date.fromisoformat(data['from']);observed=datetime.combine(day,time(9,30),NY)
            if expected_date is not None and day!=expected_date:raise ValueError()
            if observed>now:raise ValueError()
            price=Decimal(str(data['open']));url=f'https://api.massive.com/v1/open-close/{ticker}/{day}?adjusted=false'
            canonical=json.dumps(data,sort_keys=True,default=str).encode()
            return MarketOpening(ticker,price,day,observed,now,url,hashlib.sha256(canonical).hexdigest(),self.delay,fallback,
                {'META':'Class A','GOOGL':'Class A','AAPL':'Common'}[ticker])
        except (ValueError,KeyError,TypeError):raise MarketUnavailable('Invalid or unavailable regular-session opening observation') from None
