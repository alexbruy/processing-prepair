# -*- coding: utf-8 -*-

"""
***************************************************************************
    pprepair.py
    ---------------------
    Date                 : July 2017
    Copyright            : (C) 2017 by Alexander Bruy
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
__date__ = 'July 2017'
__copyright__ = '(C) 2017, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon

from qgis.core import *

from processing.core.Processing import Processing
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.GeoAlgorithm import GeoAlgorithm

from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterBoolean
from processing.core.parameters import ParameterSelection
from processing.core.outputs import OutputVector

from processing.tools import dataobjects
from processing.tools import vector
from processing.tools import system

from processing_prepair.prepairUtils import prepairUtils

pluginPath = os.path.dirname(__file__)


class pprepair(GeoAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    OUTPUT = 'OUTPUT'

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'pprepair.png'))

    def defineCharacteristics(self):
        self.name = 'pprepair'
        self.group = 'prepair'

        self.addParameter(ParameterVector(self.INPUT_LAYER,
            self.tr('Layer to repair'), [ParameterVector.VECTOR_TYPE_POLYGON]))
        self.addOutput(OutputVector(self.OUTPUT, self.tr('Repaired layer')))

    def processAlgorithm(self, progress):
        inputFile = self.getParameterValue(self.INPUT_LAYER)
        outputFile = self.getOutputValue(self.OUTPUT)

        commands = []
        toolPath = prepairUtils.pprepairPath()
        if not toolPath:
            toolPath = 'prepair'
        commands.append(toolPath)

        commands.append('-i')
        commands.append(inputFile)
        commands.append('-o')
        commands.append(outputFile)
        commands.append('-fix')

        prepairUtils.execute(commands, progress)
