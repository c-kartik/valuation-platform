import {cleanup} from '@testing-library/react';
import {afterEach,vi} from 'vitest';
// jsdom lacks native dialog operations. Focus containment/Escape are verified
// in the actual browser; this shim only exposes open/close state to unit tests.
HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open',''); };
HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
afterEach(cleanup);

// Object-URL lifecycle is explicitly asserted by export tests; jsdom has no downloader.
if(!URL.createObjectURL)URL.createObjectURL=()=> 'blob:offline-test';
if(!URL.revokeObjectURL)URL.revokeObjectURL=()=>{};

// jsdom has no layout/scroll implementation; modal scroll restoration is tested by calls.
window.scrollTo=vi.fn();

HTMLElement.prototype.scrollIntoView=vi.fn();
