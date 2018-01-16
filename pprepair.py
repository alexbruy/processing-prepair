# -*- coding: utf-8 -*-

"""
***************************************************************************
    pprepair.py
    ---------------------
    Date                 : July 2017
    Copyright            : (C) 2017-2018 by Alexander Bruy
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
__copyright__ = '(C) 2017-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterVectorDestination
                      )
from processing_prepair import prepairUtils

pluginPath = os.path.dirname(__file__)


class pprepair(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "pprepair.png"))

    def tr(self, text):
        return QCoreApplication.translate("pprepair", text)

    def name(self):
        return "pprepair"

    def displayName(self):
        return self.tr("pprepair")

    def group(self):
        return self.tr("Geometry tools")

    def groupId(self):
        return "geometrytools"

    def tags(self):
        return self.tr("polygon,repair,broken,geometry").split(",")

    def shortHelpString(self):
        return self.tr("Automatic repair of planar partitions.")

    def helpUrl(self):
        return "https://github.com/tudelft3d/pprepair"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT,
                                                              self.tr("Input layer"),
                                                              [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  self.tr("Repaired polygons"),
                                                                  QgsProcessing.TypeVectorPolygon))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []

        toolPath = prepairUtils.pprepairPath()
        if toolPath == "":
            toolPath = self.name()

        arguments.append(toolPath)
        arguments.append("-i")
        arguments.append(self.parameterAsVectorLayer(parameters, self.INPUT, context).source())
        arguments.append("-o")
        arguments.append(self.parameterAsOutputLayer(parameters, self.OUTPUT, context))
        arguments.append("-fix")

        prepairUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results
