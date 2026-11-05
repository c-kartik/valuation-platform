/** Offline integrity and Python preservation check; does not import Python. */
import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const read=path=>readFile(resolve(root,path));
const json=async path=>JSON.parse(await read(path));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const prefix='frontend/public/browser-data/';
const manifest=await json(prefix+'manifest.json');
for(const [path,expected]of Object.entries(manifest.files))if(digest(await read(prefix+path))!==expected)throw Error('Asset hash mismatch: '+path);
for(const [route,path]of Object.entries(manifest.routes))if(!route.startsWith('/api/v1/')||!manifest.files[path])throw Error('Invalid route binding: '+route);
const baselinePath='scripts/browser-migration/python-source-baseline.json';
if(digest(await read(baselinePath))!==manifest.python_baseline_sha256)throw Error('Python baseline snapshot changed');
const snapshot=await json(baselinePath);
for(const [path,expected]of Object.entries(snapshot.files))if(digest(await read(path))!==expected)throw Error('Existing Python file changed: '+path);
const fixturePath='frontend/src/browser-engine/fixtures/parity.json';
if(digest(await read(fixturePath))!==manifest.fixture_sha256)throw Error('Parity fixtures changed');
const fixtures=await json(fixturePath);
if(fixtures.length!==manifest.fixture_count)throw Error('Fixture count differs');
for(const fixture of fixtures)if(!fixture.name||!fixture.path||!fixture.body||!fixture.expected||![200,422].includes(fixture.status))throw Error('Malformed fixture');
let extraCount=0;
try{
 const extraPrefix='frontend/src/browser-engine/fixtures/';
 const extra=await json(extraPrefix+'extra-parity-manifest.json');
 const bytes=await read(extraPrefix+'extra-parity.json');
 if(digest(bytes)!==extra.sha256||JSON.parse(bytes).length!==extra.fixture_count)throw Error('Extra parity fixture hash/count mismatch');
 extraCount=extra.fixture_count;
}catch(error){if(error.code!=='ENOENT')throw error;}
console.log(JSON.stringify({verified_assets:Object.keys(manifest.files).length,verified_python_files:Object.keys(snapshot.files).length,verified_fixtures:fixtures.length,verified_extra_fixtures:extraCount}));
