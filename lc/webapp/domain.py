from webapp.models import Domain
from django.db import connection
import traceback
import os

def generateId():
    return int(os.urandom(4).encode('hex'),16) / 2

def createnx_domain(name,logo=''):
    """
    tries to get the domain - if it doesn't exist, domain is created
    """
    try:
        res = Domain.objects.filter(name = name)
        if(len(res)>0):
            return (res[0],'')
        else:
            # create new domain object
            domain = Domain(id = generateId(), name = name, logo = logo)
            domain.save()
            return (domain,'')
    except:
        connection._rollback()
        return (None,str(traceback.format_exc()))
