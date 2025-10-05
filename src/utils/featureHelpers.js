// src/utils/featureHelpers.js
// Note: Keep this exactly matching training feature pipeline.
export function makeUrlFeatures(rawUrl) {
  try {
    const u = new URL(rawUrl);
    const host = (u.hostname || "").toLowerCase();
    const path = u.pathname || "";
    const q = u.search || "";

    const length = Math.min(rawUrl.length, 512) / 512;
    const countDots = (host.match(/\./g) || []).length / 5;
    const hasIP = /^\d+\.\d+\.\d+\.\d+$/.test(host) ? 1 : 0;
    const hasLogin = /(login|verify|secure|account|update|confirm)/i.test(rawUrl) ? 1 : 0;
    const countHyphen = (host.match(/-/g) || []).length / 5;
    const hasAt = rawUrl.includes("@") ? 1 : 0;
    const punycode = host.includes("xn--") ? 1 : 0;
    const pathLen = Math.min(path.length, 200) / 200;
    const params = new URLSearchParams(q);
    const numParams = params.toString().length ? [...params].length / 10 : 0;

    const freq = {};
    for (let c of host) freq[c] = (freq[c] || 0) + 1;
    let ent = 0;
    const L = host.length || 1;
    for (let k in freq) {
      const p = freq[k] / L;
      ent -= p * Math.log2(p);
    }
    const entropy = Math.min(ent / 8, 1);

    return [length, countDots, hasIP, hasLogin, countHyphen, hasAt, punycode, pathLen, numParams, entropy];
  } catch (e) {
    return new Array(10).fill(0);
  }
}

