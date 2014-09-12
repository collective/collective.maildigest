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
        new_modified = []
        for modified_info in info['modify']:
            uid = (modified_info['uid'], modified_info['actor'])
            if uid not in uid_actors:
                uid_actors.add(uid)
                new_modified.append(modified_info)

        info['modify'] = new_modified
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
        if 'add' not in infos or 'publish' not in infos:
            return infos

        published = set([info['uid'] for info in infos['publish']])
        new_add = []
        for info in infos['add']:
            if info['uid'] not in published:
                new_add.append(info)

        if len(new_add) == 0:
            del infos['add']
        else:
            infos['add'] = new_add

        return infos


class ModifiedAndRemoved(BaseRule):
    """If a document has been removed, do not display modify activity
    """

    def filter(self, portal, subscriber, infos):
        if 'modify' not in infos or 'delete' not in infos:
            return infos

        new_modify = []
        removed = set([info['uid'] for info in infos['delete']])
        for info in infos['modify']:
            if info['uid'] not in removed:
                new_modify.append(info)

        new_delete = []
        modified = set([info['uid'] for info in infos['modify']])
        for info in infos['delete']:
            if info['uid'] not in modified:
                new_delete.add(info)

        if len(new_modify) == 0:
            del infos['modify']
        else:
            infos['modify'] = new_modify

        if len(new_delete) == 0:
            del infos['delete']
        else:
            infos['delete'] = new_delete

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
                    filtered.setdefault(activity, []).append(info)

        return filtered
