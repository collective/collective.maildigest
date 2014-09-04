from copy import deepcopy, copy

from Products.CMFCore.utils import getToolByName


class BaseRule(object):

    def __call__(self, *args, **kwargs):
        return self.filter(*args, **kwargs)


class SameEditor(BaseRule):
    """remove from info when a content has been modified by same user many times
    """

    def filter(self, portal, subscriber, info):
        if 'modify' not in info:
            return info

        uid_actors = set()
        for modified_info in copy(info['modify']):
            uid = (modified_info['uid'], modified_info['actor'])
            if uid in uid_actors:
                info['modify'].remove(modified_info)
            else:
                uid_actors.add(uid)

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
            arau = ['Anonymous']
        elif usertype == 'member':
            user = pas.getUserById(userid) or mtool.getMemberById(userid)
            if user is None:
                return infos

            arau = ctool._listAllowedRolesAndUsers(user)

        activity_uids = set()
        for activity, activity_infos in infos.items():
            if activity == 'delete':
                continue

            for info in activity_infos:
                activity_uids.add(info['folder-uid'])
                activity_uids.add(info['uid'])

        allowed_brains = ctool.unrestrictedSearchResults(
                                        UID=list(activity_uids),
                                        allowedRolesAndUsers=arau)
        allowed_uids = [b.UID for b in allowed_brains]

        filtered = {}
        for activity, activity_infos in infos.items():
            if activity == 'delete':
                filtered[activity] = activity_infos
                continue

            for info in activity_infos:
                if info['folder-uid'] in allowed_uids and info['uid'] in allowed_uids:
                    filtered.setdefault(activity, []).append(info)

        return filtered


class AddedAndRemoved(BaseRule):
    """If a document has been added/published and removed during the same session
    do not display any activity on it
    """

    def filter(self, portal, subscriber, infos):
        if ('add' not in infos and 'publish' not in infos) \
         or 'delete' not in infos:
            return infos

        added = set()
        removed = set()
        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if activity in ('add', 'publish'):
                    added.add(info['uid'])
                elif activity == 'delete':
                    removed.add(info['uid'])

        added_and_removed = added.intersection(removed)

        filtered = {}
        for activity, activity_infos in infos.items():
            for info in activity_infos:
                if info['uid'] not in added_and_removed:
                    filtered.setdefault(activity, []).append(info)

        return filtered


class AddedAndPublished(BaseRule):
    """If a document has been added and published,
    display only publication
    """

    def filter(self, portal, subscriber, infos):
        infos = deepcopy(infos)
        if 'add' not in infos or 'publish' not in infos:
            return infos

        published = set([info['uid'] for info in infos['add']])
        added = set([info['uid'] for info in infos['add']])

        added_and_published = published.intersection(added)

        for info in copy(infos['add']):
            if info['uid'] in added_and_published:
                infos['add'].remove(info)

        if len(infos['add']) == 0:
            del infos['add']

        return infos


class ModifiedAndRemoved(BaseRule):
    """If a document has been removed, do not display modify activity
    """

    def filter(self, portal, subscriber, infos):
        infos = deepcopy(infos)
        if 'modify' not in infos or 'delete' not in infos:
            return infos

        modified = set([info['uid'] for info in infos['modify']])
        removed = set([info['uid'] for info in infos['delete']])

        modified_and_removed = modified.intersection(removed)

        for info in copy(infos['modify']):
            if info['uid'] in modified_and_removed:
                infos['modify'].remove(info)

        for info in copy(infos['delete']):
            if info['uid'] in modified_and_removed:
                infos['delete'].remove(info)

        if len(infos['modify']) == 0:
            del infos['modify']
        if len(infos['delete']) == 0:
            del infos['delete']

        return infos


class AddedAndModifiedBySame(BaseRule):
    """If a document has been added and modified by the same user,
    ignore modify activity
    """

    def filter(self, portal, subscriber, infos):
        if 'modify' not in infos:
            return infos
        elif 'add' not in infos:
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
