# -*- coding: utf-8 -*-

"""
***************************************************************************
    prepairProvider.py
    ---------------------
    Date                 : May 2014
    Copyright            : (C) 2014 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'May 2014'
__copyright__ = '(C) 2014, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


from PyQt4.QtGui import QIcon

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from processing.tools import system

from processing_prepair.prepair import prepair
from processing_prepair.prepairUtils import prepairUtils

from processing_prepair.resources_rc import *


class prepairProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)

        self.activate = False

        self.alglist = [prepair()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

        ProcessingConfig.addSetting(
            Setting(self.getDescription(), prepairUtils.PREPAIR_FOLDER,
            self.tr('prepair folder'), prepairUtils.prepairPath()))

    def unload(self):
        AlgorithmProvider.unload(self)

        ProcessingConfig.removeSetting(prepairUtils.PREPAIR_FOLDER)

    def getName(self):
        return 'prepair'

    def getDescription(self):
        return 'prepair'

    def getIcon(self):
        return QIcon(':/icons/prepair.png')

    def _loadAlgorithms(self):
        self.algs = self.alglist
