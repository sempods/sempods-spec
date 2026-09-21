#!/usr/bin/env node
// Bounded SDK/fixture experiment, not a pod conformance suite. See repository-checks.md.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const sdk = resolve(process.argv[2] ?? '');
assert.equal(JSON.parse(readFileSync(resolve(sdk, 'package.json'))).version, '1.30.0');
const module = path => import(pathToFileURL(resolve(sdk, 'dist/esm', path)));
const { Client } = await module('client/index.js');
const { StreamableHTTPClientTransport } = await module('client/streamableHttp.js');
const { auth } = await module('client/auth.js');
const { OAuthMetadataSchema, OAuthProtectedResourceMetadataSchema } = await module('shared/auth.js');
const { LATEST_PROTOCOL_VERSION } = await module('types.js');
assert.equal(LATEST_PROTOCOL_VERSION, '2025-11-25');

const suffix = '/_system/mcp';
const pod = 'https://example.org/alice';
const otherPod = 'https://example.org/bob';
const resourceMetadataUrl = p => p + '/.well-known/oauth-protected-resource';
const authorizationMetadataUrl = p => p + '/.well-known/oauth-authorization-server';
const records = [];

function fixture(p, changes = {}) {
  const endpoint = p + suffix;
  const trace = [];
  const resource = {
    resource: changes.resource ?? p,
    authorization_servers: changes.servers ?? [p],
    bearer_methods_supported: ['header'],
    unknown_optional_field: true
  };
  const metadata = {
    issuer: changes.issuer ?? p,
    authorization_endpoint: p + '/_system/auth/authorize',
    token_endpoint: p + '/_system/auth/token',
    registration_endpoint: p + '/_system/auth/register',
    response_types_supported: ['code'], grant_types_supported: ['authorization_code'],
    token_endpoint_auth_methods_supported: ['none'], code_challenge_methods_supported: ['S256']
  };
  const json = (body, status = 200, headers = {}) => new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json', ...headers }
  });
  const fetch = async (input, init = {}) => {
    const url = String(input), method = init.method ?? 'GET';
    const message = url === endpoint && method === 'POST' ? JSON.parse(init.body) : undefined;
    trace.push({ method, url, ...(message ? { rpc: message.method } : {}) });
    if (message?.method === 'initialize') return json({ jsonrpc: '2.0', id: message.id, result: {
      protocolVersion: LATEST_PROTOCOL_VERSION, capabilities: { tools: {} },
      serverInfo: { name: 'scripted-spec-fixture', version: '1' }
    } });
    if (message?.method === 'notifications/initialized') return new Response(null, { status: 202 });
    if (message) return json({ jsonrpc: '2.0', id: message.id,
      error: { code: -32001, message: 'Authorization required' }
    }, 401, { 'WWW-Authenticate': `Bearer realm="${p}", resource_metadata="${changes.hint ?? resourceMetadataUrl(p)}"` });
    const u = new URL(p);
    const rootResource = u.origin + '/.well-known/oauth-protected-resource' + u.pathname.replace(/\/$/, '') + suffix;
    const rootAuthorization = u.origin + '/.well-known/oauth-authorization-server' + u.pathname.replace(/\/$/, '');
    if (url === resourceMetadataUrl(p) || changes.legacyAlias && url === endpoint + '/.well-known/oauth-protected-resource'
      || changes.hostAliases && url === rootResource) {
      if (changes.unavailable) return new Response(null, { status: 404 });
      if (changes.redirect) return new Response(null, { status: 302, headers: { Location: resourceMetadataUrl(otherPod) } });
      return json(resource);
    }
    if (url === authorizationMetadataUrl(p) || changes.hostAliases && url === rootAuthorization) return json(metadata);
    if (url === metadata.registration_endpoint && method === 'POST') return json({
      ...JSON.parse(init.body), client_id: 'dyn:fixture'
    }, 201);
    return new Response(null, { status: 404 });
  };
  return { fetch, trace };
}

function provider() {
  let information, verifier;
  const redirects = [];
  return {
    redirects,
    redirectUrl: 'http://localhost:12345/callback',
    clientMetadata: { redirect_uris: ['http://localhost:12345/callback'],
      token_endpoint_auth_method: 'none', grant_types: ['authorization_code'], response_types: ['code'] },
    clientInformation: () => information,
    saveClientInformation: value => { information = value; },
    tokens: () => undefined, saveTokens: () => {},
    saveCodeVerifier: value => { verifier = value; }, codeVerifier: () => verifier,
    state: () => 'fixture-state',
    redirectToAuthorization: url => { redirects.push(url); }
  };
}

// This adapter is the supplied sempods model, not behavior built into the SDK. It establishes
// identity before fetching metadata and uses the SDK's public provider hooks for validated state.
function sempodsProfile(endpoint, f, p) {
  const url = new URL(endpoint);
  assert.equal(url.href, endpoint, 'canonical endpoint required');
  assert(!url.username && !url.password && !url.search && !url.hash, 'endpoint components');
  assert(endpoint.endsWith(suffix), 'literal MCP suffix');
  const base = endpoint.slice(0, -suffix.length);
  assert(!base.endsWith('/'), 'pod base has no trailing slash');
  const u = new URL(base);
  assert(u.protocol === 'https:' || u.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(u.hostname));
  const prm = resourceMetadataUrl(base), asm = authorizationMetadataUrl(base);
  const fetch = async (input, init = {}) => {
    const response = await f.fetch(input, init);
    if (String(input) === endpoint && response.status === 401) {
      // The fixture emits one quoted hint; compare its original spelling before SDK URL parsing.
      const hint = /resource_metadata="([^"]*)"/.exec(response.headers.get('www-authenticate'))?.[1];
      assert.equal(hint, prm, 'wrong metadata hint');
    }
    return response;
  };
  const get = async address => {
    const response = await fetch(address, { redirect: 'error' });
    assert(response.ok && !response.redirected, 'metadata unavailable or redirected');
    return response.json();
  };
  p.discoveryState = async () => {
    const resourceMetadata = OAuthProtectedResourceMetadataSchema.parse(await get(prm));
    assert.equal(resourceMetadata.resource, base, 'wrong resource');
    assert.deepEqual(resourceMetadata.authorization_servers, [base], 'wrong authorization server');
    const authorizationServerMetadata = OAuthMetadataSchema.parse(await get(asm));
    assert.equal(authorizationServerMetadata.issuer, base, 'wrong issuer');
    return { authorizationServerUrl: base, resourceMetadataUrl: prm,
      resourceMetadata, authorizationServerMetadata };
  };
  p.validateResourceURL = (_endpoint, resource) => {
    assert.equal(resource, base, 'wrong resource selected');
    return new URL(base);
  };
  return { fetch, base };
}

async function run(name, { base = pod, mode = 'proactive', profile = false, changes = {}, succeeds = true } = {}) {
  const endpoint = base + suffix, f = fixture(base, changes), p = provider();
  const fetch = profile ? sempodsProfile(endpoint, f, p).fetch : f.fetch;
  let failure;
  if (mode === 'proactive') {
    try { await auth(p, { serverUrl: endpoint, fetchFn: fetch }); } catch (e) { failure = e.message; }
  } else {
    const client = new Client({ name: 'sempods-discovery-probe', version: '1' });
    const transport = new StreamableHTTPClientTransport(new URL(endpoint), { fetch, authProvider: p });
    try {
      await client.connect(transport);
      assert.equal(f.trace.filter(r => r.url.includes('.well-known')).length, 0, 'anonymous initialize needs no discovery');
      await client.callTool({ name: 'authorize', arguments: {} });
    } catch (e) { failure = e.message; } finally { await client.close(); }
  }
  assert.equal(p.redirects.length, succeeds ? 1 : 0, name);
  if (profile && !succeeds) {
    assert(failure, name + ': rejection expected');
    assert(!f.trace.some(r => r.method === 'POST' && !r.rpc), name + ': no registration after rejection');
    assert(!f.trace.some(r => r.url.startsWith(otherPod)), name + ': no request to Bob');
  }
  if (profile && succeeds) {
    assert.equal(p.redirects[0].origin + p.redirects[0].pathname, base + '/_system/auth/authorize');
    assert.equal(p.redirects[0].searchParams.get('resource'), new URL(base).href);
    assert(f.trace.some(r => r.url === resourceMetadataUrl(base)));
    assert(f.trace.some(r => r.url === authorizationMetadataUrl(base)));
  }
  records.push({ name, discovery: succeeds ? 'authorization redirect reached' : 'rejected',
    trace: f.trace, ...(failure ? { terminalMessage: failure } : {}) });
}

for (const mode of ['challenge', 'proactive']) {
  await run('generic SDK, required append routes only: ' + mode, {
    mode, changes: { legacyAlias: true }, succeeds: false
  });
  const requests = records.at(-1).trace;
  assert(!requests.some(r => r.url === pod + suffix + '/.well-known/oauth-protected-resource'));
  await run('generic SDK, host aliases present: ' + mode, { mode, changes: { hostAliases: true } });
  await run('explicit sempods profile: ' + mode, { mode, profile: true });
}
for (const base of ['https://alice.example', otherPod, 'https://example.org/teams/alice']) {
  await run('profile base ' + base, { base, profile: true });
}
for (const [name, changes] of Object.entries({
  'wrong hint': { hint: resourceMetadataUrl(otherPod) },
  'nonidentical hint spelling': { hint: resourceMetadataUrl(pod).replace('example.org', 'EXAMPLE.ORG') },
  'wrong resource': { resource: otherPod },
  'parent resource': { resource: 'https://example.org' },
  'prefix collision': { resource: 'https://example.org/alic' },
  'wrong authorization server': { servers: [otherPod] },
  'multiple authorization servers': { servers: [pod, otherPod] },
  'wrong issuer': { issuer: otherPod },
  'auth route as issuer': { issuer: pod + '/_system/auth' },
  'metadata redirect': { redirect: true },
  'metadata missing': { unavailable: true }
})) await run('profile rejects ' + name, { profile: true, mode: 'challenge', changes, succeeds: false });

// Reaching a redirect in a permissive SDK is not evidence of this profile's identity checks.
await run('generic SDK accepts parent resource', { changes: { hostAliases: true, resource: 'https://example.org' } });
await run('generic SDK accepts mismatching issuer', { changes: { hostAliases: true, issuer: otherPod } });
for (const endpoint of [pod + '/mcp', pod + suffix + '/', pod + suffix + '?q=1', pod + suffix + '#x',
  'https://user@example.org/alice' + suffix, 'https://example.org/alice/../bob' + suffix,
  pod + '/%5Fsystem/mcp', 'http://example.org/alice' + suffix]) {
  const f = fixture(pod);
  assert.throws(() => sempodsProfile(endpoint, f, provider()), endpoint);
  assert.equal(f.trace.length, 0);
}
console.log(JSON.stringify({ sdk: '1.30.0', protocol: LATEST_PROTOCOL_VERSION,
  node: process.version, flows: records.length, invalidEntries: 8,
  boundary: 'SDK with scripted fetch; explicit profile is fixture code; stops at authorization redirect; no TLS, browser, token exchange or running pod',
  records }, null, 2));
