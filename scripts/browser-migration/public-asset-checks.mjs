/** PEM header names are bounded tokens, not arbitrary minified JavaScript. */
export function hasRecognizableSecret(text){
 return /-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY|AIza[0-9A-Za-z_-]{30}|gh[pousr]_[0-9A-Za-z]{20}/.test(text);
}
/** Browser network dependencies, excluding Browserify's internal require maps. */
export function javascriptAssetReferences(text){
 const patterns=[
  /\b(?:import|export)\s*(?:\{[^}]*\}|\*\s*(?:as\s+[\w$]+)?|[\w$]+(?:\s*,\s*(?:\{[^}]*\}|\*\s+as\s+[\w$]+))?)\s*from\s*["'`]([^"'`]+)["'`]/g,
  /\bimport\s*["'`]([^"'`]+)["'`]/g,
  /\bimport\s*\(\s*["'`]([^"'`]+)["'`]/g,
  /\bnew\s+URL\(\s*["'`]([^"'`]+)["'`]\s*,\s*import\.meta\.url/g,
 ];
 return [...new Set(patterns.flatMap(pattern=>[...text.matchAll(pattern)].map(m=>m[1])).filter(ref=>/^\.{0,2}\//.test(ref)&&/\.(?:js|mjs|css)(?:\?[^\s]*)?$/.test(ref)))];
}
