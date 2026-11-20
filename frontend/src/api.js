// One place for every call to the backend: adds the login token,
// sends/reads JSON, and turns error responses into readable messages.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8001'

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

let token = null
let onUnauthorized = () => {}

export function setToken(newToken) {
  token = newToken
}

// Called when a logged-in request gets 401 (e.g. the token expired)
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

function readableDetail(detail) {
  if (typeof detail === 'string') return detail
  // FastAPI validation errors (422) come as a list of { loc, msg }
  if (Array.isArray(detail)) {
    return detail
      .map((err) => {
        const field = err.loc?.at(-1)
        return field && field !== 'body' ? `${field}: ${err.msg}` : err.msg
      })
      .join(', ')
  }
  return null
}

export async function api(path, { method = 'GET', body } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Is the backend running?')
  }

  if (res.status === 401 && token) onUnauthorized()

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      message = readableDetail((await res.json()).detail) ?? message
    } catch {
      // response had no JSON body: keep the generic message
    }
    throw new ApiError(res.status, message)
  }

  return res.status === 204 ? null : res.json()
}
