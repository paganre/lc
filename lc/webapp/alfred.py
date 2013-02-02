from webapp.models import Thread,LcUser,Domain,Comment
from django.db import connection
from webapp import comment as c
import traceback
from math import sqrt

def get_time():
    return [t.id for t in Thread.objects.all().order_by('-time_created')[:50]]

def get_best_subthread(tid):
    """
    returns the best comment subthread of the given thread
    for main page display purposes
    Sorting logic: Return the parent comment with the highest up vote
    and return the child of this comment with the highest up vote
    """
    
    try:
        t = Thread.objects.get(pk = int(tid))
        primer_comments = Comment.objects.filter(thread = t, parent = None).order_by('-up')
            #get a single None thread with the hightest up vote
        sub = []
        if(len(primer_comments) > 0):
            # there is at least a single comment about the thread
            # Therefore top_primer_comment is well defined
            # try to get the child with the highest up vote
            top_primer_comment = primer_comments[0]
            sub.append(top_primer_comment)
            secondary_comments = Comment.objects.filter(parent = top_primer_comment.id).order_by('-up')
            if(len(secondary_comments) > 0):
                # there is at least a single child
                # There top_secondary_comment is well defined
                # Append it to the list
                top_secondary_comment = secondary_comments[0]
                sub.append(top_secondary_comment)
        return (True,c.get_comment_fields(sub))
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def subthread_list_sort(subtread_list):
    try:
        # List subtreads by their parents' up field in decreasing order
        subtread_list.sort(key=lambda l: l.comment.up, reverse=True)
        return True
    except:
        # If an object that is not a subthread list, return the object
        return False

def get_best():
    res = []
    for t in Thread.objects.all():
        res = res + [(t.id,contro(t.up, t.down, t.views))]
    res.sort(key=lambda l: l[1], reverse=True)
    tid = []
    for r in res:
        tid = tid + [r[0]]
    return tid

def contro(up, down, views):
    # Given total up votes, total down votes and total views of a thread
    # Quantifies how controversial a thread is
    # Controlversiality = a_1 (Total views) + a_2 (Positive vote estimation) + a_3 (Total votes)
    a1 = 0.2
    a2 = 1
    a3 = 0.6
    
    n = up + down
    if n==0:
        return 0
    
    # Positive vote estimation
    # ------------------------
    
    # I am just implementing this:
    #http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
    
    # 95% confidence
    z = 1.96
    
    # Lower bound of the estimate
    up_perc = 1.0*up/n
    up_estimate = up_perc + z*z/(2*n)
    up_estimate = up_estimate - z * sqrt((up_perc*(1-up_perc)+z*z/(4*n))/n)
    up_estimate = up_perc/(1+z*z/n)
    up_vote_estimate = up_estimate * n
                            
    # To calculate the upper bound, use the following
    # up_estimate = 1.0*up/n (up_estimate + z*z/(2*n)
    # up_estimate = up_estimate + z * sqrt((up_estimate*(1-up_estimate)+z*z/(4*n))/n)
    # up_estimate = up_estimate/(1+z*z/n)

    # ------------------------
    # Combine elements and return controversiality
    return a1*views + a2*up_vote_estimate + a3*n