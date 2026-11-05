import {D,SolverDecimal as S,clone,number,keys,requireInput,text,day,type Doc} from './decimal';
import {runCase,selectedMethod,type EngineData} from './case';
import {sourceCase} from './scenarios';

const gcd=(a:bigint,b:bigint):bigint=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){const r=a%b;a=b;b=r;}return a;};
// Exact fractions are used for mathematical certification only, never money output.
class Q {
 n:bigint;d:bigint;
 constructor(n:bigint|number|string,d:bigint=1n){let a:bigint;
  if(typeof n==='string'){const [mantissa,exp='0']=n.toLowerCase().split('e'),parts=mantissa.split('.'),places=(parts[1]?.length??0)-Number(exp);a=BigInt(parts.join(''));if(places>=0)d=10n**BigInt(places);else a*=10n**BigInt(-places);}else a=BigInt(n);
  requireInput(d!==0n,'exact rational: division by zero');if(d<0n){a=-a;d=-d;}const g=gcd(a,d);this.n=a/g;this.d=d/g;
 }
 add(b:Q){return new Q(this.n*b.d+b.n*this.d,this.d*b.d);}neg(){return new Q(-this.n,this.d);}sub(b:Q){return this.add(b.neg());}mul(b:Q){return new Q(this.n*b.n,this.d*b.d);}div(b:Q){return new Q(this.n*b.d,this.d*b.n);}pow(n:number){return new Q(this.n**BigInt(n),this.d**BigInt(n));}cmp(b:Q){const n=this.n*b.d-b.n*this.d;return n<0n?-1:n>0n?1:0;}json(){return {numerator:String(this.n),denominator:String(this.d)};}
 exactDigits(){let d=this.d,two=0,five=0;while(d%2n===0n){d/=2n;two++;}while(d%5n===0n){d/=5n;five++;}if(d!==1n)return Infinity;const places=Math.max(two,five);let n=(this.n<0n?-this.n:this.n)*2n**BigInt(places-two)*5n**BigInt(places-five);while(n!==0n&&n%10n===0n)n/=10n;return String(n).length;}
}
const q=(v:any)=>new Q(String(v));const qsum=(a:Q[])=>a.reduce((x,y)=>x.add(y),q(0));
function fixedCash(revenue:Q,r:Doc):Q{
 const ebit=revenue.mul(q(r.operating_margin)),tax=(ebit.n>0n?ebit:q(0)).mul(q(r.forecast_tax_rate??r.operating_tax_rate));
 const terms=[ebit,tax,revenue.mul(q(r.d_and_a_percent_revenue)),revenue.mul(q(r.capex_percent_revenue??r.investment_percent_revenue)),revenue.mul(q(r.change_in_operating_nwc_percent_revenue??r.working_capital_cash_requirement_percent_revenue))];
 requireInput(terms.every(x=>x.exactDigits()<=512),'Exact operating components exceed precision cap');return terms[0].sub(terms[1]).add(terms[2]).sub(terms[3]).sub(terms[4]);
}
function comb(n:number,k:number):number{let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return v;}
function certificate(doc:Doc,c:Doc,reference:Doc){
 const w=q(c.wacc),g=q(selectedMethod(c).terminal_growth),seed=q(reference.stage_b.stage_a.anchor.revenue),one=q(1),fixed=c.forecast_years.map((r:Doc)=>fixedCash(seed,r)),terminal=fixedCash(seed.mul(one.add(g)),selectedMethod(c).terminal);
 const coeff:Q[]=[q(0),...fixed.map((v:Q,i:number)=>v.div(one.add(w).pow(i+1)))];coeff[5]=coeff[5].add(terminal.div(w.sub(g)).div(one.add(w).pow(5)));
 if(doc.target.metric==='VALUE_PER_SHARE'){coeff[0]=qsum(reference.stage_c.contributions.map((x:Doc)=>q(x.signed_contribution)));const shares=q(reference.stage_c.valuation_shares);for(let i=0;i<coeff.length;i++)coeff[i]=coeff[i].div(shares);}
 const a=one.add(q(doc.growth_bounds.lower)),b=one.add(q(doc.growth_bounds.upper)),derivative=coeff.slice(1).map((v,i)=>v.mul(q(i+1)));
 const powers=Array.from({length:5},(_,k)=>qsum(Array.from({length:5-k},(_,off)=>{const j=k+off;return derivative[j].mul(q(comb(j,k))).mul(a.pow(j-k)).mul(b.sub(a).pow(k));})));
 const bernstein=Array.from({length:5},(_,k)=>qsum(Array.from({length:k+1},(_,j)=>powers[j].mul(new Q(comb(k,j))).div(q(comb(4,j))))));
 const sorted=[...bernstein].sort((x,y)=>x.cmp(y)),lower=sorted[0],upper=sorted.at(-1)!,direction=bernstein.every(v=>v.n===0n)?'FLAT':lower.n>=0n?'INCREASING':upper.n<=0n?'DECREASING':'NOT_CERTIFIED';
 return {coeff,evidence:{method:'exact-rational-bernstein-derivative-v1',direction,variable:'x = 1 + constant annual growth',x_interval:[a.json(),b.json()],polynomial_coefficients_ascending:coeff.map(v=>v.json()),derivative_bernstein_coefficients:bernstein.map(v=>v.json()),derivative_enclosure:[lower.json(),upper.json()],reason:['INCREASING','DECREASING'].includes(direction)?'All derivative Bernstein coefficients share a weak sign, at least one strict: derivative has that strict sign throughout the open interval, hence strict monotonicity including endpoints.':direction==='FLAT'?'Exact derivative is identically zero: no unique solution.':'Derivative enclosure straddles zero. Uniqueness is unsupported; multiple roots are not proven. No sampled-monotonicity fallback.',component_source:'Shared _operating_year at fixed anchor revenue with Inexact trapped; exact rational discount/timing homogeneity and engine signed bridge components. Proof only; every reported valuation uses run_case.'}};
}
export function validateReverse(doc:Doc,data:EngineData){
 keys(doc,['schema_version','reverse_dcf_name','source','target','growth_bounds'],'reverse');requireInput(['analyst-reverse-dcf-request-v1','investor-reverse-dcf-request-v1','investor-reverse-dcf-request-v2'].includes(doc.schema_version),'reverse: unsupported schema');text(doc.reverse_dcf_name,'reverse_dcf_name');
 const source=sourceCase(doc,data,doc.schema_version==='investor-reverse-dcf-request-v2');const c=source.case;
 requireInput(c.forecast_years.length===5&&selectedMethod(c).method==='perpetual_growth','reverse: certified solve supports five-year perpetual growth only');
 if(doc.schema_version.startsWith('investor'))requireInput(['investor-case-v1','investor-case-v2'].includes(c.schema_version),'reverse: investor v1/v2 case required');
 keys(doc.target,['metric','amount','unit','date'],'target');requireInput(['ENTERPRISE_VALUE','VALUE_PER_SHARE'].includes(doc.target.metric),'target.metric: unsupported metric');number(doc.target.amount,'target.amount');day(doc.target.date,'target.date');requireInput(doc.target.date===source.selection.analytical_date,'target.date: analytical date must match');requireInput(doc.target.unit===(doc.target.metric==='ENTERPRISE_VALUE'?'USD':'USD/share'),'target.unit: incompatible units');requireInput(doc.target.metric!=='VALUE_PER_SHARE'||c.bridge,'target.metric: complete equity/share case required');
 keys(doc.growth_bounds,['lower','upper'],'growth_bounds');const lo=number(doc.growth_bounds.lower,'growth_bounds.lower',-1),hi=number(doc.growth_bounds.upper,'growth_bounds.upper',-1);requireInput(lo.lt(hi),'growth_bounds: lower must precede upper');return source;
}
export function runReverse(doc:Doc,data:EngineData):Doc{
 const {case:c,selection}=validateReverse(doc,data),reference=runCase(c,data);let evaluations=1;
 let cert;try{cert=certificate(doc,c,reference);}catch{cert={coeff:[] as Q[],evidence:{direction:'UNSUPPORTED',reason:'Shared operating components could not be established exactly within precision cap; no claim of multiple roots.'}};}
 const {coeff,evidence}=cert;const result:Doc={schema_version:doc.schema_version.replace('-request-','-results-'),reverse_dcf_name:doc.reverse_dcf_name,submitted_inputs:clone(doc),selected_case:clone(c),selection:{scenario_label:selection.scenario_label,analytical_date:selection.analytical_date,information_cutoff:selection.information_cutoff},original_growth_path:c.forecast_years.map((y:Doc)=>y.revenue_growth),reference_result:reference,...clone(data.metadata.reverse),monotonicity:evidence,iterations:0,evaluations,status:null,reason:null,solution:null,final_bracket:null,semantic_input_review:'NOT_ASSESSED_BY_CALCULATOR'};
 const finish=(status:string,reason:string,bracket:any=null,solution:any=null)=>({...result,status,reason,evaluations,final_bracket:bracket,solution});
 if(evidence.direction==='FLAT')return finish('FLAT_RESPONSE',evidence.reason);if(!['INCREASING','DECREASING'].includes(evidence.direction))return finish('UNIQUENESS_NOT_CERTIFIED',evidence.reason);
 const target=new S(doc.target.amount),atol=new S(doc.target.metric==='ENTERPRISE_VALUE'?'1e-8':'1e-10'),rtol=new S('1e-12'),gtol=new S('1e-12');
 const proof=(g:any)=>{const x=q(1).add(q(g));return qsum(coeff.map((v,i)=>v.mul(x.pow(i)))).sub(q(doc.target.amount));};
 const evaluate=(g:any):[InstanceType<typeof S>,Doc]=>{const d=clone(c);d.forecast_years.forEach((y:Doc)=>y.revenue_growth=g.toString());const r=runCase(d,data);evaluations++;return [new S(doc.target.metric==='ENTERPRISE_VALUE'?r.stage_b.enterprise_value:r.stage_c.value_per_share),r];};
 const bracket=(lo:any,hi:any,lv:any,hv:any)=>({lower_growth:lo.toString(),upper_growth:hi.toString(),width:hi.minus(lo).toString(),lower_achieved_metric:lv.toString(),upper_achieved_metric:hv.toString()});
 const verified=(g:any,lo:any,hi:any,lv:any,hv:any,endpoint=false)=>{const [achieved,forward]=evaluate(g),residual=achieved.minus(target),tolerance=atol.plus(rtol.times(S.max(target.abs(),achieved.abs()))),left=proof(lo),right=proof(hi);const exists=(left.n<=0n&&right.n>=0n)||(right.n<=0n&&left.n>=0n);if(!exists||residual.abs().gt(tolerance)||(!endpoint&&hi.minus(lo).gt(gtol)))return finish('NUMERICAL_VERIFICATION_FAILED','Fresh residual, exact final-bracket existence or growth-width check failed; no solution exposed.',bracket(lo,hi,lv,hv));return finish('SUCCESS','Unique mathematical solution certified; fresh existing-engine valuation meets residual and growth-bracket policy.',bracket(lo,hi,lv,hv),{constant_annual_growth:g.toString(),achieved_metric:achieved.toString(),signed_residual:residual.toString(),absolute_residual:residual.abs().toString(),residual_tolerance:tolerance.toString(),exact_endpoint:endpoint,forward_result:forward});};
 let lo=new S(doc.growth_bounds.lower),hi=new S(doc.growth_bounds.upper),[lv]=evaluate(lo),[hv]=evaluate(hi);const left=proof(lo),right=proof(hi);
 if(left.n===0n)return verified(lo,lo,lo,lv,lv,true);if(right.n===0n)return verified(hi,hi,hi,hv,hv,true);
 if((left.n>0n&&right.n>0n)||(left.n<0n&&right.n<0n))return finish('UNREACHABLE_TARGET','Certified monotone mathematical endpoint values do not bracket the target; no nearest-bound solution.',bracket(lo,hi,lv,hv));
 const increasing=evidence.direction==='INCREASING';for(let i=1;i<=128;i++){result.iterations=i;const mid=lo.plus(hi).div(2);if(mid.eq(lo)||mid.eq(hi))return finish('NUMERICAL_VERIFICATION_FAILED','Solver precision cannot shrink growth bracket further.',bracket(lo,hi,lv,hv));const [mv]=evaluate(mid);
  if(hi.minus(lo).lte(gtol)&&mv.minus(target).abs().lte(atol.plus(rtol.times(S.max(target.abs(),mv.abs())))))return verified(mid,lo,hi,lv,hv);
  if(mv.eq(target)){lo=S.max(lo,mid.minus(gtol.div(4)));hi=S.min(hi,mid.plus(gtol.div(4)));[lv]=evaluate(lo);[hv]=evaluate(hi);return verified(mid,lo,hi,lv,hv);}
  if(mv.lt(target)===increasing){lo=mid;lv=mv;}else{hi=mid;hv=mv;}
 }
 return finish('ITERATION_LIMIT','Iteration limit reached before both acceptance tests; no approximate solution exposed.',bracket(lo,hi,lv,hv));
}
