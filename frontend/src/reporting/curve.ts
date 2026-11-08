/** Shape-preserving cubic Hermite segments: pass through each observation,
 * flatten at turning points, and never overshoot a segment's endpoint values.
 * Gaps start new paths. Curves are visual guides, not intermediate observations.
 */
export function smoothPath(points: readonly (readonly [number, number] | null)[]): string {
 const segments: (readonly [number, number])[][] = [];
 for (const point of points) {
  if (!point) { if (segments.at(-1)?.length) segments.push([]); }
  else { if (!segments.length) segments.push([]); segments.at(-1)!.push(point); }
 }
 return segments.filter(s=>s.length).map(p=>{
  const slopes=p.slice(1).map((v,i)=>(v[1]-p[i][1])/(v[0]-p[i][0]));
  const tangent=p.map((_,i)=>{
   if(i===0)return slopes[0]??0;
   if(i===p.length-1)return slopes[i-1];
   const a=slopes[i-1],b=slopes[i];
   return a*b<=0?0:2*a*b/(a+b);
  });
  return `M${p[0][0]},${p[0][1]}`+p.slice(1).map((v,i)=>{
   const dx=(v[0]-p[i][0])/3;
   return ` C${p[i][0]+dx},${p[i][1]+dx*tangent[i]} ${v[0]-dx},${v[1]-dx*tangent[i+1]} ${v[0]},${v[1]}`;
  }).join('');
 }).join(' ');
}
