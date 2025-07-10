import os
from .base import *

ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .prod import *
else:
    from .dev import *
