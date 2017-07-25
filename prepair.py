# -*- coding: utf-8 -*-

"""
***************************************************************************
    prepair.py
    ---------------------
    Date                 : November 2014
    Copyright            : (C) 2014-2017 by Alexander Bruy
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
__date__ = 'November 2014'
__copyright__ = '(C) 2014-2017, Alexander Bruy'

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


class prepair(GeoAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    PARADIGM = 'PARADIGM'
    MIN_AREA = 'MIN_AREA'
    SNAP_ROUNDING = 'SNAP_ROUNDING'
    ONLY_INVALID = 'ONLY_INVALID'
    OUTPUT = 'OUTPUT'

    PARADIGMS = ['Odd-even', 'Point set topology']

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'prepair.png'))

    def defineCharacteristics(self):
        self.name = 'prepair'
        self.group = 'prepair'

        self.addParameter(ParameterVector(self.INPUT_LAYER,
            self.tr('Layer to repair'), [ParameterVector.VECTOR_TYPE_POLYGON]))
        self.addParameter(ParameterSelection(self.PARADIGM,
            self.tr('Repair paradigm'), self.PARADIGMS, 0))
        self.addParameter(ParameterNumber(self.MIN_AREA,
            self.tr('Remove sliver polugons'), 0.0, 999999.999999, 0.0))
        self.addParameter(ParameterNumber(self.SNAP_ROUNDING,
            self.tr('Snap round input'), 0, 999999, 0))
        self.addParameter(ParameterBoolean(self.ONLY_INVALID,
            self.tr('Process only invalid geometries'), False))

        self.addOutput(OutputVector(self.OUTPUT, self.tr('Repaired layer')))

    def processAlgorithm(self, progress):
        layer = dataobjects.getObjectFromUri(
            self.getParameterValue(self.INPUT_LAYER))

        paradigm = self.getParameterValue(self.PARADIGM)
        minArea = self.getParameterValue(self.MIN_AREA)
        snapRounding = self.getParameterValue(self.SNAP_ROUNDING)
        onlyInvalid = self.getParameterValue(self.ONLY_INVALID)

        tmpFile = system.getTempFilename()

        commands = []
        commands.append(prepairUtils.prepairPath())

        if paradigm == 1:
            commands.append('--setdiff')

        if minArea > 0.0:
            commands.append('--minarea')
            commands.append(unicode(minArea))

        if snapRounding > 0:
            commands.append('--isr')
            commands.append(unicode(snapRounding))

        commands.append('-f')
        commands.append(tmpFile)

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            layer.pendingFields().toList(), QGis.WKBMultiPolygon , layer.crs())

        features = vector.features(layer)
        total = 100.0 / len(features)
        for count, ft in enumerate(features):
            geom = ft.geometry()
            if onlyInvalid and len(geom.validateGeometry()) == 0:
                progress.setInfo(
                    self.tr('Feature {} is valid, skipping...'.format(ft.id())))
                progress.setPercentage(int(count * total))
                continue

            with open(tmpFile, 'w') as f:
                f.write(geom.exportToWkt())

            result = prepairUtils.execute(commands, progress)

            if len(result) == 0:
                progress.setInfo(self.tr('Feature {} not repaired'.format(ft.id())))
                progress.setPercentage(int(count * total))
                continue

            geom = QgsGeometry.fromWkt(result[0].strip())
            if geom is None or geom.isGeosEmpty():
                progress.setInfo(
                    self.tr('Empty geometry after repairing feature {}, '
                            'skipping...'.format(ft.id())))
                progress.setPercentage(int(count * total))
                continue

            ft.setGeometry(geom)
            writer.addFeature(ft)

            progress.setPercentage(int(count * total))

        del writer
