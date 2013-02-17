import os

# Add local directory to python path
os.sys.path.insert(0, os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1]))

# Activate virtualenv
activate_this = os.path.dirname(os.path.abspath(__file__)) + '/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from app import app as application
