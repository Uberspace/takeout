class TakeoutItem():
    kind = None
    tar_path = None
    description = None

    def __init__(self, username, hostname):
        self.username = username
        self.hostname = hostname

    def takeout(self):
        raise NotImplementedError()

    def takein(self):
        raise NotImplementedError()

    def is_active(self):
        return True


class PathItem(TakeoutItem):
    kind = 'path'

    def takeout(self):
        return self.path()

    def takein(self):
        return self.path()
