"""
/**
* qgis 라이브러리 활용 위한 공통 모듈
*
* @author Song
* @version 0.1
* @Latest Date 27-Dec-2020
* @History
*           09-Sep-2022 : selectbyexpression2 추가
*
* @memo :
*    1) QgsProcessingParameterVectorLayer 타입을 지원하지 않는 경우가 많음
*       - 해결방안 : 'QgsFeatureRequest' 클래스 활용 가능 -> ex) INPUT=input.materialize(QgsFeatureRequest())
*
*
*
*
*/
"""


import os
from qgis.core import (
                    QgsApplication,
                    QgsVectorLayer,
                    QgsVectorFileWriter,
                    QgsProcessingFeatureSourceDefinition,
                    QgsFeatureRequest
                    )


from processing.core.Processing import Processing
Processing.initialize()
import processing


class qgsprocessUtils:
    def __init__(self, feedback, context, debugmode=False):
        self.debugging = debugmode
        self.feedback = feedback
        self.context = context

    def checkAlgname(self, findalgid):
        algid = ""
        for alg in QgsApplication.processingRegistry().algorithms():
            if alg.id() == findalgid:
                algid = alg.id()
                #            bchecked = True

                break
        return algid


    
    
    def run_algprocessing(self, algname, params):
        if self.feedback.isCanceled(): return None
        result = processing.run(algname,
                                params,
                                context=self.context,
                                feedback=self.feedback)
        return result


    def rectanglesovalsdiamonds(self, input, onlyselected=False, shape=0, width=1.0, height=1.0, rotation=None, segment=36, output='TEMPORARY_OUTPUT'):
        # 0 — Rectangles
        # 1 — Ovals
        # 2 — Diamonds
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'

        algname = ""
        if algname == "": algname = self.checkAlgname("qgis:rectanglesovalsdiamondsfixed")
        if algname == "": algname = self.checkAlgname("native:rectanglesovalsdiamondsfixed")
        if algname == "": algname = self.checkAlgname("qgis:rectanglesovalsdiamonds")
        if algname == "": algname = self.checkAlgname("native:rectanglesovalsdiamonds")

        self.feedback.pushInfo("************ checkAlgname %s : " % algname)



        inputsource = input
        if onlyselected:
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      SHAPE=shape,
                      WIDTH=width,
                      HEIGHT=height,
                      ROTATION=rotation,
                      SEGMENTS=segment,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']


    def bufferwithQgis(self, input, onlyselected, distance, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'native:multiringconstantbuffer'

        inputsource = input
        if onlyselected:
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      DISTANCE=distance,
                      OUTPUT=output,
                      RINGS=1)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def createGridfromLayer(self, sourcelayer, gridsize, type=0, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        # qgis 3.10부터는 native:creategrid로 변경됨
        # algname = "qgis:creategrid"
        algname = "native:creategrid"

        layer = sourcelayer
        # layer = QgsVectorLayer(path=sourcelayer)

        extent = layer.extent()
        xmin, ymin, xmax, ymax = extent.toRectF().getCoords()
        extent = str(xmin) + ',' + str(xmax) + ',' + str(ymin) + ',' + str(ymax)

        # TYPE
        # 0 — Point
        # 1 — Line
        # 2 — Rectangle(polygon)
        # 3 — Diamond(polygon)
        # 4 — Hexagon(polygon)

        params = dict(TYPE=type,
                      EXTENT=extent,
                      HSPACING=gridsize,
                      VSPACING=gridsize,
                      HOVERLAY=0,
                      VOVERLAY=0,
                      CRS=layer.crs(),
                      OUTPUT=output
                      )

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def clipwithQgis(self, input, onlyselected, overlay, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = "native:clip"

        inputsource = input
        if onlyselected:
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      OVERLAY=overlay,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def dissolvewithQgis(self, input, onlyselected, field=None, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'native:dissolve'

        inputsource = input
        if onlyselected:
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      FIELD=field,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def dissolvewithQgis2(self, input, onlyselected, field=None, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'qgis:dissolve'

        inputsource = input
        if onlyselected:
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      FIELD=field,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def addField(self, input, fid, ftype, flen, fprecision, output='TEMPORARY_OUTPUT'):

        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'qgis:addfieldtoattributestable'

        inputsource = input

        params = dict(INPUT=inputsource,
                      FIELD_NAME=fid,
                      FIELD_TYPE=ftype,
                      FIELD_LENGTH=flen,
                      FIELD_PRECISION=fprecision,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def fieldCalculate(self, input, fid, ftype, flen, fprecision, formula, newfield=False,
                       output='TEMPORARY_OUTPUT'):

        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        # algname = 'qgis:advancedpythonfieldcalculator'
        algname = 'qgis:fieldcalculator'

        inputsource = input

        params = dict(INPUT=inputsource,
                      FIELD_NAME=fid,
                      FIELD_TYPE=ftype,
                      FIELD_LENGTH=flen,
                      FIELD_PRECISION=fprecision,
                      NEW_FIELD=newfield,
                      FORMULA=formula,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']


    def renameField(self, layer, fromName, toName, baseName='renamedlayer'):
        vector = QgsVectorLayer(path=layer, baseName=baseName)
        vector.startEditing()
        # idx = result.fieldNameIndex('HubName')
        idx = vector.fields().indexFromName(fromName)
        vector.renameAttribute(idx, toName)
        vector.commitChanges()

        return vector.source()

    def intersection(self, input, inputonlyseleceted, inputfields,
                     overlay, overayprefix, overonlyselected=False, overlayer_fields=None,
                     output='TEMPORARY_OUTPUT'):

        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'native:intersection'

        inputsource = input
        if inputonlyseleceted: inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        overlaysource = overlay
        if overonlyselected: overlaysource = QgsProcessingFeatureSourceDefinition(overlay, True)

        params = dict(INPUT=inputsource,
                      INPUT_FIELDS=inputfields,
                      OVERLAY=overlaysource,
                      OVERLAY_FIELDS_PREFIX=overayprefix,
                      OVERLAY_FIELDS=overlayer_fields,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']




    def countpointsinpolygon(self, polygons, points, field, polyonlyselected=False, pointonlyseleced=False, weight=None, classfield=None, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'qgis:countpointsinpolygon'

        polyinputsource = polygons
        if polyonlyselected: polyinputsource = QgsProcessingFeatureSourceDefinition(polygons, True)

        pointinputsource = points
        if pointonlyseleced: pointinputsource = QgsProcessingFeatureSourceDefinition(points, True)

        params = dict(POLYGONS=polyinputsource,
                      POINTS=pointinputsource,
                      FIELD=field,
                      WEIGHT=weight,
                      CLASSFIELD=classfield,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def centroidlayer(self, input, onlyselected, allparts=False, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'native:centroids'

        inputsource = input
        if onlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      ALL_PARTS=allparts,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']




    def nearesthubpoints(self, input, onlyselected, sf_hub, hubfield, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = "qgis:distancetonearesthubpoints"

        inputsource = input
        if onlyselected:
            # self.feedback.pushInfo('onlyselected')
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      HUBS=sf_hub,
                      FIELD=hubfield,
                      UNIT=0,
                      OUTPUT=output)

        result = self.run_algprocessing(algname=algname, params=params)['OUTPUT']

        if output.find('TEMPORARY_OUTPUT') < 0:
            basename = 'output'
            result = self.renameField(layer=result, fromName='HubName', toName=hubfield, baseName=basename)
        else:
            result.startEditing()
            idx = result.fields().indexFromName('HubName')
            result.renameAttribute(idx, hubfield)
            result.commitChanges()
        return result


    def nearesthubpoints2(self, input, onlyselected, sf_hub, hubfield, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = "qgis:distancetonearesthubpoints"

        inputsource = input
        if onlyselected:
            # self.feedback.pushInfo('onlyselected')
            inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource.materialize(QgsFeatureRequest()),
                      HUBS=sf_hub,
                      FIELD=hubfield,
                      UNIT=0,
                      OUTPUT=output)

        result = self.run_algprocessing(algname=algname, params=params)['OUTPUT']

        if output.find('TEMPORARY_OUTPUT') < 0:
            basename = 'output'
            result = self.renameField(layer=result, fromName='HubName', toName=hubfield, baseName=basename)
        else:
            result.startEditing()
            idx = result.fields().indexFromName('HubName')
            result.renameAttribute(idx, hubfield)
            result.commitChanges()
        return result


    def distancematrix(self, input, inputonlyselected, inputfield, target, targetonlyseleted, targetfield,
                       matrixtype=2, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'qgis:distancematrix'

        inputsource = input
        tarsource = target
        if inputonlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)
        if targetonlyseleted: tarsource = QgsProcessingFeatureSourceDefinition(target, True)

        params = dict(INPUT=inputsource,
                      INPUT_FIELD=inputfield,
                      TARGET=tarsource,
                      TARGET_FIELD=targetfield,
                      MATRIX_TYPE=matrixtype,
                      NEAREST_POINTS=0,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def multiparttosingleparts(self, input, onlyselected, output='TEMPORARY_OUTPUT'):

        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'native:multiparttosingleparts'
        #algname = 'qgis:multiparttosingleparts'

        inputsource = input
        if onlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      OUTPUT=output)
        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def joinattributesbylocation(self, input, join, inputonlyselected=False, joinonlyselected=False, joinfiels=[], method=0, predicate=[0], prefix='', discardnomatching=False, output='TEMPORARY_OUTPUT'):

        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'qgis:joinattributesbylocation'

        inputsource = input
        joinsource = join

        if inputonlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)
        if joinonlyselected: joinsource = QgsProcessingFeatureSourceDefinition(join, True)

        params = dict(INPUT=inputsource,
                      JOIN=joinsource,
                      JOIN_FIELDS=joinfiels,
                      METHOD=method,     # 0 — (one-to-many), 1 — (one - to - one)
                      PREDICATE=predicate, # 0 — intersects, 1 — contains, 2 — equals, 3 — touches, 4 — overlaps, 5 — within, 6 — crosses
                      PREFIX=prefix,
                      DISCARD_NONMATCHING=discardnomatching,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def joinattributetable(self, input1, input1onlyselected, input2, input2onlyselected, field1, field2,
                           prefix='M_', output='TEMPORARY_OUTPUT'):

        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'native:joinattributestable'

        inputsource1 = input1
        inputsource2 = input2
        if input1onlyselected: inputsource1 = QgsProcessingFeatureSourceDefinition(input1, True)
        if input2onlyselected: inputsource2 = QgsProcessingFeatureSourceDefinition(input2, True)

        params = dict(INPUT=inputsource1,
                      FIELD=field1,
                      INPUT_2=inputsource2,
                      FIELD_2=field2,
                      FIELDS_TO_COPY=[],
                      METHOD=1,
                      PREFIX=prefix,
                      DISCARD_NONMATCHING=False,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    # predicate : 0—intersect, 1—contain, 2—disjoint, 3—equal, 4—touch, 5—overlap, 6—are within, 7—cross
    # method : 0—creating new selection, 1—adding to current selection, 2—selecting within current selection
    #          3 — removing from current selection
    def selectbylocation(self, input, intersect, predicate, method, output='TEMPORARY_OUTPUT'):
        algname = "qgis:selectbylocation"
        params = dict(INPUT=input,
                      INTERSECT=intersect,
                      PREDICATE=predicate,
                      METHOD=method,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def selectbyexpression(self, input, expression, method=0):
        algname = "qgis:selectbyexpression"
        params = dict(INPUT=input,
                      EXPRESSION=expression,
                      METHOD=method)
        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def selectbyexpression2(self, input, expression, method=0):
        algname = "qgis:selectbyexpression"
        params = dict(INPUT=input.materialize(QgsFeatureRequest()),
                      EXPRESSION=expression,
                      METHOD=method)
        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']



    def saveselectedfeatrues(self, input, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = "native:saveselectedfeatures"
        params = dict(INPUT=input,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def duplicate_layer(self, sourcelayer, copylayer):
        algname = "qgis:selectbyexpression"
        params = dict(INPUT=sourcelayer,
                      EXPRESSION='1=1',
                      METHOD=0)
        layer = self.run_algprocessing(algname=algname, params=params)['OUTPUT']

        algname = "native:saveselectedfeatures"
        params = dict(INPUT=layer,
                      OUTPUT=copylayer)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def statisticsbycategories(self, input, onlyselected, categoriesfields, valuefield, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = 'qgis:statisticsbycategories'

        inputsource = input
        if onlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      CATEGORIES_FIELD_NAME=categoriesfields,
                      METHOD=0,
                      VALUES_FIELD_NAME=valuefield,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def vectorlayer2ShapeFile(self, vectorlayer, output, destCRS, fileEncoding='utf-8'):
        return QgsVectorFileWriter.writeAsVectorFormat(layer=vectorlayer,
                                                fileName=output,
                                                fileEncoding=fileEncoding,
                                                destCRS=destCRS,
                                                driverName='ESRI Shapefile')
        #  select & export로 변경...




    def differencelayer(self, input, onlyselected, overlay, overonlyselected, output='TEMPORARY_OUTPUT'):
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = "native:difference"

        inputsource = input
        if onlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        oversource = overlay
        if overonlyselected: oversource = QgsProcessingFeatureSourceDefinition(overlay, True)

        params = dict(INPUT=inputsource,
                      OVERLAY=oversource,
                      OUTPUT=output)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']

    def refactorfields(self, input , onlyselected, refieldmapping, output='TEMPORARY_OUTPUT'):
      # qgis:refactorfields
      # {'FIELDS_MAPPING': [{'expression': '"NEAR_FID"', 'length': 10, 'name': 'NEAR_FID', 'precision': 0, 'type': 4},
      #                     {'expression': '"pop_all"', 'length': 18, 'name': 'pop_all', 'precision': 11, 'type': 6}],
      #  'INPUT': '/Users/song-ansup/Desktop/KoALA_data/logfile/cliped_pop.shp', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        if output is None or output == '': output = 'TEMPORARY_OUTPUT'
        algname = "qgis:refactorfields"

        inputsource = input
        if onlyselected: inputsource = QgsProcessingFeatureSourceDefinition(input, True)

        params = dict(INPUT=inputsource,
                      FIELDS_MAPPING=refieldmapping,
                      OUTPUT=output)
        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']


    def writeAsVectorLayer(self, layername):
        base = os.path.basename(layername)
        baseName = os.path.splitext(base)[0]

        # self.feedback.pushInfo(base)
        # self.feedback.pushInfo(baseName)

        layer = QgsVectorLayer(path=layername, baseName=baseName, providerLib='ogr')
        if layer.isValid():
            return layer
        else:
            self.feedback.pushInfo("%s is not valid" % layername)
            return None





    # 이함수는 좀 더 테스트 필요
    def statisticsfromfield(self, input, numericfield, output_html='TEMPORARY_OUTPUT'):
        if output_html is None or output_html == '': output_html = 'TEMPORARY_OUTPUT'
        algname = 'qgis:basicstatisticsforfields'

        inputsource = input
        params = dict(INPUT_LAYER=inputsource,
                      FIELD_NAME=numericfield,
                      OUTPUT_HTML_FILE=output_html)

        return self.run_algprocessing(algname=algname, params=params)

    # 테스트 되지 않은 함수... 확인 필요
    def createspatialindex(self, input):
        algname = 'qgis:createspatialindex'

        inputsource = input
        params = dict(INPUT=inputsource)

        return self.run_algprocessing(algname=algname, params=params)['OUTPUT']
