import socket
from django.core.wsgi import get_wsgi_application
host = socket.gethostname()
if host and host.startswith('staging-vault-i'):
    import newrelic.agent
    newrelic.agent.initialize('venv/vault/conf/staging-newrelic.ini')

if host and host.startswith('production-vault'):
    import newrelic.agent
    newrelic.agent.initialize('venv/vault/conf/production-newrelic.ini')

application = get_wsgi_application()
