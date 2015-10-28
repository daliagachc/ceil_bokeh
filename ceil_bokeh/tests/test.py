import ConfigParser
__author__ = 'diego'

con = ConfigParser.ConfigParser()
con.read('conf.ini')
res= con.get('sql_weewx',"column_names")
ress=res.split(',')
print ress

import os

print os.path.join(os.path.abspath(os.path.dirname(__file__)), 'conf.ini')