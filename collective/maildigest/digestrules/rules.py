from copy import deepcopy

class BaseRule(object):

    def __call__(self, info):
        return self.filter(info)

class SameEditor(BaseRule):

    def filter(self, info):
        """remove from info when a content has been modified by same user many times
        """
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
