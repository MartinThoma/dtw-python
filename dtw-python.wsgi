#!/usr/bin/python
# Core Library modules
import logging
import sys

# First party modules
from index import app as application

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/dtw-python/")

application.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RTsss'
