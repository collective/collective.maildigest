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

class IDigestFilterRule(Interface):
    """A rule gets a digest info and modify it to provide more pertinent information
    by example:
        if a document has been added and removed during the storage delay,
        do not display it in digest
    """
    def filter(digest_info):
        """@return digest_info (a copy, not the same object)
        """

class IDigestAction(Interface):
    """An action do "something" with an user id and a digest info
    """

    def execute(portal, userid, digest_info):
        """
        """