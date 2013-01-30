from webapp.models import Thread,LcUser,Domain

def get_main():
    """
    returns an array of sorted thread ids - sorting logic to be added
    """
    return [t.id for t in Thread.objects.all()[:10]]
