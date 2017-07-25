# -*- coding: utf-8 -*-

"""
***************************************************************************
    prepairUtils.py
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
import subprocess

from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig


class prepairUtils:

    PREPAIR_FOLDER = 'PREPAIR_FOLDER'

    @staticmethod
    def prepairPath():
        folder = ProcessingConfig.getSetting(prepairUtils.PREPAIR_FOLDER)
        return folder if folder is not None else ''

    @staticmethod
    def execute(command, progress):
        fused_command = ''.join(['"{}" '.format(c) for c in command])

        loglines = []
        proc = subprocess.Popen(
            fused_command,
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            ).stdout
        for line in iter(proc.readline, ''):
            loglines.append(line)

        return loglines
