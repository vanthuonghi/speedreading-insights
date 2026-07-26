/**
 * Cloudflare Worker: Static form → Odoo CRM Lead (no backend, no CORS)
 *
 * Architecture (clean):
 *   Form on speedreading.vn  →  POST /api/webinar  (same-origin Worker)
 *        →  Worker calls Odoo XML-RPC over HTTPS (odoo.speedreading.vn)
 *        →  Odoo creates crm.lead (source = "Webinar Free")
 *        →  Odoo automation sends welcome email (already configured)
 *
 * Why this is clean:
 *   - Same origin → no CORS, no WAF block, no extra subdomain
 *   - Serverless → no Python process to keep alive, auto-scales, free
 *   - One file, deployed to Cloudflare edge in 1 click
 *
 * Deploy:
 *   1. Cloudflare Dashboard → Workers & Pages → Create Worker → paste this → Save
 *   2. Worker Settings → Variables → Add secret ODOO_PASS = (mật khẩu Odoo)
 *   3. Worker → Triggers → Routes → Add: speedreading.vn/api/webinar  (GET/POST)
 */

const ODOO_URL = 'https://odoo.speedreading.vn';
const ODOO_DB = 'speedreading_prod';
const ODOO_USER = 'vanthuonghi@gmail.com';

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' }[c]));
}

function xmlrpcValue(v) {
  if (typeof v === 'string') return `<string>${escapeXml(v)}</string>`;
  if (typeof v === 'number') return `<int>${v}</int>`;
  if (typeof v === 'boolean') return `<boolean>${v ? 1 : 0}</boolean>`;
  if (v === null || v === undefined) return `<nil/>`;
  if (Array.isArray(v)) return `<array><data>${v.map(xmlrpcValue).join('')}</data></array>`;
  if (typeof v === 'object') {
    return `<struct>${Object.entries(v).map(([k, val]) =>
      `<member><name>${k}</name><value>${xmlrpcValue(val)}</value></member>`).join('')}</struct>`;
  }
  return `<string>${escapeXml(String(v))}</string>`;
}

function xmlrpcMethodCall(methodName, params) {
  return `<?xml version="1.0"?>
<methodCall>
  <methodName>${methodName}</methodName>
  <params>
    ${params.map(p => `<param><value>${p}</value></param>`).join('')}
  </params>
</methodCall>`;
}

async function odooAuthenticate(ODOO_PASS) {
  const loginBody = `<?xml version="1.0"?>
<methodCall>
  <methodName>login</methodName>
  <params>
    <param><value><string>${ODOO_DB}</string></value></param>
    <param><value><string>${ODOO_USER}</string></value></param>
    <param><value><string>${ODOO_PASS}</string></value></param>
  </params>
</methodCall>`;
  const res = await fetch(`${ODOO_URL}/xmlrpc/2/common`, {
    method: 'POST',
    headers: { 'Content-Type': 'text/xml' },
    body: loginBody
  });
  const text = await res.text();
  const uidMatch = text.match(/<int>(\d+)<\/int>/);
  if (!uidMatch) throw new Error('Auth failed: ' + text.slice(0, 200));
  return parseInt(uidMatch[1], 10);
}

async function odooExecute(uid, model, method, args, kwargs, ODOO_PASS) {
  const params = [
    `<string>${ODOO_DB}</string>`,
    `<int>${uid}</int>`,
    `<string>${ODOO_PASS}</string>`,
    `<string>${model}</string>`,
    `<string>${method}</string>`,
    xmlrpcValue(args),
    xmlrpcValue(kwargs || {})
  ];
  const body = xmlrpcMethodCall('execute_kw', params);
  const res = await fetch(`${ODOO_URL}/xmlrpc/2/object`, {
    method: 'POST',
    headers: { 'Content-Type': 'text/xml' },
    body
  });
  const text = await res.text();
  if (text.includes('<fault>')) {
    const fm = text.match(/<string>([\s\S]*?)<\/string>/);
    throw new Error('Odoo fault: ' + (fm ? fm[1] : text.slice(0, 200)));
  }
  return text;
}

async function handleWebinarPost(data, ODOO_PASS) {
  const name = (data.name || data.first_name || '').toString().trim();
  const email = (data.email || '').toString().trim();
  const phone = (data.phone || '').toString().trim();

  if (!name || !phone) {
    return new Response(JSON.stringify({ status: 'error', msg: 'Thiếu tên hoặc số điện thoại' }), {
      status: 400, headers: { 'Content-Type': 'application/json' }
    });
  }

  const uid = await odooAuthenticate(ODOO_PASS);

  // Resolve or create utm.source "Webinar Free"
  let srcIds = await odooExecute(uid, 'utm.source', 'search', [[['name', '=', 'Webinar Free']]], { 'limit': 1 }, ODOO_PASS);
  let sourceId;
  const srcMatch = srcIds.match(/<int>(\d+)<\/int>/);
  if (srcMatch) {
    sourceId = parseInt(srcMatch[1], 10);
  } else {
    const created = await odooExecute(uid, 'utm.source', 'create', [{ name: 'Webinar Free' }], {}, ODOO_PASS);
    const cm = created.match(/<int>(\d+)<\/int>/);
    sourceId = cm ? parseInt(cm[1], 10) : false;
  }

  const leadVals = {
    name: `Đăng ký Webinar Free - ${name}`,
    contact_name: name,
    email_from: email,
    phone: phone,
    source_id: sourceId,
    description: `Webinar free lead từ form speedreading.vn (${new Date().toISOString()})`
  };

  const createRes = await odooExecute(uid, 'crm.lead', 'create', [leadVals], {}, ODOO_PASS);
  const leadMatch = createRes.match(/<int>(\d+)<\/int>/);
  const leadId = leadMatch ? parseInt(leadMatch[1], 10) : null;

  return new Response(JSON.stringify({ status: 'ok', lead_id: leadId }), {
    status: 200, headers: { 'Content-Type': 'application/json' }
  });
}

export default {
  async fetch(request, env, ctx) {
    const ODOO_PASS = env.ODOO_PASS;  // Set as Worker secret
    if (!ODOO_PASS) {
      return new Response(JSON.stringify({ status: 'error', msg: 'Worker not configured' }), {
        status: 500, headers: { 'Content-Type': 'application/json' }
      });
    }

    const url = new URL(request.url);
    if (url.pathname !== '/api/webinar') {
      return new Response('Not found', { status: 404 });
    }

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const contentType = request.headers.get('content-type') || '';
      let data;
      if (contentType.includes('application/json')) {
        data = await request.json();
      } else {
        const fd = await request.formData();
        data = Object.fromEntries(fd.entries());
      }
      return await handleWebinarPost(data, ODOO_PASS);
    } catch (e) {
      return new Response(JSON.stringify({ status: 'error', msg: e.message }), {
        status: 500, headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
