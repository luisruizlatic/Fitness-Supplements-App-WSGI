#python_home = '/var/www/FitnessSupplementsApp/venv'
#activate_this = python_home + '/bin/activate_this.py'
#exec(open(activate_this).read())

import sys


if sys.version_info[0]<3: #check if is run with python3
    raise Exception("Python3 is required to run this program! Current version: '%s'" % sys.version_info)

sys.path.insert(0,'/var/www/FitnessSupplementsApp')#path where the project is located
from FitnessSupplementsApp import app as application