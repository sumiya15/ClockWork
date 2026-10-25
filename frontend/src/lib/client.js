// Browser holds only the HttpOnly session cookie. No token in JS storage.
const base = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export async function api(path, { method = 'GET', body, signal } = {}) {
  const response = await fetch(`${base}${path}`, {
    method, credentials: 'include', signal,
    headers: body ? { 'Content-Type': 'application/json', 'X-ClockWork-CSRF': '1' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(data.error?.message || 'The request could not be completed.');
    error.status = response.status;
    throw error;
  }
  return data;
}
