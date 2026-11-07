/** PEM header names are bounded tokens, not arbitrary minified JavaScript. */
export function hasRecognizableSecret(text){
 return /-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY|AIza[0-9A-Za-z_-]{30}|gh[pousr]_[0-9A-Za-z]{20}/.test(text);
}
