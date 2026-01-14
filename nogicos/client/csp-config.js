/**
 * Content Security Policy Config
 * Phase 7.13: Content Security Policy Config
 * 
 * 防止 XSS Attack和未Authorization资SourceLoad
 */

const { session } = require('electron');

/**
 * CSP Policy定义
 */
const CSP_DIRECTIVES = {
  // DefaultonlyAllowsameSource
  'default-src': ["'self'"],
  
  // ScriptonlyAllowsameSource（Forbidden eval and inline）
  // Note：IfNeedSupportOnemitPattern's HotUpdate，maybeNeedResize
  'script-src': ["'self'"],
  
  // StyleAllowInnerconnect（Motion AnimationNeed）+ Google Fonts CSS
  'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
  
  // GraphpieceAllowsameSource + data URL（captureGraph）+ blob
  'img-src': ["'self'", 'data:', 'blob:'],
  
  // ConnectonlyAllowlocalAfterend + Google Fonts
  'connect-src': [
    "'self'",
    'ws://localhost:*',
    'http://localhost:*',
    'ws://127.0.0.1:*',
    'http://127.0.0.1:*',
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
  ],
  
  // fontAllowsameSource + Google Fonts
  'font-src': ["'self'", 'data:', 'https://fonts.gstatic.com'],
  
  // ForbiddenEmbeddingFramework
  'frame-ancestors': ["'none'"],
  
  // ForbiddenObject（Flash etc）
  'object-src': ["'none'"],
  
  // Forbidden base URI Modify
  'base-uri': ["'self'"],
  
  // TablesingleonlycanCommittosameSource
  'form-action': ["'self'"],
  
  // mediaonlyAllowsameSource
  'media-src': ["'self'", 'blob:'],
  
  // Worker Script
  'worker-src': ["'self'", 'blob:'],
};

/**
 * 将 CSP 指令ObjectConvert为Character串
 */
function buildCSPString(directives) {
  return Object.entries(directives)
    .map(([key, values]) => `${key} ${values.join(' ')}`)
    .join('; ');
}

/**
 * Set Content Security Policy
 */
function setupCSP() {
  const cspString = buildCSPString(CSP_DIRECTIVES);
  
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [cspString],
      },
    });
  });
  
  console.log('[Security] CSP configured');
}

/**
 * 额Outer的SecurityHeadConfig
 */
const SECURITY_HEADERS = {
  // Forbidden MIME Classtypesniff
  'X-Content-Type-Options': 'nosniff',
  
  // Forbiddenin iframe MediumLoad
  'X-Frame-Options': 'DENY',
  
  // XSS Protected（althoughappeargenerationBrowseralreadyDeprecated，butasforquotaOuterProtected）
  'X-XSS-Protection': '1; mode=block',
  
  // strict's ReferencePolicy
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // PermissionPolicy：DisableNot Need's function
  'Permissions-Policy': [
    'camera=()',
    'microphone=()',
    'geolocation=()',
    'payment=()',
  ].join(', '),
};

/**
 * Set额Outer的SecurityHead
 */
function setupSecurityHeaders() {
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    const newHeaders = { ...details.responseHeaders };
    
    for (const [header, value] of Object.entries(SECURITY_HEADERS)) {
      newHeaders[header] = [value];
    }
    
    callback({ responseHeaders: newHeaders });
  });
  
  console.log('[Security] Security headers configured');
}

/**
 * Set所有SecurityConfig
 */
function setupAllSecurity() {
  setupCSP();
  setupSecurityHeaders();
}

/**
 * On发模式的宽松 CSP（仅用于On发）
 */
function setupDevCSP() {
  const devDirectives = {
    ...CSP_DIRECTIVES,
    // OnemitPatternAllow eval（for HMR）
    'script-src': ["'self'", "'unsafe-eval'", "'unsafe-inline'"],
    // Allow WebSocket HotUpdate
    'connect-src': [
      ...CSP_DIRECTIVES['connect-src'],
      'ws://*:*',
      'http://*:*',
    ],
  };
  
  const cspString = buildCSPString(devDirectives);
  
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [cspString],
      },
    });
  });
  
  console.log('[Security] Development CSP configured (less strict)');
}

module.exports = {
  setupCSP,
  setupSecurityHeaders,
  setupAllSecurity,
  setupDevCSP,
  CSP_DIRECTIVES,
  SECURITY_HEADERS,
  buildCSPString,
};
