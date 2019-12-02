import base64
import os


NONCE_LENGTH = 16


def generate_nonce() -> str:
    """
    Generate a nonce for CSP purposes.

    Python base64 encoding adds "=" as padding
    to the text - this is unsafe for CSP purposes so we strip
    it out.
    """
    b64_str = base64.b64encode(os.urandom(NONCE_LENGTH))
    return b64_str.decode().rstrip('=')


# Security bug! CSP nonces must be unique per request.
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src
CSP_NONCE = generate_nonce()

CSP_CONFIG = {
    'base-uri': "'self'",
    'object-src': "'none'",
    'script-src': f"'nonce-{CSP_NONCE}' 'strict-dynamic' 'unsafe-inline' https: http:",
    'report-uri': '/csp/',
    'report-to': 'csp-endpoint'
}

REPORT_TO_HEADER = {
    'group': 'csp-endpoint',
    # What is this in days?
    'max-age': 10886400,
    'endpoints': ['/csp/'],
}

NON_XSRF_PROTECTED_METHODS = ('options', 'head', 'get')
# What is this in days?
XSRF_TIME_LIMIT = 86400

SECRET_KEY = os.urandom(64)

AUTH_TEMPLATE_FOLDER = os.path.join(
    os.path.dirname(__file__), 'contrib/users/templates'
)

CLOUD_TASKS_BODY = {
    'app_engine_http_request': {  # Specify the type of request.
        'http_method': 'POST',
        'app_engine_routing': {
            'version': os.getenv('GAE_VERSION', 'default')
        },
        'headers': {
            'Content-Type': 'application/json'
        }
    }
}
