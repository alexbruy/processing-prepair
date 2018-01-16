# -*- coding: utf-8 -*-

"""
***************************************************************************
    prepairUtils.py
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
import subprocess

from qgis.core import QgsMessageLog, QgsProcessingFeedback
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig

PREPAIR_ACTIVE = "PREPAIR_ACTIVE"
PREPAIR_EXECUTABLE = "PREPAIR_EXECUTABLE"
PPREPAIR_EXECUTABLE = "PPREPAIR_EXECUTABLE"
PREPAIR_VERBOSE = "PREPAIR_VERBOSE"


def prepairPath():
    filePath = ProcessingConfig.getSetting(PREPAIR_EXECUTABLE)
    return filePath if filePath is not None else ""


def pprepairPath():
    filePath = ProcessingConfig.getSetting(PPREPAIR_EXECUTABLE)
    return filePath if filePath is not None else ""


def execute(commands, feedback=None):
    if feedback is None:
        feedback = QgsProcessingFeedback()

    fused_command = " ".join([str(c) for c in commands])
    QgsMessageLog.logMessage(fused_command, "Processing", QgsMessageLog.INFO)
    feedback.pushInfo("preparir command:")
    feedback.pushCommandInfo(fused_command)
    feedback.pushInfo("prepair command output:")

    loglines = []
    with subprocess.Popen(fused_command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stdin=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True) as proc:
        try:
            for line in iter(proc.stdout.readline, ""):
                feedback.pushConsoleInfo(line)
                loglines.append(line)
        except:
            pass

    if ProcessingConfig.getSetting(PREPAIR_VERBOSE):
        QgsMessageLog.logMessage("\n".join(loglines), "Processing", QgsMessageLog.INFO)

    return loglines
