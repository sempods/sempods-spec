#!/usr/bin/env node
// Bounded HTTPS fixture for SPS-MCP-009 and SPS-MCP-033–038, not a pod implementation.
// The SDK owns discovery, registration, PKCE, token exchange and transport. No fetch,
// resource validation or discovery override is installed. See repository-checks.md.
import assert from 'node:assert/strict';
import { createServer } from 'node:https';
import { readFileSync } from 'node:fs';
import { createHash, createHmac, randomBytes, randomUUID } from 'node:crypto';
import { pathToFileURL } from 'node:url';

const sdkRoot = process.env.MCP_SDK_ROOT;
assert.notEqual(process.env.NODE_TLS_REJECT_UNAUTHORIZED, '0', 'TLS verification must stay enabled');
assert(sdkRoot, 'Set MCP_SDK_ROOT to the installed @modelcontextprotocol/sdk directory');
const version = JSON.parse(readFileSync(`${sdkRoot}/package.json`)).version;
assert.equal(version, '1.30.1', 'This experiment records SDK 1.30.1 behavior');
const { Client } = await import(pathToFileURL(`${sdkRoot}/dist/esm/client/index.js`));
const { StreamableHTTPClientTransport } = await import(pathToFileURL(`${sdkRoot}/dist/esm/client/streamableHttp.js`));
const { auth, UnauthorizedError } = await import(pathToFileURL(`${sdkRoot}/dist/esm/client/auth.js`));
const json = (res, status, body, headers = {}) => {
  res.writeHead(status, { 'Content-Type': 'application/json', ...headers });
  res.end(JSON.stringify(body));
};
const hash = s => createHash('sha256').update(s).digest('base64url');
const results = [];
const requests = [];
const clients = new Map();
const codes = new Map();
const refresh = new Map();
// Shared signing key deliberately makes issuer/audience checks necessary across fixture pods.
const key = randomBytes(32);
function sign(payload) {
  const input = [ { alg: 'HS256', typ: 'JWT' }, payload ].map(x => Buffer.from(JSON.stringify(x)).toString('base64url')).join('.');
  return `${input}.${createHmac('sha256', key).update(input).digest('base64url')}`;
}
function claims(token) {
  const [header, payload, signature] = token.split('.');
  assert.equal(signature, createHmac('sha256', key).update(`${header}.${payload}`).digest('base64url'));
  return JSON.parse(Buffer.from(payload, 'base64url'));
}
let origin;
let poison = '';
const pods = ['', '/alice', '/bob'];
const resourcePath = pod => `/.well-known/oauth-protected-resource${pod}/_system/mcp`;
const issuerPath = pod => `/.well-known/oauth-authorization-server${pod}`;
const endpoint = pod => `${origin}${pod}/_system/mcp`;
const server = createServer({ key: readFileSync(process.env.MCP_TLS_KEY), cert: readFileSync(process.env.MCP_TLS_CERT) }, async (req, res) => {
  try {
    const url = new URL(req.url, origin);
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const body = Buffer.concat(chunks).toString();
    requests.push(`${req.method} ${url.pathname}`);
    for (const pod of pods) {
      const P = origin + pod;
      const M = endpoint(pod);
      if (req.method === 'GET' && url.pathname === resourcePath(pod)) {
        const resource = poison === 'sibling-resource' ? endpoint('/bob') : poison === 'parent-resource' ? P : poison === 'origin-resource' ? origin : M;
        return json(res, 200, { resource, authorization_servers: [P], bearer_methods_supported: ['header'] });
      }
      if (req.method === 'GET' && url.pathname === issuerPath(pod)) {
        return json(res, 200, { issuer: poison === 'wrong-issuer' ? origin + '/bob' : P,
          authorization_endpoint: P + '/_system/auth/authorize', token_endpoint: P + '/_system/auth/token',
          registration_endpoint: P + '/_system/auth/register', jwks_uri: P + '/_system/auth/jwks.json',
          response_types_supported: ['code'], grant_types_supported: ['authorization_code', 'refresh_token'],
          token_endpoint_auth_methods_supported: ['none'], code_challenge_methods_supported: ['S256'] });
      }
      if (req.method === 'POST' && url.pathname === pod + '/_system/auth/register') {
        const metadata = JSON.parse(body);
        const client_id = randomUUID();
        clients.set(client_id, { pod, ...metadata });
        return json(res, 201, { ...metadata, client_id });
      }
      if (req.method === 'GET' && url.pathname === pod + '/_system/auth/authorize') {
        const q = url.searchParams;
        const client = clients.get(q.get('client_id'));
        if (!client || client.pod !== pod || !client.redirect_uris.includes(q.get('redirect_uri'))) return json(res, 400, { error: 'invalid_request' });
        const target = new URL(q.get('redirect_uri'));
        if (q.has('state')) target.searchParams.set('state', q.get('state'));
        if (q.getAll('resource').length !== 1 || q.get('resource') !== M) target.searchParams.set('error', 'invalid_target');
        else {
          assert.equal(q.get('response_type'), 'code');
          assert.equal(q.get('code_challenge_method'), 'S256');
          assert(q.get('code_challenge'));
          const code = randomUUID();
          // Consent is a fixture decision, not an exercised browser or human consent screen.
          codes.set(code, { pod, resource: M, client: q.get('client_id'), redirect: q.get('redirect_uri'), challenge: q.get('code_challenge') });
          target.searchParams.set('code', code);
        }
        res.writeHead(302, { Location: target.href });
        return res.end();
      }
      if (req.method === 'POST' && url.pathname === pod + '/_system/auth/token') {
        const q = new URLSearchParams(body);
        if (q.getAll('resource').length !== 1 || q.get('resource') !== M) return json(res, 400, { error: 'invalid_target' });
        const isCode = q.get('grant_type') === 'authorization_code';
        const grant = (isCode ? codes : refresh).get(q.get(isCode ? 'code' : 'refresh_token'));
        if (!grant || grant.pod !== pod || grant.client !== q.get('client_id')) return json(res, 400, { error: 'invalid_grant' });
        if (grant.resource !== M) return json(res, 400, { error: 'invalid_target' });
        if (isCode && (grant.redirect !== q.get('redirect_uri') || grant.challenge !== hash(q.get('code_verifier') || ''))) return json(res, 400, { error: 'invalid_grant' });
        (isCode ? codes : refresh).delete(q.get(isCode ? 'code' : 'refresh_token'));
        const refresh_token = randomUUID();
        refresh.set(refresh_token, grant);
        return json(res, 200, { access_token: sign({ iss: P, aud: M, sub: 'fixture-person', client_id: grant.client, exp: Math.floor(Date.now()/1000)+300 }), token_type: 'Bearer', expires_in: 300, refresh_token });
      }
      if (req.method === 'POST' && url.pathname === pod + '/_system/mcp') {
        const message = JSON.parse(body);
        let authenticated = false;
        const bearer = req.headers.authorization;
        if (bearer) {
          try {
            const token = claims(bearer.replace(/^Bearer /, ''));
            const audience = Array.isArray(token.aud) ? token.aud : [token.aud];
            authenticated = token.iss === P && audience.length === 1 && audience[0] === M && token.exp > Date.now()/1000;
          } catch { /* A rejected credential cannot fall back to anonymous. */ }
        }
        if ((bearer && !authenticated) || (!authenticated && message.method === 'tools/call' && message.params.name === 'authorize')) {
          return json(res, 401, { jsonrpc: '2.0', id: message.id, error: { code: -32001, message: 'Authorization required' } }, {
            'WWW-Authenticate': `Bearer realm="${P}", resource_metadata="${origin}${resourcePath(pod)}"`
          });
        }
        if (message.method === 'notifications/initialized') { res.writeHead(202); return res.end(); }
        let result;
        if (message.method === 'initialize') result = { protocolVersion: '2025-11-25', capabilities: { tools: {} }, serverInfo: { name: 'sempods-discovery-fixture', version: '0' } };
        else if (message.method === 'tools/list') result = { tools: ['public_read', 'authorize'].map(name => ({ name, inputSchema: { type: 'object', additionalProperties: false } })) };
        else result = { content: [{ type: 'text', text: authenticated ? `authorized:${P}` : 'public' }] };
        return json(res, 200, { jsonrpc: '2.0', id: message.id, result });
      }
    }
    return json(res, 404, { error: 'not_found' });
  } catch (error) { json(res, 500, { fixture_error: error.message }); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
origin = `https://127.0.0.1:${server.address().port}`;

// Only ordinary application callbacks: storage, verifier and user-agent redirection.
class Provider {
  redirectUrl = 'http://127.0.0.1:34567/callback';
  clientMetadata = { redirect_uris: [this.redirectUrl], client_name: 'unmodified-sdk-probe', token_endpoint_auth_method: 'none', grant_types: ['authorization_code', 'refresh_token'], response_types: ['code'] };
  state() { return 'fixture-state'; }
  clientInformation() { return this.client; }
  saveClientInformation(value) { this.client = value; }
  tokens() { return this.savedTokens; }
  saveTokens(value) { this.savedTokens = value; }
  saveCodeVerifier(value) { this.verifier = value; }
  codeVerifier() { return this.verifier; }
  redirectToAuthorization(value) { this.authorizationUrl = value; }
}
async function consent(provider) {
  const response = await fetch(provider.authorizationUrl, { redirect: 'manual' });
  assert.equal(response.status, 302);
  const callback = new URL(response.headers.get('location'));
  assert.equal(callback.searchParams.get('state'), 'fixture-state');
  assert(!callback.searchParams.has('error'));
  assert(callback.searchParams.get('code'));
  return callback.searchParams.get('code');
}
const transports = [];
const sessions = new Map();
try {
  for (const pod of pods) for (const proactive of [false, true]) {
    const provider = new Provider();
    const M = endpoint(pod);
    const traceStart = requests.length;
    if (proactive) {
      assert.equal(await auth(provider, { serverUrl: M }), 'REDIRECT');
      assert.equal(await auth(provider, { serverUrl: M, authorizationCode: await consent(provider) }), 'AUTHORIZED');
    }
    const transport = new StreamableHTTPClientTransport(new URL(M), { authProvider: provider });
    transports.push(transport);
    const client = new Client({ name: 'probe', version: '0' });
    await client.connect(transport);
    await client.listTools();
    if (!proactive) {
      assert.equal((await client.callTool({ name: 'public_read', arguments: {} })).content[0].text, 'public');
      assert.equal(requests.slice(traceStart).some(x => x.includes('.well-known')), false);
      await assert.rejects(client.callTool({ name: 'authorize', arguments: {} }), UnauthorizedError);
      await transport.finishAuth(await consent(provider));
    }
    assert.equal((await client.callTool({ name: 'authorize', arguments: {} })).content[0].text, `authorized:${origin}${pod}`);
    const token = claims(provider.savedTokens.access_token);
    assert.equal(token.iss, origin + pod);
    assert.equal(token.aud, M);
    assert.equal(await auth(provider, { serverUrl: M }), 'AUTHORIZED'); // SDK refresh
    const trace = requests.slice(traceStart);
    assert(trace.includes(`GET ${resourcePath(pod)}`));
    assert(trace.includes(`GET ${issuerPath(pod)}`));
    assert(!trace.some(x => /openid-configuration|\/mcp\/.well-known/.test(x)));
    sessions.set(pod, provider);
    results.push({ case: `${pod || 'root'} ${proactive ? 'proactive' : 'anonymous-then-challenge'}`, result: 'PASS', evidence: 'TLS, discovery, DCR, PKCE, fixture consent, token, authenticated call, refresh', requests: [...new Set(trace)] });
    await client.close();
  }
  for (const scenario of ['sibling-resource', 'parent-resource', 'origin-resource', 'wrong-issuer']) {
    poison = scenario;
    const provider = new Provider();
    let outcome;
    try { outcome = await auth(provider, { serverUrl: endpoint('/alice') }); }
    catch (error) { outcome = 'REJECTED'; assert.match(error.message, /does not match expected/); }
    const expected = scenario === 'sibling-resource' ? 'REJECTED' : 'REDIRECT';
    assert.equal(outcome, expected, 'SDK behavior changed; re-evaluate recorded limitations');
    results.push({ case: scenario, result: outcome === 'REJECTED' ? 'PASS' : 'CLIENT_LIMITATION', observed: outcome, required: 'reject before authorization' });
  }
  poison = '';
  const alice = sessions.get('/alice');
  const aliceToken = alice.savedTokens.access_token;
  const payload = claims(aliceToken);
  for (const [name, target, token] of [
    ['Alice token at Bob', endpoint('/bob'), aliceToken],
    ['wrong issuer, valid shared-key signature', endpoint('/alice'), sign({ ...payload, iss: origin + '/bob' })],
    ['pod audience', endpoint('/alice'), sign({ ...payload, aud: origin + '/alice' })],
    ['multiple audiences', endpoint('/alice'), sign({ ...payload, aud: [endpoint('/alice'), endpoint('/bob')] })],
    ['missing audience', endpoint('/alice'), sign({ ...payload, aud: undefined })],
  ]) {
    const response = await fetch(target, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'public_read' } }) });
    assert.equal(response.status, 401);
    results.push({ case: name, result: 'PASS', evidence: 'fixture rejection, not client validation' });
  }
  for (const [name, pod, resource, credential, expected] of [
    ['refresh at Bob', '/bob', endpoint('/bob'), alice.savedTokens.refresh_token, 'invalid_grant'],
    ['refresh for Bob at Alice', '/alice', endpoint('/bob'), alice.savedTokens.refresh_token, 'invalid_target'],
    ['refresh without resource', '/alice', undefined, alice.savedTokens.refresh_token, 'invalid_target'],
    ['refresh with repeated resource', '/alice', [endpoint('/alice'), endpoint('/alice')], alice.savedTokens.refresh_token, 'invalid_target'],
  ]) {
    const form = new URLSearchParams({ grant_type: 'refresh_token', refresh_token: credential, client_id: alice.client.client_id });
    for (const value of Array.isArray(resource) ? resource : resource ? [resource] : []) form.append('resource', value);
    const response = await fetch(origin + pod + '/_system/auth/token', { method: 'POST', body: form });
    assert.equal(response.status, 400);
    assert.equal((await response.json()).error, expected);
    results.push({ case: name, result: 'PASS', evidence: 'fixture rejection' });
  }
  console.log(JSON.stringify({ sdk: version, node: process.version, protocol: '2025-11-25', completeInteroperability: false, results, limitations: 'Three client validation failures remain. Synthetic AS/consent/grants; no browser UI, desktop client, Kotlin or production conformance tested.' }, null, 2));
} finally {
  for (const transport of transports) await transport.close();
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
}
