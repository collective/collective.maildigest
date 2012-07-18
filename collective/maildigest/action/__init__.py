class BaseAction(object):

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)