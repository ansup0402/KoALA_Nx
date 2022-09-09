# -*- coding: utf-8 -*-

"""
/***************************************************************************
 KoalaNetwork
                                 A QGIS plugin
 KoALA Network
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-09-06
        copyright            : (C) 2022 by Hyunjoong Kim
        email                : khj1122452@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Hyunjoong Kim'
__date__ = '2022-09-06'
__copyright__ = '(C) 2022 by Hyunjoong Kim'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from qgis.PyQt.QtCore import QSettings, QCoreApplication, QTranslator, qVersion
from qgis.core import QgsProcessingProvider
from .koala_nx_distance_algorithm import KoalaNxDistanceAlgorithm
from .koala_nx_speed_algorithm import KoalaNxSpeedAlgorithm

import os
import tempfile

class KoalaNxProvider(QgsProcessingProvider):

    def __init__(self):
        """
         Default constructor.
         """

        self.debugging = False
        self.debugging = True

        self.tempdir = tempfile.TemporaryDirectory()

        QgsProcessingProvider.__init__(self)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            os.path.dirname(__file__),
            'i18n',
            'koala_{}.qm'.format(locale))

        self.translator = None
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

        if qVersion() > '4.3.3':
            QCoreApplication.installTranslator(self.translator)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        nxDist = KoalaNxDistanceAlgorithm()
        nxDist.temporaryDirectory = self.tempdir.name
        nxDist.debugmode = self.debugging
        self.addAlgorithm(nxDist)

        nxSpeed = KoalaNxSpeedAlgorithm()
        nxSpeed.temporaryDirectory = self.tempdir.name
        nxSpeed.debugmode = self.debugging
        self.addAlgorithm(nxSpeed)



    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'KoALA'

    # 툴박스 이름
    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('KoALA')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()