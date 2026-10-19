export class ApiError extends Error {
  constructor(public code: string, message: string, public details: string[] = []) { super(message); }
}
export async function request<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, {once: true});
  if (signal?.aborted) controller.abort();
  const timer = setTimeout(() => controller.abort(), 50000);
  try {
    const response = await fetch(path, {
      method: body === undefined ? 'GET' : 'POST', signal: controller.signal,
      headers: body === undefined ? undefined : {'Content-Type': 'application/json'},
      body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store', credentials: 'omit',
    });
    const data = await response.json();
    if (!response.ok) throw new ApiError(data.error?.code ?? 'http_error', data.error?.message ?? 'Request failed.', data.error?.details ?? []);
    return data as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    if (controller.signal.aborted) throw new ApiError('request_cancelled', 'Request cancelled or local request deadline reached. Entries are preserved; retry explicitly.');
    throw new ApiError('connection_error', 'Cannot reach the local API or read its response. Check both servers; entries are preserved.');
  } finally {
    clearTimeout(timer); signal?.removeEventListener('abort', abort);
  }
}
// Revision tokens protect even when a transport ignores abort or replies out of order.
export class Revisions {
  private revision = 0;
  private sequence = 0;
  edit() { this.revision++; this.sequence++; }
  begin() { return {revision: this.revision, sequence: ++this.sequence}; }
  current(token: {revision: number; sequence: number}) { return token.revision === this.revision && token.sequence === this.sequence; }
}
