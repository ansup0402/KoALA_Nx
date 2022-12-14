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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       # QgsFeatureSink,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsVectorLayer,
                       QgsProject,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterDefinition)
import os
from qgis.PyQt.QtGui import QIcon

class KoalaNxSpeedAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    IN_SOURCELYR = 'IN_SOURCELYR'
    IN_TARGETLYR = 'IN_TARGETLYR'
    IN_SOURCELYR_ONLYSELECTED = 'IN_SOURCELYR_ONLYSELECTED'
    IN_TARGETLYR_ONLYSELECTED = 'IN_TARGETLYR_ONLYSELECTED'


    IN_NODE = 'IN_NODE'
    IN_NODE_ID = 'IN_NODE_ID'
    IN_LINK = 'IN_LINK'
    IN_LINK_TYPE = 'IN_LINK_TYPE'
    IN_LINK_FNODE = 'IN_LINK_FNODE'
    IN_LINK_TNODE = 'IN_LINK_TNODE'
    IN_LINK_LENGTH = 'IN_LINK_LENGTH'
    IN_LINK_SPEED = 'IN_LINK_SPEED'
    
    # ?????? ????????? ????????? ?????? ?????? ?????? ??????
    IN_ISDIVISUAL = 'IN_ISDIVISUAL'
    IN_SOURCENAMEFIELD = 'IN_SOURCENAMEFIELD'
    IN_TARGETNAMEFIELD = 'IN_TARGETNAMEFIELD'
    OUT_CSV = 'OUT_CSV'


    OUTPUT = 'OUTPUT'


    __debugging = False
    __cur_dir = None

    @property
    def debugmode(self):
        global __debugging
        return __debugging
        # return self.__debugging

    @debugmode.setter
    def debugmode(self, value):
        global __debugging
        __debugging = value
        # self.__debugging = value

    @property
    def temporaryDirectory(self):
        global __cur_dir
        return __cur_dir


    @temporaryDirectory.setter
    def temporaryDirectory(self, value):
        global __cur_dir
        __cur_dir = value



    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # ???????????????
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.IN_SOURCELYR,
                "??? " + self.tr('Origin Layer'),
                [QgsProcessing.TypeVectorPoint],
                optional=False)
        )
        # QgsProcessingParameterFeatureSource
        # ???????????????
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.IN_TARGETLYR,
                "??? " + self.tr('Destination Layer'),
                [QgsProcessing.TypeVectorPoint],
                optional=False)
        )




        # ???????????????
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.IN_NODE,
                "??? " + self.tr('Node Layer'),
                [QgsProcessing.TypeVectorPoint],
                optional=False)
        )

        # ??????????????? PK
        self.addParameter(
            QgsProcessingParameterField(
                self.IN_NODE_ID,
                self.tr('Unique Field'),
                None,
                self.IN_NODE,
                QgsProcessingParameterField.Any,
                optional=False)
        )

        # ???????????????
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.IN_LINK,
                "??? " + self.tr('Link Layer'),
                [QgsProcessing.TypeVectorLine],
                optional=False)
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.IN_LINK_TYPE,
                self.tr('Network direction'),
                options=[self.tr('One-way'), self.tr('Bidirectional')],
                defaultValue=1,
                optional=False)
        )

        # ?????? ?????? ??????
        self.addParameter(
            QgsProcessingParameterField(
                self.IN_LINK_FNODE,
                self.tr('From Node'),
                None,
                self.IN_LINK,
                QgsProcessingParameterField.Any,
                optional=False)
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.IN_LINK_TNODE,
                self.tr('To Node'),
                None,
                self.IN_LINK,
                QgsProcessingParameterField.Any,
                optional=False)
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.IN_LINK_LENGTH,
                self.tr('Distance Field'),
                None,
                self.IN_LINK,
                QgsProcessingParameterField.Numeric,
                optional=False)
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.IN_LINK_SPEED,
                self.tr('Speed Field'),         # If the speed value is zero, it is replaced by the minimum value
                None,
                self.IN_LINK,
                QgsProcessingParameterField.Numeric,
                optional=False)
        )



        # ?????? ????????? ????????? ?????? ?????? ?????? ??????
        paramIsIndivisual = QgsProcessingParameterBoolean(
            name=self.IN_ISDIVISUAL,
            description=self.tr("Distance to individual destinations"),
            defaultValue=False,
            optional=False)

        paramIsIndivisual.setFlags(paramIsIndivisual.flags() | paramIsIndivisual.FlagAdvanced)
        self.addParameter(paramIsIndivisual)

        paramSrcName = QgsProcessingParameterField(
            name=self.IN_SOURCENAMEFIELD,
            description=self.tr('Name field of Origin layer'),
            defaultValue=False,
            parentLayerParameterName=self.IN_SOURCELYR,
            type=QgsProcessingParameterField.String,
            optional=True)

        paramSrcName.setFlags(paramSrcName.flags() | paramSrcName.FlagAdvanced)
        self.addParameter(paramSrcName)


        paramTarName = QgsProcessingParameterField(
            name=self.IN_TARGETNAMEFIELD,
            description=self.tr('Name field of Destination layer'),
            defaultValue=False,
            parentLayerParameterName=self.IN_TARGETLYR,
            type=QgsProcessingParameterField.String,
            optional=True)

        paramTarName.setFlags(paramTarName.flags() | paramTarName.FlagAdvanced)
        self.addParameter(paramTarName)


        paramOutCSV = QgsProcessingParameterFileDestination(
            name=self.OUT_CSV,
            description=self.tr('CSV Output'),
            defaultValue=None,
            fileFilter='Comma Separated Values (*.csv)',
            createByDefault=False,
            optional=True)
        paramOutCSV.checkValueIsAcceptable = False

        paramOutCSV.setFlags(paramOutCSV.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(paramOutCSV)

        # paramOutCSV = QgsProcessingParameterFile(
        #     name=self.OUT_CSV,
        #     description=self.tr('CSV Output'),
        #     behavior=QgsProcessingParameterFile.File,
        #     defaultValue=None,
        #     fileFilter="csv files (*.csv)",
        #     optional=True)
        #
        # paramOutCSV.setFlags(paramOutCSV.flags() | paramOutCSV.FlagAdvanced | paramOutCSV.FlagIsModelOutput)
        # self.addParameter(paramOutCSV)
        #
        # self.addParameter(QgsProcessingParameterString('Finaloutput', 'finaloutput', 'C:/tmp/xy.csv'))

        # paramOutCSV.checkValueIsAcceptable = False

        # param = QgsProcessingParameterFile('out_csv', 'OUT_CSV', optional=True,
        #                                    behavior=QgsProcessingParameterFile.File, fileFilter='CSV ?????? (*.csv)',
        #                                    defaultValue=None)
        # param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        # self.addParameter(param)
        #





        # ?????? ??????
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Result')
            )
        )
    def onlyselectedfeature(self, parameters, context, paramID):
        layersource = self.parameterAsSource(parameters, paramID, context)
        layervertor = self.parameterAsVectorLayer(parameters, paramID, context)
        onlyselectedFeature = (layersource.featureCount() >= 0 and layervertor is None)
        return onlyselectedFeature

    def getLayerfromParameter(self, parameters, context, paramID):
        if self.onlyselectedfeature(parameters, context, paramID):
            # return self.parameterAsSource(parameters, paramID, context), True
            return self.parameterAsVectorLayer(parameters, paramID, context), True
        else:
            # return self.parameterAsSource(parameters, paramID, context), False
            return self.parameterAsVectorLayer(parameters, paramID, context), False

    def parameter2Dict(self, parameters, context):
        keyword = {}

        keyword['IN_SOURCELYR'], keyword['IN_SOURCELYR_ONLYSELECTED'] = self.getLayerfromParameter(parameters, context, self.IN_SOURCELYR)
        keyword['IN_TARGETLYR'], keyword['IN_TARGETLYR_ONLYSELECTED'] = self.getLayerfromParameter(parameters, context, self.IN_TARGETLYR)

        keyword['IN_NODE'], keyword['IN_NODE_ONLYSELECTED'] = self.getLayerfromParameter(parameters, context, self.IN_NODE)
        keyword['IN_NODE_ID'] = self.parameterAsFields(parameters, self.IN_NODE_ID, context)[0]

        keyword['IN_LINK'], keyword['IN_LINK_ONLYSELECTED'] = self.getLayerfromParameter(parameters, context, self.IN_LINK)
        keyword['IN_LINK_TYPE'] = self.parameterAsEnum(parameters, self.IN_LINK_TYPE, context)  # 0:?????????, 1:?????????
        keyword['IN_LINK_FNODE'] = self.parameterAsFields(parameters, self.IN_LINK_FNODE, context)[0]
        keyword['IN_LINK_TNODE'] = self.parameterAsFields(parameters, self.IN_LINK_TNODE, context)[0]
        keyword['IN_LINK_LENGTH'] = self.parameterAsFields(parameters, self.IN_LINK_LENGTH, context)[0]

        if len(self.parameterAsFields(parameters, self.IN_LINK_SPEED, context)) == 0:
            keyword['IN_LINK_SPEED'] = None
        else:
            keyword['IN_LINK_SPEED'] = self.parameterAsFields(parameters, self.IN_LINK_SPEED, context)[0]


        #################################### ?????? ????????? ????????? ?????? ?????? ?????? ?????? ####################################
        keyword['IN_ISDIVISUAL'] = self.parameterAsBoolean(parameters, self.IN_ISDIVISUAL, context)
        keyword['IN_SOURCENAMEFIELD'] = self.parameterAsFields(parameters, self.IN_SOURCENAMEFIELD, context)[0]
        keyword['IN_TARGETNAMEFIELD'] = self.parameterAsFields(parameters, self.IN_TARGETNAMEFIELD, context)[0]

        try:
            keyword['OUT_CSV'] = self.parameterAsFileOutput(parameters, self.OUT_CSV, context)
        except KeyError:
            keyword['OUT_CSV'] = None
        #########################################################################################################

        keyword['OUTPUT'] = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        return keyword

    def check_userinput(self, parameters):

        isvailid = True
        errMsg = ""

        if parameters['IN_ISDIVISUAL'] == True:
            if parameters['IN_SOURCENAMEFIELD'] == "false":
                if errMsg != "": errMsg += "\n"
                errMsg += "?????? ????????? ????????? ?????? ???????????????. : {}".format(self.tr('Name field of Origin layer'))
                isvailid = False
            if parameters['IN_TARGETNAMEFIELD'] == "false":
                if errMsg != "": errMsg += "\n"
                errMsg += "?????? ????????? ????????? ?????? ???????????????. : {}".format(self.tr('Name field of Destination layer'))
                isvailid = False
            if parameters['OUT_CSV'] == None or parameters['OUT_CSV'] == '':
                if errMsg != "": errMsg += "\n"
                errMsg += "?????? ????????? ????????? ?????? ???????????????. : {}".format(self.tr('CSV Output'))
                isvailid = False

        return isvailid, errMsg

    def processAlgorithm(self, parameters, context, feedback):
        params = self.parameter2Dict(parameters, context)

        if self.debugmode:
            feedback.pushInfo("IN_SOURCENAMEFIELD : {}".format(params['IN_SOURCENAMEFIELD']))
            feedback.pushInfo("IN_TARGETNAMEFIELD : {}".format(params['IN_TARGETNAMEFIELD']))
            feedback.pushInfo("OUT_CSV : {}".format(params['OUT_CSV']))


        isValid, msg = self.check_userinput(parameters=params)
        if isValid == False:
            feedback.pushInfo("========================================================")
            feedback.reportError("????????? ?????????????????????.  ????????? ?????? ?????? ?????? ??? ?????? ?????? ?????????.")
            feedback.reportError(msg, True)
            feedback.pushInfo("========================================================")
            return {self.OUTPUT: None}

        try:
            from .koala_nx_launcher import koala_nx_launcher
        except ImportError:
            from koala_nx_launcher import koala_nx_launcher


        if self.debugmode:
            feedback.pushInfo("****** [START DEBUG] ******")
            feedback.pushInfo(self.temporaryDirectory)
            # feedback.pushInfo(self.TEMP_DIR)

        # launcher = soc_locator_launcher(feedback=feedback, context=context, parameters=params, debugging=debugging,
        #                                 workpath=cur_dir)
        launcher = koala_nx_launcher(feedback=feedback, context=context, parameters=params, debugging=self.debugmode,
                                        workpath=self.temporaryDirectory)


        out_vector, out_csv = launcher.execute_nx()

        if out_csv != None:
            uri = 'file:////%s?type=csv?delimiter=%s' % (out_csv, ",")
            csv_layer = QgsVectorLayer(uri, 'result', 'delimitedtext')
            QgsProject.instance().addMapLayer(csv_layer)

        return {self.OUTPUT: out_vector}



    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return self.tr('time-based network analysis')

    # ??? ??????
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())


    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    #????????? ??? ?????????
    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return self.tr('KoALA-Nx')

    def tr(self, string):
        return QCoreApplication.translate('koala', string)

    def createInstance(self):
        return KoalaNxSpeedAlgorithm()

    def icon(self):
        return QIcon(os.path.join(os.path.split(os.path.dirname(__file__))[0], 'KoALA_Nx/icons', 'icon_koala.ico'))

    def shortHelpString(self):
        # todo : ?????? ?????? ??????
        return "<b>?????? ???????????? ?????? ???????????? ?????? ???????????? ?????? ??????????????? ???????????? ????????? ?????? ???????????? ???????????? ????????? ????????? ???????????????.</b><br>" \
               "<br><b>????????????:</b>" \
               "<ul>" \
               "<li>??????????????? : ???????????? ????????? ????????? ?????? ????????? ????????? ????????? ?????????</li>" \
               "<li>??????????????? : ?????? ???????????? ???????????? ????????? ????????? ?????? ?????? ?????? ????????? ????????? ????????? ?????????</li>" \
               "<li>??????????????? :  ???????????? ????????? ?????? ?????? ???????????????</li>" \
               "<li>??????ID?????? : ?????? ???????????? ID?????? ???????????? ?????? ?????? </li>" \
               "<li>??????????????? : ???????????? ????????? ?????? ?????? ???????????????</li>" \
               "<li>???????????? : ????????? ?????? ???????????? ?????? ??????(?????????/?????????)</li>" \
               "<li>?????? : ????????? ?????? ??? ?????? ??? ?????? ????????? ??????ID?????? ???????????? ?????? ??????</li>" \
               "<li>?????? : ????????? ?????? ??? ?????? ??? ?????? ????????? ??????ID?????? ???????????? ?????? ??????</li>" \
               "<li>???????????? : ????????? ??????(??????) ?????? ???????????? ?????? ??????(?????? m)</li>" \
               "<li>?????? : ?????? ?????? ????????? ?????? ?????? ????????? ???????????? ?????? ??????(?????? km/h)</li>" \
               "<li>?????? ????????? ?????? ?????? : ?????? ?????? ???????????? ?????? ?????? ??????????????? ???????????? ?????? ??????</li>" \
               "<li>????????? ?????? ?????? : ??????????????? ????????? ????????? ??????(Text ??????)</li>" \
               "<li>????????? ?????? ?????? : ??????????????? ????????? ????????? ??????(Text ??????)</li>" \
               "</ul>" \
               "<b>??? ???????????? ????????? ??????/?????? ????????? ????????? ????????? ???????????? ????????????, ?????? ????????? ????????? ??????????????? ????????? ???????????? ???????????? ???????????????.<b>" \
               "<b>??? ?????? ????????? 0??? ?????? ?????? ?????? ?????? ?????? ??? ??? ??????????????? ???????????? ???????????????.<b>"
