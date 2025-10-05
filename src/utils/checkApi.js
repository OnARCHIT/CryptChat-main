// src/utils/checkApi.js
export async function checkUrlWithApi(endpoint, url, timeoutMs = 8000) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${endpoint}?url=${encodeURIComponent(url)}`, {
      method: "GET",
      signal: controller.signal,
    });
    clearTimeout(t);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    clearTimeout(t);
    return { error: true, message: err.message || err.name };
  }
}

export async function checkFileWithApi(endpoint, file, timeoutMs = 20000) {
  const form = new FormData();
  form.append("file", file);
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      body: form,
      signal: controller.signal,
    });
    clearTimeout(t);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    clearTimeout(t);
    return { error: true, message: err.message || err.name };
  }
}
