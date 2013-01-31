from webapp.models import Thread,LcUser,Domain,Comment
from django.db import connection
from webapp import comment as c
import traceback

def get_main():
    """
    returns an array of sorted thread ids - sorting logic to be added
    """
    return [t.id for t in Thread.objects.all().order_by('-time_created')[:50]]


def get_best_subthread(tid):
    """
    returns the best comment subthread of the given thread
    for main page display purposes
    no sorting logic for now - just picks a single thread
    """
    try:
        t = Thread.objects.get(pk = int(tid))
        primer_comments = Comment.objects.filter(thread = t, parent = None)[:1] # get a single None thread
        sub = []
        if(len(primer_comments) > 0): # there is at least a single comment about the thread - try to get a child
            primer = primer_comments[0]
            sub.append(primer)
            secondary_comments = Comment.objects.filter(parent = primer.id)[:1]
            if(len(secondary_comments) > 0): # there is at least a single child
                sub.append(secondary_comments[0])
        return (True,c.get_comment_fields(sub))
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))
