from zope.interface import Interface

class IFollowable(Interface):
    """A content we can follow
    """

class IFollowableContainer(IFollowable):
    """We can follow this container,
    which means we follow activity on all its contents
    """

class IDigestInfo(Interface):
    """View that provides info about user subscription on content
    """

class IDigestStorage(Interface):
    """Storage where activity on site is stored.
    One storage by delay (daily, weekly, etc)
    """

class IDigestUtility(Interface):
    """Tool used by activities to be stored for subscribers
    """