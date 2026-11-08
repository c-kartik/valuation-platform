import {expect,it} from 'vitest';
import {smoothPath} from './curve';
it('passes through observations without introducing overshoot or joining missing data',()=>{
 const points=[[0,0],[10,10],[20,-5],[30,-5],[40,7]] as const;
 const path=smoothPath(points),parts=[...path.matchAll(/C([\d.,e+\- ]+)/g)];
 expect(parts).toHaveLength(4);
 parts.forEach((part,i)=>{
  const [x1,y1,x2,y2,x3,y3]=part[1].split(/[ ,]+/).map(Number),a=points[i],b=points[i+1];
  expect([x3,y3]).toEqual(b);
  for(let j=0;j<=100;j++){
   const t=j/100,u=1-t,y=u*u*u*a[1]+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3;
   expect(y).toBeGreaterThanOrEqual(Math.min(a[1],b[1])-1e-10);
   expect(y).toBeLessThanOrEqual(Math.max(a[1],b[1])+1e-10);
  }
  expect(x1).toBeGreaterThan(a[0]);expect(x2).toBeLessThan(b[0]);
 });
 expect(smoothPath([[0,0],null,[2,2],[3,1]]).match(/M/g)).toHaveLength(2);
 expect(smoothPath([])).toBe('');
});
