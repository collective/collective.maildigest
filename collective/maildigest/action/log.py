from .. import logger
from ..interfaces import IDigestAction

from . import BaseAction

class Log(BaseAction):

    def execute(self, portal, userid, info):
        logger.info("digest info for %s : %s", userid, info)