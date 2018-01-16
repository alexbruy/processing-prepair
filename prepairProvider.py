# -*- coding: utf-8 -*-

"""
***************************************************************************
    prepairProvider.py
    ---------------------
    Date                 : May 2014
    Copyright            : (C) 2014-2018 by Alexander Bruy
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
__copyright__ = '(C) 2014-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import QgsProcessingProvider, QgsMessageLog

from processing.core.ProcessingConfig import ProcessingConfig, Setting

from processing_prepair.prepair import prepair
from processing_prepair.pprepair import pprepair
from processing_prepair import prepairUtils

pluginPath = os.path.dirname(__file__)


class PrepairProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algs = []

    def id(self):
        return "prepair"

    def name(self):
        return "prepair"

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "prepair.png"))

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(),
                                            prepairUtils.PREPAIR_ACTIVE,
                                            self.tr("Activate"),
                                            False))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            prepairUtils.PREPAIR_EXECUTABLE,
                                            self.tr("prepair executable"),
                                            prepairUtils.prepairPath(),
                                            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            prepairUtils.PPREPAIR_EXECUTABLE,
                                            self.tr("pprepair executable"),
                                            prepairUtils.prepairPath(),
                                            valuetype=Setting.FILE))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            prepairUtils.PREPAIR_VERBOSE,
                                            self.tr("Log commands output"),
                                            False))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        ProcessingConfig.removeSetting(prepairUtils.PREPAIR_ACTIVE)
        ProcessingConfig.removeSetting(prepairUtils.PREPAIR_EXECUTABLE)
        ProcessingConfig.removeSetting(prepairUtils.PPREPAIR_EXECUTABLE)

    def isActive(self):
        return ProcessingConfig.getSetting(prepairUtils.PREPAIR_ACTIVE)

    def setActive(self, active):
        ProcessingConfig.setSettingValue(prepairUtils.PREPAIR_ACTIVE, active)

    def getAlgs(self):
        algs = [prepair(),
                pprepair()
               ]

        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=''):
        if context == "":
            context = "PrepairProvider"
        return QCoreApplication.translate(context, string)
