import {test} from 'node:test';
import assert from 'node:assert/strict';
import {hasRecognizableSecret} from './public-asset-checks.mjs';
test('rejects private key headers including unencrypted, RSA, EC, OpenSSH and encrypted keys',()=>{
 for(const type of ['','RSA ','EC ','OPENSSH ','ENCRYPTED '])assert.equal(hasRecognizableSecret(`prefix -----BEGIN ${type}PRIVATE KEY-----\nbody`),true);
});
test('rejects recognizable API token formats',()=>{
 assert.equal(hasRecognizableSecret('AIza'+'a'.repeat(30)),true);
 for(const kind of ['p','o','u','s','r'])assert.equal(hasRecognizableSecret('gh'+kind+'_'+'a'.repeat(20)),true);
});
test('does not mistake a public crypto parser regex and later case label for key material',()=>{
 assert.equal(hasRecognizableSecret('const header=/-----BEGIN ((?:.*? KEY)|CERTIFICATE)-----/; switch(tag){case "PRIVATE KEY": break;}'),false);
 assert.equal(hasRecognizableSecret('Ordinary model data and worksheet values'),false);
});
