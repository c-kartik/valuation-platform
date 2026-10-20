import {cleanup} from '@testing-library/react';
import {afterEach} from 'vitest';
// jsdom lacks native dialog operations. Focus containment/Escape are verified
// in the actual browser; this shim only exposes open/close state to unit tests.
HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open',''); };
HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); };
afterEach(cleanup);
