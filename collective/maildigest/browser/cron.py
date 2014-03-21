from Products.Five.browser import BrowserView

from collective.maildigest.tool import get_tool


class DigestCron(BrowserView):

    def __call__(self):
        get_tool().check_digests_to_purge_and_apply(
            debug=self.request.get('maildigest-debug-mode', False))
