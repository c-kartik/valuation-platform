"""One active, terminable calculation per API process; no execution queue."""

import asyncio
from dataclasses import dataclass
import multiprocessing
import time

from .worker import calculate


class ExecutionError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message
        super().__init__(code)


@dataclass
class Job:
    process: object
    connection: object
    done: object


class Calculator:
    def __init__(self, root, policy, target=calculate, target_args=()):
        self.root, self.policy = root, policy
        self.target, self.target_args = target, target_args
        self.job = None
        self.closing = False
        self.shutdown = asyncio.Event()

    async def close(self):
        self.closing = True
        self.shutdown.set()
        if self.job is not None:
            await self.job.done.wait()

    async def _reap(self, job):
        p = job.process
        if p.is_alive():
            p.terminate()
        await asyncio.to_thread(p.join, .5)
        if p.is_alive():
            p.kill()
            await asyncio.to_thread(p.join)
        job.connection.close()
        p.close()

    async def run(self, body, disconnected):
        if self.closing:
            raise ExecutionError(503, 'shutting_down', 'Service is shutting down.')
        if self.job is not None:
            raise ExecutionError(503, 'busy', 'One calculation is already running; retry later.')
        ctx = multiprocessing.get_context('spawn')
        receiver, sender = ctx.Pipe(duplex=False)
        p = ctx.Process(target=self.target, args=(sender, body, self.root, self.policy, *self.target_args), daemon=True)
        job = Job(p, receiver, asyncio.Event())
        self.job = job
        received = stop = gone = None
        started = time.monotonic()
        try:
            p.start()
            sender.close()
            received = asyncio.create_task(asyncio.to_thread(receiver.recv_bytes, max(self.policy.max_response_bytes, 8192) + 4))
            stop = asyncio.create_task(self.shutdown.wait())
            gone = asyncio.create_task(disconnected())
            done, _ = await asyncio.wait((received, stop, gone), timeout=max(0, self.policy.deadline_seconds - (time.monotonic() - started)), return_when=asyncio.FIRST_COMPLETED)
            if self.closing or stop in done:
                raise ExecutionError(503, 'shutting_down', 'Service is shutting down.')
            if gone in done:
                raise ExecutionError(499, 'client_disconnected', 'Client disconnected; calculation stopped.')
            if received not in done:
                raise ExecutionError(504, 'deadline_exceeded', 'Calculation deadline exceeded; process stopped.')
            message = received.result()
            if message[:4] not in (b'200 ', b'422 ', b'500 '):
                raise ValueError('Invalid worker message')
            if message[:4] == b'200 ' and len(message) - 4 > self.policy.max_response_bytes:
                raise ExecutionError(422, 'response_budget', 'Result exceeds HTTP execution budget.')
            return int(message[:3]), message[4:]
        except ExecutionError:
            raise
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise ExecutionError(500, 'worker_failed', 'Calculation process failed; no result returned.') from exc
        finally:
            sender.close()
            for task in (stop, gone):
                if task is not None:
                    task.cancel()
            # Finish cleanup even if the HTTP coroutine was cancelled. Closing the
            # pipe after killing the child unblocks the bounded receive thread.
            try:
                if p.pid is not None:
                    cleanup = asyncio.create_task(self._reap(job))
                    try:
                        await asyncio.shield(cleanup)
                    except asyncio.CancelledError:
                        await cleanup
                else:
                    receiver.close()
                if received is not None:
                    await asyncio.gather(received, return_exceptions=True)
                await asyncio.gather(*(t for t in (stop, gone) if t is not None), return_exceptions=True)
            finally:
                self.job = None
                job.done.set()
