from .. import logger

from . import BaseAction

class Log(BaseAction):

    def execute(self, portal, subscriber, info):
        logger.info("digest info for %s : %s", subscriber[1], info)