from webapp.models import Comment

class Subthread:
    def __init__(self,comment,children=[]):
        self.comment = comment
        self.children = children

    def addChild(self,child):
        self.children.append(child)

    def insertChildTo(self,id,child):
        if(id == self.comment.id):
            self.children.append(child)
            return True
        else:
            for c in self.children:
                if(c.insertChildTo(id,child)):
                    return True
            return False

    def toList(self,level,list=[]):
        list.append((self.comment,level))
        for child in self.children:
            child.toList(level+1,list)
        return list

    def __str__(self):
        return str((self.comment.id,[str(child) for child in self.children]))

