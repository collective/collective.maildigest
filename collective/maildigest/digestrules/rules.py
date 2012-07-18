from copy import deepcopy
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import allowedRolesAndUsers

class BaseRule(object):

    def __call__(self, *args, **kwargs):
        return self.filter(*args, **kwargs)

class SameEditor(BaseRule):
    """remove from info when a content has been modified by same user many times
    """

    def filter(self, portal, subscriber, info):
        if not 'modify' in info:
            return info

        info = deepcopy(info)
        modified_infos = deepcopy(info['modify'])
        modified_infos.sort(key=lambda x: x['date'], reverse=True)
        uid_actors = []
        for modified_info in modified_infos:
            if (modified_info['uid'], modified_info['actor']) in uid_actors:
                info['modify'].remove(modified_info)

            uid_actors.append((modified_info['uid'], modified_info['actor']))

        return info

class Unauthorized(BaseRule):
    """Remove from info if folder or document is unauthorized for user
    or document has been removed
    (exept for delete activity)
    """

    def filter(self, portal, subscriber, infos):
        mtool = getToolByName(portal, 'portal_membership')
        ctool = getToolByName(portal, 'portal_catalog')
        usertype, userid = subscriber
        if usertype == 'email':
            allowed = ['Anonymous']
        elif usertype == 'member':
            user = mtool.getMemberById(userid)
            allowed = ctool._listAllowedRolesAndUsers(user)

        filtered = {}
        for activity, activity_infos in infos.items():
            if activity == 'delete':
                filtered[activity] = activity_infos
                continue

            for info in activity_infos:
                filtered[activity] = []
                brains = ctool.searchResults(UID=(info['folder-uid'], info['uid']),
                                             allowedRolesAndUsers=allowed)
                if len(brains) == 2:
                    filtered[activity].append(info)

        return filtered
