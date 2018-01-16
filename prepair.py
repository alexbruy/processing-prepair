# -*- coding: utf-8 -*-

"""
***************************************************************************
    prepair.py
    ---------------------
    Date                 : November 2014
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
__date__ = 'November 2014'
__copyright__ = '(C) 2014-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from collections import OrderedDict

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsGeometry,
                       QgsFeatureSink,
                       QgsFeatureRequest,
                       QgsProcessing,
                       QgsProcessingUtils,
                       QgsProcessingAlgorithm,
                       QgsProcessingFeatureSource,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink
                      )
from processing_prepair import prepairUtils

pluginPath = os.path.dirname(__file__)


class prepair(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    PARADIGM = 'PARADIGM'
    MIN_AREA = 'MIN_AREA'
    SNAP_ROUNDING = 'SNAP_ROUNDING'
    ONLY_INVALID = 'ONLY_INVALID'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "prepair.png"))

    def tr(self, text):
        return QCoreApplication.translate("prepair", text)

    def name(self):
        return "prepair"

    def displayName(self):
        return self.tr("prepair")

    def group(self):
        return self.tr("Geometry tools")

    def groupId(self):
        return "geometrytools"

    def tags(self):
        return self.tr("polygon,repair,broken,geometry").split(",")

    def shortHelpString(self):
        return self.tr("Automatic repair of single polygons (according to the "
                       "OGC Simple Features / ISO19107 rules) using "
                       "a constrained triangulation.")

    def helpUrl(self):
        return "https://github.com/tudelft3d/prepair"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.paradigms = [self.tr("Odd-even"), self.tr("Point set topology")]

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr("Input layer"),
                                                              [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterEnum(self.PARADIGM,
                                                     self.tr("Repair paradigm"),
                                                     self.paradigms,
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.MIN_AREA,
                                                       self.tr("Remove sliver polygons"),
                                                       QgsProcessingParameterNumber.Double,
                                                       0.0,
                                                       True))
        self.addParameter(QgsProcessingParameterNumber(self.SNAP_ROUNDING,
                                                       self.tr("Snap round input"),
                                                       QgsProcessingParameterNumber.Integer,
                                                       0,
                                                       True))
        self.addParameter(QgsProcessingParameterBoolean(self.ONLY_INVALID,
                                                        self.tr("Process only invalid geometries"),
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT,
                                                            self.tr("Repaired polygons"),
                                                            QgsProcessing.TypeVectorPolygon))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []

        toolPath = prepairUtils.prepairPath()
        if toolPath == "":
            toolPath = self.name()

        arguments.append(toolPath)

        paradigm = self.parameterAsEnum(parameters, self.PARADIGM, context)
        if paradigm == 1:
            arguments.append("--setdiff")

        minArea = self.parameterAsDouble(parameters, self.MIN_AREA, context)
        if minArea > 0.0:
            arguments.append("--minarea")
            arguments.append("{}".format(minArea))

        snapRounding = self.parameterAsInt(parameters, self.SNAP_ROUNDING, context)
        if snapRounding > 0:
            arguments.append("--isr")
            arguments.append("{}".format(snapRounding))

        onlyInvalid = self.parameterAsBool(parameters, self.ONLY_INVALID, context)

        tmpFile = QgsProcessingUtils.generateTempFilename("prepair.shp")
        arguments.append("-f")
        arguments.append(tmpFile)

        source = self.parameterAsSource(parameters, self.INPUT, context)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               source.fields(), source.wkbType(), source.sourceCrs())

        features = source.getFeatures(QgsFeatureRequest(), QgsProcessingFeatureSource.FlagSkipGeometryValidityChecks)
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, feat in enumerate(features):
            if feedback.isCanceled():
                break

            geom = feat.geometry()
            if onlyInvalid and len(geom.validateGeometry()) == 0:
                feedback.pushInfo(
                    self.tr("Feature {} is valid, skipping…".format(feat.id())))
                feedback.setProgress(int(count * total))
                continue

            with open(tmpFile, "w") as f:
                f.write(geom.asWkt())

            result = prepairUtils.execute(arguments, feedback)

            if len(result) == 0:
                feedback.poushInfo(self.tr("Feature {} not repaired".format(feat.id())))
                feedback.setProgress(int(count * total))
                continue

            geom = QgsGeometry.fromWkt(result[0].strip())
            if geom is None or geom.isEmpty():
                feedback.pushInfo(self.tr("Empty geometry after repairing "
                                          "feature {}, skipping…".format(feat.id())))
                feedback.setProgress(int(count * total))
                continue

            feat.setGeometry(geom)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
