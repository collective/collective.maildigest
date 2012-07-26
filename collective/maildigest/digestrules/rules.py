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
        pas = getToolByName(portal, 'acl_users')
        mtool = getToolByName(portal, 'portal_membership')
        ctool = getToolByName(portal, 'portal_catalog')
        usertype, userid = subscriber
        if usertype == 'email':
            allowed = ['Anonymous']
        elif usertype == 'member':
            user = pas.getUserById(userid) or mtool.getMemberById(userid)
            if user is None:
                return infos

            allowed = ctool._listAllowedRolesAndUsers(user)

        filtered = {}
        for activity, activity_infos in infos.items():
            if activity == 'delete':
                filtered[activity] = activity_infos
                continue

            for info in activity_infos:
                brains = ctool.unrestrictedSearchResults(
                                        UID=(info['folder-uid'], info['uid']),
                                        allowedRolesAndUsers=allowed)
                if len(brains) == 2:
                    filtered.setdefault(activity, []).append(info)

        return filtered


class AddedAndRemoved(BaseRule):
    """If a document has been added and removed during the same session
    do not display any activity on it
    """

    def filter(self, portal, subscriber, infos):
        if not 'delete' in infos:
            return infos
        elif not 'add' in infos:
            return infos

        added = set()
        removed = set()
        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if activity == 'add':
                    added.add(info['uid'])
                elif activity == 'delete':
                    removed.add(info['uid'])

        added_and_removed = added.intersection(removed)

        filtered = {}
        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if info['uid'] not in added_and_removed:
                    filtered.setdefault(activity, []).append(deepcopy(info))

        return filtered

class ModifiedAndRemoved(BaseRule):
    """If a document has been removed, do not display modify activity
    """

    def filter(self, portal, subscriber, infos):
        if not 'modify' in infos:
            return infos
        elif not 'delete' in infos:
            return infos

        modified = set()
        removed = set()

        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if activity == 'modify':
                    modified.add(info['uid'])
                elif activity == 'remove':
                    removed.add(info['uid'])

        modified_and_removed = modified.intersection(removed)

        filtered = {}
        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if activity == 'modify' and info['uid'] in modified_and_removed:
                    pass
                else:
                    filtered.setdefault(activity, []).append(deepcopy(info))

        return filtered


class AddedAndModifiedBySame(BaseRule):
    """If a document has been added and modified by the same user,
    ignore modify activity
    """

    def filter(self, portal, subscriber, infos):
        if not 'modify' in infos:
            return infos
        elif not 'add' in infos:
            return infos

        added_uid_actors = set()
        modified_uid_actors = set()


        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if activity == 'modify':
                    modified_uid_actors.add((info['uid'], info['actor']))
                elif activity == 'add':
                    added_uid_actors.add((info['uid'], info['actor']))

        added_and_modified_uid_actors = added_uid_actors.intersection(modified_uid_actors)

        filtered = {}
        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if activity == 'modify' \
                   and (info['uid'], info['actor']) in added_and_modified_uid_actors:
                    pass
                else:
                    filtered.setdefault(activity, []).append(deepcopy(info))

        return filtered
