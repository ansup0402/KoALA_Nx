"""
/**
* koala 네트워크분석 관련 공통 기능
*
* @author Song
* @version 0.2
* @memo : soc_locator_model 클래스 승계(v0.1)
* @Latest Date 00-Oct-2022
* @History
*           09-Sep-2022 :   [전체] selectbyexpression -> selectbyexpression2 변경
*                           [추가] anal_NetworkSum()
*                           [추가] make_networksumScore()
*                           [createNodeEdgeInGraph] 속도 기반 분석시 단위를 km로 수정(/1000)
*                           [shortestAllnodes] 네트워크 분석 결과 저장 및 불러오기(pickle)
*                           [__init__] 변수 추가, 관련 property 추가
*                         ...
*
* @memo : soc_locator_model 클래스 승계(v0.1)
*/
"""




import os
import networkx as nx
import pandas as pd
import numpy as np
from qgis.core import QgsVectorLayer
import tempfile
import pickle


from processing.core.Processing import Processing
Processing.initialize()
import processing

class koala_model:

    def __init__(self, feedback, context, debugmode=False, workpath=None):
        try:
            from .qgsprocssing_utils import qgsprocessUtils as qgsutils
        except ImportError:
            from qgsprocssing_utils import qgsprocessUtils as qgsutils

        self.workpath = workpath
        self.qgsutils = qgsutils(feedback=feedback, context=context, debugmode=debugmode)

        self.debugging = debugmode
        self.feedback = feedback
        self.context = context

        # 변수 추가(koala_nx용)
        self.__sourcelayer = None
        self.__targetlayer = None
        self.__networkSum = None

        self.allshortestnodes = {}
        self.nxGraph = None
        self.__nodelayer = None
        self.__nodeID = ''
        self.__linklayer = None
        self.__toNodefield = ''
        self.__fromNodefield = ''
        self.__linklenfield = ''
        self.__linkSpeed = None
        self.__boundarylayer = None
        self.__potentiallayer = None
        self.__populationLayer = None
        self.__popSinglepartlayer = None

        self.__currentSOClayer = None
        self.__popcntField = ''
        self.__livingareaLayer = None
        self.__livinglyrID = ''
        self.__cutoff = 0
        self.__outofcutoff = 0
        self.__dfPop = None
        self.__dictFinalwithScore = {}
        self.__dtFinalwithsScore = None

        self.__currentSOCID = ''
        self.__potentialID = ''
        self.__poplyrID = ''

        self.__classify_count = 10

    @property
    def targetlayer(self):
        return (self.__targetlayer)

    @targetlayer.setter
    def targetlayer(self, value):
        self.__targetlayer = value

    # 속성 추가
    @property
    def sourcelayer(self):
        return (self.__sourcelayer)

    @sourcelayer.setter
    def sourcelayer(self, value):
        self.__sourcelayer = value


    @property
    def boundary(self):
        return (self.__boundarylayer)

    @boundary.setter
    def boundary(self, value):
        self.__boundarylayer = value

    @property
    def classify_count(self):
        return (self.__classify_count)

    @classify_count.setter
    def classify_count(self, value):
        self.__classify_count = value

    @property
    def cutoff(self):
        return (self.__cutoff)

    @cutoff.setter
    def cutoff(self, value):
        if value is None:
            self.__cutoff = 0
        else:
            self.__cutoff = value

    @property
    def outofcutoff(self):
        return (self.__outofcutoff)

    @outofcutoff.setter
    def outofcutoff(self, value):
        self.__outofcutoff = value

    @property
    def currentSOC(self):
        return (self.__currentSOClayer)

    @currentSOC.setter
    def currentSOC(self, value):
        self.__currentSOClayer = value

    @property
    def currentSOCID(self):
        return (self.__currentSOCID)

    @currentSOCID.setter
    def currentSOCID(self, value):
        self.__currentSOCID = value

    @property
    def potentiallayer(self):
        return (self.__potentiallayer)

    @potentiallayer.setter
    def potentiallayer(self, value):
        self.__potentiallayer = value

    @property
    def potentialID(self):
        return (self.__potentialID)

    @potentialID.setter
    def potentialID(self, value):
        self.__potentialID = value

    @property
    def populationLayer(self):
        return (self.__populationLayer)

    @populationLayer.setter
    def populationLayer(self, value):
        self.__populationLayer = value

    @property
    def popIDField(self):
        return (self.__poplyrID)

    @popIDField.setter
    def popIDField(self, value):
        self.__poplyrID = value

    @property
    def popcntField(self):
        return (self.__popcntField)

    @popcntField.setter
    def popcntField(self, value):
        self.__popcntField = value

    @property
    def livingareaLayer(self):
        return (self.__livingareaLayer)

    @livingareaLayer.setter
    def livingareaLayer(self, value):
        self.__livingareaLayer = value

    @property
    def livingareaIDField(self):
        return (self.__livinglyrID)

    @livingareaIDField.setter
    def livingareaIDField(self, value):
        self.__livinglyrID = value

    @property
    def nodelayer(self):
        return (self.__nodelayer)

    @nodelayer.setter
    def nodelayer(self, value):
        self.setProgressSubMsg("nodelayer setter :{}".format(type(value)))
        self.__nodelayer = value

    @property
    def nodeIDfield(self):
        return (self.__nodeID)

    @nodeIDfield.setter
    def nodeIDfield(self, value):
        self.__nodeID = value

    @property
    def linklayer(self):
        return (self.__linklayer)

    @linklayer.setter
    def linklayer(self, value):
        self.__linklayer = value

    @property
    def linkTonodefield(self):
        return (self.__toNodefield)

    @linkTonodefield.setter
    def linkTonodefield(self, value):
        self.__toNodefield = value

    @property
    def linkFromnodefield(self):
        return (self.__fromNodefield)

    @linkFromnodefield.setter
    def linkFromnodefield(self, value):
        self.__fromNodefield = value

    @property
    def linklengthfield(self):
        return (self.__linklenfield)

    @linklengthfield.setter
    def linklengthfield(self, value):
        self.__linklenfield = value

    @property
    def linkSpeed(self):
        return (self.__linkSpeed)

    @linkSpeed.setter
    def linkSpeed(self, value):
        self.__linkSpeed = value

    def setProgressSubMsg(self, msg):
        import datetime
        # using now() to get current time
        now = datetime.datetime.now()

        # snow = "%04d-%02d-%02d %02d:%02d:%02d:%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
        snow = "%04d-%02d-%02d %02d:%02d:%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        # self.feedback.pushInfo("%s..........  %s" % (snow, msg))
        self.feedback.pushDebugInfo("%s..........  %s" % (snow, msg))
        # self.feedback.pushConsoleInfo(msg)

    def initNXGraph(self, isoneway=True):
        if isoneway:
            self.nxGraph = nx.DiGraph()
        else:
            self.nxGraph = nx.Graph()

    # processing funtions
    def rectanglesovalsdiamonds(self, input, onlyselected=False, shape=0, width=1.0, height=1.0, rotation=None,
                                segment=36, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.rectanglesovalsdiamonds(input=input, onlyselected=onlyselected, shape=shape, width=width,
                                                     height=height, rotation=rotation, segment=segment, output=output)

    def writeAsVectorLayer(self, layername):
        return self.qgsutils.writeAsVectorLayer(layername=layername)

    def bufferwithQgis(self, input, onlyselected, distance, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.bufferwithQgis(input=input, onlyselected=onlyselected, distance=distance, output=output)

    def createGridfromLayer(self, sourcelayer, gridsize, type=0, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.createGridfromLayer(sourcelayer=sourcelayer, gridsize=gridsize, type=type, output=output)

    def clipwithQgis(self, input, onlyselected, overlay, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.clipwithQgis(input=input, onlyselected=onlyselected, overlay=overlay, output=output)

    def dissolvewithQgis(self, input, onlyselected, field=None, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.dissolvewithQgis(input=input, onlyselected=onlyselected, field=field, output=output)

    def dissolvewithQgis2(self, input, onlyselected, field=None, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.dissolvewithQgis2(input=input, onlyselected=onlyselected, field=field, output=output)

    def nearesthubpoints(self, input, onlyselected, sf_hub, hubfield, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.nearesthubpoints(input=input, onlyselected=onlyselected, sf_hub=sf_hub, hubfield=hubfield,
                                              output=output)

    def nearesthubpoints2(self, input, onlyselected, sf_hub, hubfield, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.nearesthubpoints2(input=input, onlyselected=onlyselected, sf_hub=sf_hub, hubfield=hubfield,
                                              output=output)

    def createspatialindex(self, input):
        return self.qgsutils.createspatialindex(input=input)

    def countpointsinpolygon(self, polylayer, pointslayer, field, weight=None, classfield=None,
                             output='TEMPORARY_OUTPUT'):
        return self.qgsutils.countpointsinpolygon(polygons=polylayer,
                                                  points=pointslayer,
                                                  field=field,
                                                  weight=weight,
                                                  classfield=classfield,
                                                  output=output)

    def joinattributesbylocation(self, input, join, joinfiels=[], prefix='', discardnomatching=False,
                                 output='TEMPORARY_OUTPUT'):
        return self.qgsutils.joinattributesbylocation(input=input, join=join, joinfiels=joinfiels, prefix=prefix,
                                                      discardnomatching=discardnomatching, output=output)

    def intersection(self, input, inputfields, inputonlyseleceted, overlay, overayprefix, overlayer_fields=None,
                     output='TEMPORARY_OUTPUT'):
        return self.qgsutils.intersection(input=input,
                                          inputfields=inputfields,
                                          inputonlyseleceted=inputonlyseleceted,
                                          overlay=overlay,
                                          overayprefix=overayprefix,
                                          overlayer_fields=overlayer_fields,
                                          output=output)

    def centroidlayer(self, input, allparts=False, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.centroidlayer(input=input, onlyselected=False, allparts=allparts, output=output)

    def vectorlayer2ShapeFile(self, vectorlayer, output):
        return self.qgsutils.vectorlayer2ShapeFile(vectorlayer=vectorlayer, output=output,
                                                   destCRS=vectorlayer.sourceCrs())

    def differencelayer(self, input, onlyselected, overlayer, overonlyselected, output):
        return self.qgsutils.differencelayer(input=input, onlyselected=onlyselected,
                                             overlay=overlayer, overonlyselected=overonlyselected,
                                             output=output)

    def selectbylocation(self, input, intersect, method=0, predicate=0, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.selectbylocation(input=input,
                                              intersect=intersect,
                                              predicate=predicate,
                                              method=method,
                                              output=output)

    def addIDField(self, input, idfid, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.fieldCalculate(input=input,
                                            fid=idfid,
                                            ftype=0,
                                            flen=10,
                                            fprecision=0,
                                            formula='$id',
                                            newfield=True,
                                            output=output)

    def deleteFields(self, input, onlyselected=False, requredfields=[], output=None):
        inputsrc = None
        if isinstance(input, str):
            inputsrc = self.writeAsVectorLayer(input)
        else:
            inputsrc = input

        notDelete = list(map(lambda x: x.upper(), requredfields))

        fields = inputsrc.dataProvider().fields()
        remappings = []

        for idx in range(fields.count()):
            name = fields.field(idx).name()
            length = fields.field(idx).length()
            precision = fields.field(idx).precision()
            ftype = fields.field(idx).type()
            remap = {}
            if name.upper() in notDelete:
                remap['expression'] = name
                remap['name'] = name
                remap['type'] = ftype
                remap['length'] = length
                remap['precision'] = precision
                remappings.append(remap)

        return self.qgsutils.refactorfields(input=input, onlyselected=onlyselected, refieldmapping=remappings,
                                            output=output)

    # 해당 함수는 input과 output에 따라 오류 테스트가 더 필요함(그래서 현재 deleteFields를 사용함)
    def deleteFields2(self, input, requredfields=[], output=None):
        # copy
        # inputsrc = QgsVectorLayer(input.source(), input.name(), input.providerType())
        inputsrc = input

        fields = inputsrc.dataProvider().fields()

        notDelete = list(map(lambda x: x.upper(), requredfields))
        if self.debugging: self.setProgressSubMsg(str(notDelete))

        toDelete = []
        for idx in range(fields.count()):
            name = fields.field(idx).name()
            if not name.upper() in notDelete:
                toDelete.append(idx)

        completedlayer = None
        if len(toDelete) > 0:
            editstatus = inputsrc.startEditing()
            bsuccess = inputsrc.dataProvider().deleteAttributes(toDelete)
            if bsuccess:
                inputsrc.updateFields()
                inputsrc.commitChanges()

                completedlayer = self.vectoclayer2output(input=inputsrc, output=output)
            else:
                self.setProgressSubMsg(">> 필드 삭제 실패")
                inputsrc.rollback()
        else:
            completedlayer = inputsrc

        return completedlayer

    def multiparttosingleparts(self, input, onlyselected=False, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.multiparttosingleparts(input=input, onlyselected=onlyselected, output=output)


    def createNodeEdgeInGraph(self):

        fnodes = []
        tnodes = []
        weights = []

        tempNodes = []
        totalcnt = self.__linklayer.featureCount()
        i = 0
        if self.debugging: self.setProgressSubMsg("speed mode : {}, count of link :{}".format(str(self.__linkSpeed is not None), str(totalcnt)))

        # to get minimum speed beside zero
        tmplayer = self.__linklayer
        tmplayer = self.qgsutils.selectbyexpression2(input=tmplayer, expression='%s > 0' % self.__linkSpeed)
        tmplayer = self.qgsutils.saveselectedfeatrues(input=tmplayer)
        if self.debugging: self.setProgressSubMsg("not zero feature(link) : {}".format(tmplayer.featureCount()))
        idx = tmplayer.fields().indexFromName(self.__linkSpeed)
        minimumSpeed = tmplayer.minimumValue(idx)
        if self.debugging: self.setProgressSubMsg("minimumValue speed : {}".format(str(minimumSpeed)))

        for feature in self.__linklayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            tempNodes.append(feature.attribute(self.__fromNodefield))
            tempNodes.append(feature.attribute(self.__toNodefield))

            fnodes.append(feature.attribute(self.__fromNodefield))
            tnodes.append(feature.attribute(self.__toNodefield))

            length = feature.attribute(self.__linklenfield)

            if self.__linkSpeed is None:
                weights.append(length)
            else:
                speed = feature.attribute(self.__linkSpeed)
                if int(speed) == 0:
                    if self.debugging: self.setProgressSubMsg(
                        "링크레이어의 속도 필드에 0값이 있습니다. 최저속도인 %s으로 대체하여 계산합니다." % str(minimumSpeed))
                    speed = minimumSpeed
                # self.setProgressSubMsg("speed ={}, len")
                linktime = length/1000 / speed
                weights.append(linktime)

        allnodes = list(set(tempNodes))
        # if self.debugging: self.setProgressSubMsg("link list : {}".format(str(weights)))

        tmplink = tuple(zip(fnodes, tnodes, weights))
        self.nxGraph.add_nodes_from(allnodes)
        self.nxGraph.add_weighted_edges_from(tmplink)

        return self.nxGraph

    def selpopinsvrareaEuclidean(self, input, applyArea):
        return self.selectbylocation(input=input, intersect=applyArea)

    def selpopinsvrareaNetwork(self, input):

        return None

    # 선택된 인구만(서비스 중인 시설) 배제율 적용
    def calpopexclusratio(self, poplyr, popratiofield, popfield, exlusrate, output=None):

        editstatus = poplyr.startEditing()
        if self.debugging: self.setProgressSubMsg("editmode : %s" % str(editstatus))

        selection = poplyr.selectedFeatures()

        totalcnt = len(selection)
        if self.debugging: self.setProgressSubMsg("선택피처 : %s" % str(totalcnt))

        i = 0
        for feature in selection:
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            # 선택객체 : pop_ratio = ratio 변경
            feature[popratiofield] = exlusrate
            poplyr.updateFeature(feature)

        editstatus = poplyr.commitChanges()
        if self.debugging: self.setProgressSubMsg("commit : %s" % str(editstatus))

        # poprate = (100 - popexlusrate) / 100
        # popfield = popfield * pop_ratio 변경
        if self.debugging:
            tmp = self.qgsutils.fieldCalculate(input=poplyr,
                                               fid="ORG_POP",
                                               ftype=1,
                                               flen=10,
                                               fprecision=4,
                                               formula='\"{}\"'.format(popfield),
                                               newfield=True)

        applyedpoplyr = self.qgsutils.fieldCalculate(input=poplyr,
                                                     fid=popfield,
                                                     ftype=0,
                                                     flen=10,
                                                     fprecision=4,
                                                     formula='(100 - \"{}\") / 100 * \"{}\"'.format(popratiofield,
                                                                                                    popfield),
                                                     newfield=False)

        if output is None:
            if self.debugging: self.setProgressSubMsg("output is none")
            resultlayer = applyedpoplyr
        else:
            if self.debugging: self.setProgressSubMsg("output is not none")
            resultlayer = self.vectoclayer2output(input=applyedpoplyr, output=output)

        return resultlayer

    def applypopratioinselectedNetwork(self, input, popfield, exlusrate, output=None):

        dfpopremovedSOC = self.__dfPop
        # pop_ratio 필드 추가, pop_ratio 값을 전부 1로 변경
        popratiofield = 'exlusrate'
        tmppoplayer = self.qgsutils.fieldCalculate(input=self.__populationLayer,
                                                   fid=popratiofield,
                                                   ftype=1,
                                                   flen=10,
                                                   fprecision=4,
                                                   formula='0',
                                                   newfield=True)

        tmppoplayer.removeSelection()

        totalcnt = tmppoplayer.featureCount()
        i = 0
        for feature in tmppoplayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            popID = feature[self.__poplyrID]

            isSvredCurSOC = dfpopremovedSOC['CUR_ISSVRED'].loc[dfpopremovedSOC[self.__poplyrID] == popID].values[0]

            if str(isSvredCurSOC) == '1':
                expression = "\"%s\"=%s" % (self.__poplyrID, str(popID))
                # if self.debugging: self.setProgressSubMsg("expression : %s" % expression)
                tmppoplayer.selectByExpression2(expression, QgsVectorLayer.AddToSelection)

        if self.debugging: self.setProgressSubMsg("선택된 객체 : %s " % str(len(list(tmppoplayer.getSelectedFeatures()))))

        return self.calpopexclusratio(poplyr=tmppoplayer, popratiofield=popratiofield, popfield=popfield,
                                      exlusrate=exlusrate, output=output)

        #
        #
        #
        #
        #
        #
        # # pop_ratio 필드 추가, pop_ratio 값을 전부 1로 변경
        # popratiofield = 'exlusrate'
        # poplyr = self.qgsutils.fieldCalculate(input=input,
        #                                       fid=popratiofield,
        #                                       ftype=1,
        #                                       flen=10,
        #                                       fprecision=4,
        #                                       formula='0',
        #                                       newfield=True)
        #
        # dfpopremovedSOC = self.__dfPop
        #
        # totalcnt = poplyr.featureCount()
        # i = 0
        # for feature in poplyr.getFeatures():
        #     i += 1
        #     if self.feedback.isCanceled(): return None
        #     self.feedback.setProgress(int(i / totalcnt * 100))
        #
        #     popID = feature[self.__poplyrID]
        #
        #     isSvredCurSOC = dfpopremovedSOC['CUR_ISSVRED'].loc[dfpopremovedSOC[self.__poplyrID] == popID].values[0]
        #
        #     if str(isSvredCurSOC) == '1':
        #         expression = "\"%s\"=%s" % (self.__poplyrID, str(popID))
        #         # if self.debugging: self.setProgressSubMsg("expression : %s" % expression)
        #         poplyr.selectByExpression(expression, QgsVectorLayer.AddToSelection)
        #
        # if self.debugging: self.setProgressSubMsg("선택된 객체 : %s " % str(len(list(poplyr.getSelectedFeatures()))))

        # return self.calpopexclusratio(poplyr=poplyr, popratiofield=popratiofield, popfield=popfield,
        #                               exlusrate=exlusrate, output=output)

    def applypopratioinselectedEuclidean(self, input, popfield, exlusrate, applyArea, output=None):

        # pop_ratio 필드 추가, pop_ratio 값을 전부 1로 변경
        popratiofield = 'exlusrate'
        poplyr = self.qgsutils.fieldCalculate(input=input,
                                              fid=popratiofield,
                                              ftype=1,
                                              flen=10,
                                              fprecision=4,
                                              formula='0',
                                              newfield=True)

        # # selbyloc : applyArea
        self.createspatialindex(poplyr)
        poplyr2 = self.selectbylocation(input=poplyr, intersect=applyArea)
        return self.calpopexclusratio(poplyr=poplyr2, popratiofield=popratiofield, popfield=popfield,
                                      exlusrate=exlusrate, output=output)


    def make_networksumScore(self, output=None):

        finanallayer = self.qgsutils.addField(input=self.__sourcelayer,
                                              fid="NX_SCORE",
                                              ftype=0,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=10,
                                              fprecision=8)

        dfScore = self.__dtFinalwithsScore


        i = 0
        finanallayer.startEditing()
        cnt = finanallayer.featureCount()
        for feature in finanallayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / cnt * 100))

            feanodeid = feature[self.__nodeID]

            try:
                score = self.__networkSum['NX_WEIGHT'].loc[self.__networkSum[self.__nodeID] == feanodeid]
                feature["NX_SCORE"] = float(score)
            except:
                self.setProgressSubMsg('NODE : {}, NX_SCORE : {}'.format(feanodeid, score))

            finanallayer.updateFeature(feature)

        finanallayer.commitChanges()


        # # 불필요한 필드 제거
        if not self.debugging:
            reqfiels = self.__sourcelayer.fields().names()

            try: reqfiels.remove(self.__nodeID)
            except: pass
            try: reqfiels.remove('HubDist')
            except: pass

            reqfiels.append("NX_SCORE")
            finanallayer = self.deleteFields(input=finanallayer, requredfields=reqfiels)

        if output is None:
            resultlayer = finanallayer
        else:
            resultlayer = self.vectoclayer2output(input=finanallayer, output=output)

        return resultlayer


    def anal_NetworkSum(self):

        sourceNodefid = self.__nodeID
        sourceNodeDistfid = 'HubDist'
        targetNodefid = self.__nodeID
        targetNodeDistfid = 'HubDist'

        listsourceNodeID = []
        listShortestSum = []

        sourcelayer = self.__sourcelayer
        targetNodelist = [feature.attribute(targetNodefid) for feature in self.__targetlayer.getFeatures()]
        targetNodeDist = [feature.attribute(targetNodeDistfid) for feature in self.__targetlayer.getFeatures()]

        if self.debugging: self.setProgressSubMsg(targetNodeDist)

        targetNodedistSum = 0
        nodeDistSum = 0
        try:
            targetNodedistSum = sum(targetNodeDist)
        except:
            if len(targetNodeDist) > 0: self.setProgressSubMsg("인근 노드까지의 거리를 구할 수 없어, 분석 지점에서 최근린 노드까지의 직선거리를 무시합니다\n(QGIS 프로젝트 좌표계 설정을 확인하세요)")

        i = 0
        totalcnt = sourcelayer.featureCount()
        for feature in sourcelayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            sourceNodeId = feature[sourceNodefid]
            sourceNodeDist = feature[sourceNodeDistfid]

            if sourceNodeDist != None and targetNodedistSum != None: nodeDistSum = sourceNodeDist + targetNodedistSum

            # 최단거리 분석
            shortest = nx.single_source_dijkstra_path_length(self.nxGraph, sourceNodeId, weight='weight')
            targetshortest = {idx: val for idx, val in shortest.items() if (idx in targetNodelist)}
            shortestDistsum = sum(targetshortest.values())

            listsourceNodeID.append(sourceNodeId)
            listShortestSum.append(shortestDistsum+nodeDistSum)

        rawData = {sourceNodefid: listsourceNodeID,
                   "NX_WEIGHT": listShortestSum}


        self.__networkSum = pd.DataFrame(rawData)

        if self.debugging:
            tempexcel = os.path.join(self.workpath, 'source_network.csv')
            self.__networkSum.to_csv(tempexcel)

        return self.__networkSum




    # Calculate the shortest distance and store the result in memory
    # 디버깅 모드시 : 대용량 파일 저장시 속도 저하 유의
    def shortestAllnodes(self, algorithm='dijkstra', output_alllink=None):
        self.feedback.setProgress(0)
        allNodes = None

        # if output_alllink is not None:

        if self.__cutoff == 0:
            cutoff = None
        else:
            cutoff = self.__cutoff

        if self.debugging: self.setProgressSubMsg("[start] shortestAllnodes")

        # if False:
        if self.debugging and output_alllink is not None and os.path.exists(output_alllink):
            with open(output_alllink, 'rb') as handle:
                allNodes = pickle.load(handle)
        else:
            if algorithm.lower() == 'johnson':
                allNodes = dict(nx.johnson(self.nxGraph, weight='weight'))
            elif algorithm.lower() == 'dijkstra':
                allNodes = dict(nx.all_pairs_dijkstra_path_length(self.nxGraph, weight='weight', cutoff=cutoff))
            elif algorithm.lower() == 'bellman':
                allNodes = dict(nx.all_pairs_bellman_ford_path_length(self.nxGraph, weight='weight'))

            # if False:
            if self.debugging and output_alllink is not None:
                with open(output_alllink, 'wb') as handle:
                    pickle.dump(allNodes, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if self.debugging: self.setProgressSubMsg("[END] shortestAllnodes")

        self.allshortestnodes = allNodes
        self.feedback.setProgress(100)
        return allNodes

    def get_Distance(self, fromNodeID, toNodeID):
        dis = None
        try:
            pairNode = self.allshortestnodes[fromNodeID]
            dis = pairNode[toNodeID]

            if (self.__cutoff is not None) and (self.__cutoff > 0) and (dis > self.__cutoff):
                dis = None
        except:
            dis = None

        return dis

    def get_alltargetSumofDistance(self, fromNodeID, svrNodeList):
        dis = None
        dict_distlist = self.get_allOfDistFromAlltarget(fromNodeID, svrNodeList)
        if len(dict_distlist) > 0: dis = sum(dict_distlist.values())
        return dis

    def get_nearesttargetDistnace(self, fromNodeID, svrNodeList):

        dis = None

        dict_distlist = self.get_allOfDistFromAlltarget(fromNodeID, svrNodeList)

        # if self.debugging:
        #     if dict_distlist is None
        #         self.setProgressSubMsg("    >> get_nearesttargetDistnace [NODE-%s] 해당 노드 %sm 이내에는 현재 생활SOC가 없습니다." % (str(fromNodeID), str(self.cutoff)))

        if dict_distlist is not None:
            import operator
            sorteddict = sorted(dict_distlist.items(), key=operator.itemgetter(1))

            if len(sorteddict) > 0:
                if fromNodeID in svrNodeList:
                    # fromNode위치와 svrNode의 위치가 동일한 경우
                    dis = sorteddict[0][1]

                else:
                    if len(sorteddict) == 1:
                        # fromNode위치와 svrNode의 위치가 동일하지 않은 경우는 0번째는 자신 Node까지의 거리를 뜻함
                        dis = sorteddict[0][1]

                    else:
                        dis = sorteddict[1][1]

        return dis

    def get_allOfDistFromAlltarget(self, fromNodeID, alltargetNodeList):

        new_dict = {}
        try:
            pairNode = self.allshortestnodes[fromNodeID]
            if self.__cutoff == 0 or self.__cutoff is None:
                new_dict = {idx: val for idx, val in pairNode.items() if (idx in alltargetNodeList)}
            else:
                # new_dict = {idx: val for idx, val in pairNode.items() if (idx in alltargetNodeList) and (val <= self.__cutoff)}
                new_dict = {idx: self.__outofcutoff if val > self.__cutoff else val for idx, val in pairNode.items() if
                            (idx in alltargetNodeList)}

        except:
            if self.debugging: self.setProgressSubMsg("[get_AllDistanceFromNode] 노드 찾기 오류(디버깅용메시지) : %s" % fromNodeID)
            new_dict = None

        return new_dict

    # 사용 : 형평성(직선)
    def getPopdistmatrixDataLayer(self, targetlayer, targetlayerID, output):

        # 1) 싱글파트로 변경
        singlepop = self.__popSinglepartlayer
        singleTarget = targetlayer

        # # MultiPoint : 4
        if singlepop is None: singlepop = self.qgsutils.multiparttosingleparts(self.__populationLayer, False)
        if singleTarget.wkbType() == 4: singleTarget = self.qgsutils.multiparttosingleparts(targetlayer, False)

        # 잠재지역 분석시 활용하기 위해 저장
        self.__popSinglepartlayer = singlepop

        # 2) 거리 행렬 연산
        matrixtype = 2
        if (self.__cutoff is not None) and (self.__cutoff > 0): matrixtype = 0

        tmpoutput = os.path.join(self.workpath, 'popdistmatrix1_%s.gpkg' % targetlayer.sourceName())
        if self.debugging:
            self.setProgressSubMsg("distancematrix(인구-SOC(기존 or 신규) : {}".format(tmpoutput))
        matrix_distance = self.qgsutils.distancematrix(input=singlepop,
                                                       inputonlyselected=False,
                                                       inputfield=self.popIDField,
                                                       target=singleTarget,
                                                       targetonlyseleted=False,
                                                       targetfield=targetlayerID,
                                                       matrixtype=matrixtype,
                                                       output=tmpoutput)

        resultlayer = matrix_distance

        # 3) 거리 조락 반영
        if (self.__cutoff is not None) and (self.__cutoff > 0):
            selecedlyr = self.qgsutils.selectbyexpression2(input=matrix_distance,
                                                          expression='Distance <= %s' % (str(self.__cutoff)))

            resultlayer = self.qgsutils.saveselectedfeatrues(selecedlyr, output)

        return resultlayer

    def anal_AllCurSOC_straight(self):

        if self.debugging:
            self.setProgressSubMsg("===기존 시설 분석 시작===")
            self.setProgressSubMsg("기존 SOC 레이어 갯수 : {}".format(str(self.__currentSOClayer.featureCount())))

        tmpoutput = os.path.join(self.workpath, 'AllCurSOC1.gpkg')
        if self.debugging:
            self.setProgressSubMsg("Distancematrix(인구-기존) : {}".format(tmpoutput))
        # [향후-인구배제율] 추가1) 거리조락 밖에 있는 것도 반환하도록 수정(getPopdistmatrixDataLayer 함수 내)
        matrixDisLayer = self.getPopdistmatrixDataLayer(targetlayer=self.__currentSOClayer,
                                                        targetlayerID=self.__currentSOCID,
                                                        output=tmpoutput)

        # [향후-인구배제율] 추가2) maxrixAllDisLayer = 매트릭스 결과와 인구 조인(인구-시설매트릭스+인구수)
        #
        #
        #
        # [향후-인구배제율] 추가3) maxrixAllDisLayer를 이용하여, statisticsbycategories 대신 loop 돌면서 처리하도록 변경
        #
        #
        #
        tmpoutput = os.path.join(self.workpath, 'AllCurSOC2')
        if self.debugging:
            self.setProgressSubMsg("통계(AllCurSOC1.Distance) : {}".format(tmpoutput))
        statstable = self.qgsutils.statisticsbycategories(input=matrixDisLayer,
                                                          onlyselected=False,
                                                          categoriesfields=['InputID'],
                                                          valuefield='Distance',
                                                          output=tmpoutput)

        if self.debugging:
            self.setProgressSubMsg(len(matrixDisLayer))
            self.setProgressSubMsg(len(self.__popSinglepartlayer))
            self.setProgressSubMsg(len(statstable))

        tmpoutput = os.path.join(self.workpath, 'AllCurSOC3.gpkg')
        if (self.debugging):
            self.setProgressSubMsg("조인(인구-통계) : {}".format(tmpoutput))
        joinedpop = self.qgsutils.joinattributetable(input1=self.__popSinglepartlayer,
                                                     input1onlyselected=False,
                                                     field1=self.popIDField,
                                                     input2=statstable,
                                                     input2onlyselected=False,
                                                     field2='InputID',
                                                     prefix='M_',
                                                     output=tmpoutput
                                                     )

        self.setProgressSubMsg(type(joinedpop))
        if isinstance(joinedpop, str): joinedpop = self.qgsutils.writeAsVectorLayer(joinedpop)
        self.setProgressSubMsg(type(joinedpop))

        listPopID = []
        listPopCnt = []
        listPoptoSocDis = []

        singleTarget = self.__popSinglepartlayer
        targetcnt = singleTarget.featureCount()
        totalcnt = joinedpop.featureCount()
        i = 0

        for feature in joinedpop.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            listPopID.append(feature[self.popIDField])
            listPopCnt.append(feature[self.__popcntField])

            accval = 0
            if (self.__cutoff is not None) and (self.__cutoff > 0):
                accval = feature['M_SUM']
            else:
                accval = feature['M_MEAN'] * targetcnt

            # if str(accval).isnumeric() == False:
            if accval is None or str(accval) is None or str(accval) == 'NULL':
                accval = 0

            listPoptoSocDis.append(accval)

        rawData = {self.__poplyrID: listPopID,
                   self.__popcntField: listPopCnt,
                   'ACC_SCORE': listPoptoSocDis}

        dfPopwidthDis = pd.DataFrame(rawData)

        dfPopwidthDis['ACC_SCORE'].fillna(0, inplace=True)
        # dfPopwidthDis.loc[dfPopwidthDis['ACC_SCORE'] == 'NULL', 'ACC_SCORE'] = 0

        dfPopwidthDis.to_csv(os.path.join(self.workpath, 'matrix4_AllCurSOC.csv'))

        self.__dfPop = dfPopwidthDis

        return self.__dfPop

    # [향후-인구배제율] 추가) 구배제률 계산하여 적용
    #
    #
    #
    def anal_AllCurSOC_network(self):
        dists = []
        i = 0

        svrNodeilst = [feature.attribute(self.__nodeID) for feature in self.__currentSOClayer.getFeatures()]
        if self.debugging: self.setProgressSubMsg("svrNodeilst : %s" % str(svrNodeilst))

        listpopNode = []
        listpopCnt = []
        listpopAccscore = []
        calculatedNode = {}

        tmppoplayer = self.__populationLayer
        totalcnt = tmppoplayer.featureCount()
        notfounddatacnt = 0

        if self.debugging: self.setProgressSubMsg("tmppoplayer count : {}".format(totalcnt))

        for feature in tmppoplayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            popNodeid = str(feature[self.__nodeID])
            poppnt = feature[self.__popcntField]

            try:
                dis = calculatedNode[popNodeid]
            except:
                dis = self.get_alltargetSumofDistance(fromNodeID=popNodeid,
                                                      svrNodeList=svrNodeilst)
                if dis is None:
                    # newdis를 찾지 못할 경우 최대값을 할당함(형평성은 모든 시설까지의 거리를 기반으로 하므로 len(svrNodeilst)를 곱해줌)
                    dis = self.__outofcutoff * len(svrNodeilst)

                    if self.debugging:
                        self.setProgressSubMsg(
                            "[NODE-%s] 해당 인구데이터의 %sm 이내에는 현재 생활SOC가 없습니다." % (str(popNodeid), str(self.cutoff)))
                    notfounddatacnt += 1

                calculatedNode[popNodeid] = dis

            listpopCnt.append(poppnt)

            listpopNode.append(popNodeid)
            listpopAccscore.append(dis)

        rawData = {self.nodeIDfield: listpopNode,
                   self.__popcntField: listpopCnt,
                   'ACC_SCORE': listpopAccscore}

        self.__dfPop = pd.DataFrame(rawData)

        if self.debugging:
            self.setProgressSubMsg("총 %s의 인구 데이터 중에 %s개의 인구데이터는 %sm 이내의 인근 생활 SOC를 찾지 못했습니다."
                                   % (str(totalcnt), str(notfounddatacnt), str(self.cutoff))
                                   )
        self.__dfPop.to_csv(os.path.join(self.workpath, 'analyze_fromAllCurSOC.csv'))

        return self.__dfPop

    def anal_AllPotenSOC_straight(self):

        # 1) 잠재적위치 레이어와 세생활권 인구레이어 distance matrix
        tmpoutput = os.path.join(self.workpath, 'AllPotenSOC1.gpkg')
        matrixDisLayer = self.getPopdistmatrixDataLayer(targetlayer=self.__potentiallayer,
                                                        targetlayerID=self.__potentialID,
                                                        output=tmpoutput)
        # [향후-인구배제율] 추가) 인구배제률 계산하여 적용
        #
        #
        #
        if isinstance(matrixDisLayer, str): matrixDisLayer = self.qgsutils.writeAsVectorLayer(matrixDisLayer)

        # 2) 거리 2차 dict 생성
        totalcnt = matrixDisLayer.featureCount()
        pot2popDists = {}
        i = 0
        # self.setProgressSubMsg(str(totalcnt))
        for feature in matrixDisLayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            potenID = int(feature['TargetID'])
            popID = int(feature['InputID'])
            if feature['Distance'] is None:
                distance = 0
            else:
                distance = int(feature['Distance'])

            try:
                toPopDists = pot2popDists[potenID]
                # 이미 있을 경우 현재값으로 변경한다..(실제로는 이런 경우 없음)
                toPopDists[popID] = distance
            except:
                toPopDists = {}
                toPopDists[popID] = distance
                pot2popDists[popID] = toPopDists

        try:
            tmppotenlayer = self.__potentiallayer
            potencnt = tmppotenlayer.featureCount()
            potenIDList = []
            potenEquityScore = []
            dictResultwithsScore = {}

            i = 0
            calculatedNode = {}
            tmpPopCopy = self.__dfPop.copy()

            for feature in tmppotenlayer.getFeatures():
                i += 1
                if self.feedback.isCanceled(): return None
                self.feedback.setProgress(int(i / potencnt * 100))

                ############# 이부분 다름 ##############################
                potenID = feature[self.__potentialID]
                potenIDList.append(potenID)
                ####################################################

                tmpPopCopy['NEW_DIS'] = 0
                try:
                    popDistances = pot2popDists[potenID]

                    for key, value in popDistances.items():
                        tmpPopCopy.loc[tmpPopCopy[self.__poplyrID] == key, "NEW_DIS"] = value

                except:
                    tmpPopCopy['NEW_DIS'] = 0

                dfsumOfacc = tmpPopCopy['ACC_SCORE'] + tmpPopCopy['NEW_DIS']

                tmpPopCopy['A'] = tmpPopCopy[self.__popcntField] * dfsumOfacc
                avg = tmpPopCopy['A'].mean()
                # tmpPopCopy['EQ_SCORE'] = np.sqrt((tmpPopCopy['A'] - avg) ** 2)
                tmpPopCopy['EQ_SCORE'] = ((tmpPopCopy['A'] - avg) ** 2) ** (1 / 2)

                sumofeqscore = tmpPopCopy['EQ_SCORE'].sum()
                potenEquityScore.append(int(sumofeqscore))
                dictResultwithsScore[potenID] = int(sumofeqscore)

            rawData = {self.__potentialID: potenIDList,
                       'EQ_SCORE': potenEquityScore}

            self.__dtFinalwithsScore = pd.DataFrame(rawData)
            self.__dictFinalwithScore = dictResultwithsScore

            return self.__dtFinalwithsScore

        except MemoryError as error:
            self.setProgressSubMsg(type(error))

    def anal_accessibilityCurSOC_straight(self):

        tmppoplayer = self.__populationLayer

        listpopID = []
        listpopCnt = []
        listlivingID = []
        listpopAccscore = []

        for feature in tmppoplayer.getFeatures():
            poplivingID = feature[self.__livinglyrID]
            popID = feature[self.__poplyrID]
            poppnt = feature[self.__popcntField]
            dis = feature['HubDist']

            if self.__cutoff > 0 and dis >= self.__cutoff:
                dis = self.__outofcutoff
                # dis = 0

            listlivingID.append(poplivingID)
            listpopID.append(popID)
            listpopCnt.append(poppnt)
            listpopAccscore.append(dis)

        rawData = {self.__poplyrID: listpopID,
                   self.__popcntField: listpopCnt,
                   self.__livinglyrID: listlivingID,
                   'DISTANCE': listpopAccscore}

        self.__dfPop = pd.DataFrame(rawData)

        return self.__dfPop

    def anal_accessibilityCurSOC_network(self):

        svrNodeilst = [feature.attribute(self.__nodeID) for feature in self.__currentSOClayer.getFeatures()]
        tmppoplayer = self.__populationLayer
        totalcnt = tmppoplayer.featureCount()

        listlivingID = []
        listpopID = []
        listpopNode = []
        listpopCnt = []
        listpopAccscore = []
        calculatedNode = {}

        i = 0
        # errcnt = 0
        # noerrcnt = 0
        for feature in tmppoplayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            poplivingID = feature[self.__livinglyrID]
            popID = feature[self.__poplyrID]
            popNodeid = feature[self.__nodeID]
            poppnt = feature[self.__popcntField]

            try:
                dis = calculatedNode[popNodeid]
            except:
                dis = self.get_nearesttargetDistnace(fromNodeID=popNodeid,
                                                     svrNodeList=svrNodeilst)
                if dis is None:
                    if self.debugging:
                        self.setProgressSubMsg(
                            "[NODE-%s] 해당 세생권데이터의 %sm 이내에는 현재 생활SOC가 없습니다." % (str(popNodeid), str(self.cutoff)))
                    dis = self.__outofcutoff

                calculatedNode[popNodeid] = dis

            listlivingID.append(poplivingID)
            listpopID.append(popID)
            listpopNode.append(popNodeid)
            listpopCnt.append(poppnt)
            listpopAccscore.append(dis)

        rawData = {self.__poplyrID: listpopID,
                   self.__nodeID: listpopNode,
                   self.__popcntField: listpopCnt,
                   self.__livinglyrID: listlivingID,
                   'DISTANCE': listpopAccscore}

        self.__dfPop = pd.DataFrame(rawData)

        tempexcel = os.path.join(self.workpath, 'anal_NeartestCurSOC_network.csv')
        self.__dfPop.to_csv(tempexcel)
        # except MemoryError as error:
        #     self.setProgressSubMsg(type(error))

        return self.__dfPop

    # [향후-인구배제율] 추가) 구배제률 계산하여 적용
    #
    #
    #
    def anal_AllPotenSOC_network(self):

        tmppotenlayer = self.__potentiallayer

        potencnt = tmppotenlayer.featureCount()
        potenNodeID = []
        potenEquityScore = []
        dictResultwithsScore = {}

        i = 0
        calculatedNode = {}
        for feature in tmppotenlayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / potencnt * 100))
            nodeid = feature[self.__nodeID]
            potenNodeID.append(nodeid)

            dists = []
            try:
                dists = calculatedNode[nodeid]
            except:
                for idx, row in self.__dfPop.iterrows():
                    if self.feedback.isCanceled(): return None
                    popNodeID = row[self.__nodeID]
                    newdis = self.get_Distance(fromNodeID=popNodeID,
                                               toNodeID=nodeid)

                    # newdis를 찾지 못할 경우 최대값을 할당함
                    if newdis is None: newdis = self.__outofcutoff

                    dists.append(newdis)
                    calculatedNode[nodeid] = dists

            self.__dfPop['NEW_DIS'] = pd.DataFrame({'NEW_DIS': dists})

            dfsumOfacc = self.__dfPop['ACC_SCORE'] + self.__dfPop['NEW_DIS']

            self.__dfPop['A'] = self.__dfPop[self.__popcntField] * dfsumOfacc
            avg = self.__dfPop['A'].mean()

            # self.__dfPop['EQ_SCORE'] = np.sqrt((self.__dfPop['A'] - avg) ** 2)
            self.__dfPop['EQ_SCORE'] = ((self.__dfPop['A'] - avg) ** 2) ** (1 / 2)

            sumofeqscore = self.__dfPop['EQ_SCORE'].sum()
            potenEquityScore.append(int(sumofeqscore))
            dictResultwithsScore[nodeid] = int(sumofeqscore)

        rawData = {self.nodeIDfield: potenNodeID,
                   'EQ_SCORE': potenEquityScore}

        self.__dtFinalwithsScore = pd.DataFrame(rawData)
        self.__dictFinalwithScore = dictResultwithsScore

        tempexcel = os.path.join(self.workpath, 'anal_AllPotenSOC_network.csv')
        self.__dtFinalwithsScore.to_csv(tempexcel)

        return self.__dtFinalwithsScore

    def make_Accessbillityscore(self, isNetwork=True, output=None):

        # ACC_SCORE : dataframe의 필드
        # scorefield : final layer의 필드
        scorefield = 'ACC_SCORE'

        dfPop = self.__dfPop
        dfPop[scorefield] = dfPop[self.__popcntField] * dfPop['DISTANCE']

        # 구 버전 문법
        # dfgroupy = dfPop.groupby([self.__livinglyrID])[self.__popcntField, 'DISTANCE', scorefield].agg({scorefield : {'ACC_SCORE_SUM': 'sum'},
        #                                                                                                  self.__popcntField: {'POP_SUM': 'sum'}
        #                                                                                                  }).reset_index()
        # 문법 변경
        # dfgroupy = dfPop.groupby([self.__livinglyrID])[self.__popcntField, 'DISTANCE', scorefield].agg(ACC_SCORE_SUM=(scorefield, 'sum'),
        #                                                                                                POP_SUM=("val", 'sum')).reset_index()

        dfgroupy = dfPop.groupby([self.__livinglyrID])[self.__popcntField, 'DISTANCE', scorefield].agg(
            ['sum']).reset_index()
        dfgroupy.columns = ["".join(x) for x in dfgroupy.columns.ravel()]
        dfgroupy.rename(columns={self.__popcntField + "sum": "POP_SUM", "DISTANCE" + "sum": "DISTANCE_SUM",
                                 scorefield + "sum": "ACC_SCORE_SUM"}, inplace=True)

        dfgroupy[scorefield] = dfgroupy['ACC_SCORE_SUM'] / dfgroupy['POP_SUM']

        finanallayer = self.qgsutils.addField(input=self.__livingareaLayer,
                                              fid='AC_GRADE',
                                              ftype=0,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=10,
                                              fprecision=8)

        # if self.debugging:
        finanallayer = self.qgsutils.addField(input=finanallayer,
                                              fid='AC_SCORE',
                                              ftype=1,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=20,
                                              fprecision=8)

        if isNetwork:
            finalKeyID = self.__livinglyrID
        else:
            finalKeyID = self.__livinglyrID

        # tmpdfPOP = self.__dfPop.astype({finalKeyID: str})
        tmpdfPOP = dfgroupy.astype({finalKeyID: str})

        tempexcel = os.path.join(self.workpath, 'tmpdfPOP.csv')
        if self.debugging: self.setProgressSubMsg(
            "인구 최종->그룹바이 세새활권 id.sum of(인구, 거리, 인구*거리)-> (인구*거리)/총인구 : \n{}\n\n".format(tempexcel))
        tmpdfPOP.to_csv(tempexcel)

        ###################### 등급 산정 부분 ######################
        # 접근성 분석은 1인당 인근의 가장 가까운 시설까지의 거리이므로 결과 값이 작을 수록 등급도 좋음

        step = 100 / self.__classify_count

        classRange = [cls * step for cls in range(0, self.__classify_count + 1)]
        clsfy = np.nanpercentile(tmpdfPOP[scorefield], classRange, interpolation='linear')
        # 값이 낮을 수록 좋은(낮은 숫자) 등급\

        clsfy[0] = tmpdfPOP[scorefield].min(skipna=True) - 1
        clsfy[len(clsfy) - 1] = tmpdfPOP[scorefield].max(skipna=True) + 1

        grade = 0
        gradeval = None
        prevalue = None

        if self.debugging: self.setProgressSubMsg("classify count : {}".format(len(clsfy)))
        if self.debugging: self.setProgressSubMsg("classify : {}".format(clsfy))

        for gradeval in clsfy:
            if prevalue is not None:
                if prevalue != gradeval:
                    # print('{} 등급 : {} < GRADE <= {}'.format(grade, prevalue, gradeval))
                    tmpdfPOP.loc[
                        (prevalue < tmpdfPOP[scorefield]) & (tmpdfPOP[scorefield] <= gradeval), "AC_GRADE"] = grade
                    if self.debugging:
                        self.setProgressSubMsg("{}등급 : {} < score <= {}".format(grade, prevalue, gradeval))

            prevalue = gradeval
            grade += 1

        # scorefield = 'ACC_SCORE'
        # step = 100 / self.__classify_count
        # # classRange = [cls * step for cls in reversed(range(0, self.__classify_count + 1))]
        # classRange = [cls * step for cls in (range(0, self.__classify_count + 1))]
        # clsfy = np.nanpercentile(tmpdfPOP[scorefield], classRange, interpolation='linear')
        #
        # # + vs - 지표에 따라 아래 내용이 약간 달라짐
        # clsfy[0] = tmpdfPOP[scorefield].min(skipna=True) - 1
        # clsfy[len(clsfy) - 1] = tmpdfPOP[scorefield].max(skipna=True) + 1
        #
        # # print(clsfy)
        #
        # grade = self.__classify_count + 1
        # gradeval = None
        # prevalue = None
        #
        # for gradeval in clsfy:
        #     if prevalue is not None:
        #         if prevalue != gradeval:
        #             # 접근성 분석은 +지표, 이부분 지표 성격에 따라 다름(+지표 or 0지표)
        #             # print('{} > {} >= {}'.format(prevalue, i, gradeval))
        #             tmpdfPOP.loc[(prevalue < tmpdfPOP[scorefield]) & (tmpdfPOP[scorefield] <= gradeval), 'AC_GRADE'] = grade
        #             if self.debugging:
        #                 self.setProgressSubMsg("{}등급 : {} < score <= {}".format(grade, prevalue, gradeval))
        #             # print('{} 등급 : {} < AC_GRADE <= {}'.format(grade, prevalue, gradeval))
        #     prevalue = gradeval
        #     grade -= 1

        #
        # clsfy[len(clsfy) - 1] = tmpdfPOP[scorefield].min(skipna=True) - 1
        # clsfy[0] = tmpdfPOP[scorefield].max(skipna=True) + 1
        #
        # if self.debugging: self.setProgressSubMsg("classify count : {}".format(len(clsfy)))
        #
        # grade = 0
        # prevalue = None
        # for gradeval in clsfy:
        #     if prevalue is not None:
        #         if prevalue != gradeval:
        #             # 접근성 분석은 +지표, 이부분 지표 성격에 따라 다름(+지표 or 0지표)
        #             # print('{} > {} >= {}'.format(prevalue, i, gradeval))
        #             tmpdfPOP.loc[(prevalue > tmpdfPOP[scorefield]) & (tmpdfPOP[scorefield] >= gradeval), 'AC_GRADE'] = grade
        #     prevalue = gradeval
        #     grade += 1
        ########################################################################################

        tempexcel = os.path.join(self.workpath, 'final_Accessbillityscore.csv')
        if self.debugging: self.setProgressSubMsg("등급 계산 : \n{}\n\n".format(tempexcel))
        tmpdfPOP.to_csv(tempexcel)

        potencnt = finanallayer.featureCount()
        editstatus = finanallayer.startEditing()
        if self.debugging: self.setProgressSubMsg("editmode : %s" % str(editstatus))
        i = 0
        for feature in finanallayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / potencnt * 100))

            finalkey = feature[finalKeyID]
            eqscore = None
            eqgrade = None

            if len(tmpdfPOP["ACC_SCORE"].loc[tmpdfPOP[finalKeyID] == str(finalkey)]) == 0:
                if self.debugging: self.setProgressSubMsg("세생활권에 속해 있는 인구 정보가 없습니다. [%s=%s]" % (finalKeyID, finalkey))
                # self.__logger.info("세생활권에 속해 있는 인구 정보가 없습니다. [%s=%s]" % (finalKeyID, finalkey))
            else:
                eqscore = tmpdfPOP["ACC_SCORE"].loc[tmpdfPOP[finalKeyID] == str(finalkey)].head(1)
                eqscore = float(eqscore)
                if float(eqscore) == 0.0: eqscore = 0.00000001
                # if float(eqscore) == 0.0: eqscore = 999999999

                eqgrade = tmpdfPOP["AC_GRADE"].loc[tmpdfPOP[finalKeyID] == str(finalkey)].head(1)
                eqgrade = int(eqgrade)

            # if self.debugging: self.setProgressSubMsg(str(eqscore))

            # if self.debugging:
            feature["AC_SCORE"] = eqscore
            feature["AC_GRADE"] = eqgrade

            finanallayer.updateFeature(feature)

        editstatus = finanallayer.commitChanges()
        if self.debugging: self.setProgressSubMsg("commit : %s" % str(editstatus))
        if self.debugging: self.setProgressSubMsg("세생활 ID에 해당하는 최종인구 데이터의 ACC_SCORE, AC_GRADE 세생활권 레이어에 필드가 추가됨(최종결과물)")

        # 불필요한 필드 제거
        if not self.debugging:
            reqfiels = [finalKeyID, 'AC_GRADE', 'AC_SCORE']
            # self.setProgressSubMsg("start finanallayer type is %s" % str(type(finanallayer)))
            finanallayer = self.deleteFields(input=finanallayer, requredfields=reqfiels)
            # self.setProgressSubMsg("end finanallayer type is %s" % str(type(finanallayer)))

        if output is None:
            if self.debugging: self.setProgressSubMsg("output is none")
            resultlayer = finanallayer
        else:
            if self.debugging: self.setProgressSubMsg("output is not none")
            # resultlayer = self.qgsutils.vectorlayer2ShapeFile(vectorlayer=finanallayer,
            #                                                   output=output,
            #                                                   destCRS=finanallayer.sourceCrs())
            resultlayer = self.vectoclayer2output(input=finanallayer, output=output)

        return resultlayer

    def vectoclayer2output(self, input, output):
        expression = "1 = 1"
        tmplayer = self.qgsutils.selectbyexpression2(input=input, expression=expression)
        return self.qgsutils.saveselectedfeatrues(input=tmplayer, output=output)

    def make_equityscore(self, isNetwork=True, output=None):

        finanallayer = self.qgsutils.addField(input=self.__potentiallayer,
                                              fid="EQ_GRADE",
                                              ftype=0,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=10,
                                              fprecision=8)
        # if self.debugging:
        finanallayer = self.qgsutils.addField(input=finanallayer,
                                              fid="EQ_SCORE",
                                              ftype=1,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=20,
                                              fprecision=8)

        if isNetwork:
            finalKeyID = self.__nodeID
        else:
            finalKeyID = self.__potentialID

        dfScore = self.__dtFinalwithsScore

        ###################### 등급 산정 부분 ######################
        # 형평성 분석은 잠재적 지역에 신규 서비스 할 경우 총 편차크기를 나타내는 것이므로, 편차 크기 값이 작을 수록 등급도 좋음

        scorefield = 'EQ_SCORE'
        step = 100 / self.__classify_count
        # 접근성 분석은 +지표, 이부분 지표 성격에 따라 다름(+지표 or 0지표)
        classRange = [cls * step for cls in range(0, self.__classify_count + 1)]
        # ex) 100, 90, 80, 70, ... 10, 0
        clsfy = np.nanpercentile(dfScore[scorefield], classRange, interpolation='linear')
        # 값이 낮을 수록 좋은(낮은 숫자) 등급
        clsfy[0] = dfScore[scorefield].min(skipna=True) - 1
        clsfy[len(clsfy) - 1] = dfScore[scorefield].max(skipna=True) + 1

        grade = 0
        gradeval = None
        prevalue = None

        if self.debugging: self.setProgressSubMsg("classify count : {}".format(len(clsfy)))
        if self.debugging: self.setProgressSubMsg("classify : {}".format(clsfy))

        for gradeval in clsfy:
            if prevalue is not None:
                if prevalue != gradeval:
                    # 접근성 분석은 +지표, 이부분 지표 성격에 따라 다름(+지표 or 0지표)
                    # print('{} 등급 : {} < GRADE <= {}'.format(grade, prevalue, gradeval))
                    dfScore.loc[
                        (prevalue < dfScore[scorefield]) & (dfScore[scorefield] <= gradeval), 'EQ_GRADE'] = grade
            prevalue = gradeval
            grade += 1

        ########################################################################################
        dictGrade = dict(zip(dfScore[finalKeyID].tolist(), dfScore['EQ_GRADE'].tolist()))

        i = 0
        finanallayer.startEditing()
        potencnt = finanallayer.featureCount()
        for feature in finanallayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / potencnt * 100))

            potenVal = feature[finalKeyID]
            eqscore = self.__dictFinalwithScore[potenVal]
            feature["EQ_SCORE"] = float(eqscore)

            try:
                eqgrade = dictGrade[potenVal]
                feature["EQ_GRADE"] = int(eqgrade)
            except:
                self.setProgressSubMsg('NODEKEY : {}, EQGRADE : {}'.format(potenVal, eqgrade))

            finanallayer.updateFeature(feature)

        finanallayer.commitChanges()

        # 불필요한 필드 제거
        if not self.debugging:
            reqfiels = [self.__potentialID, 'EQ_SCORE', 'EQ_GRADE']
            finanallayer = self.deleteFields(input=finanallayer, requredfields=reqfiels)

        if output is None:
            resultlayer = finanallayer
        else:
            resultlayer = self.vectoclayer2output(input=finanallayer, output=output)
            # resultlayer = self.qgsutils.vectorlayer2ShapeFile(vectorlayer=finanallayer,
            #                                                   output=output,
            #                                                   destCRS=finanallayer.sourceCrs())
        return resultlayer

    # # 효율성에서만 쓰는 함수임
    # def anal_nearestSOC_network(self, socNodeList, outdistfidnm, outissvredfidnm):
    #
    #     tmppoplayer = self.__populationLayer
    #     totalcnt = tmppoplayer.featureCount()
    #
    #     listpopID = []
    #     listpopNode = []
    #     listpopCnt = []
    #     listpopAccscore = []
    #     listissvrSOC = []
    #     calculatedNode = {}
    #
    #     i = 0
    #     errcnt = 0
    #     noerrcnt = 0
    #     for feature in tmppoplayer.getFeatures():
    #         i += 1
    #         if self.feedback.isCanceled(): return None
    #         self.feedback.setProgress(int(i / totalcnt * 100))
    #
    #         popID = feature[self.__poplyrID]
    #         popNodeid = feature[self.__nodeID]
    #         poppnt = feature[self.__popcntField]
    #
    #         # dis는 서비스영역내 생활SOC 존재 여부. 있으면 0, 없으면 1
    #         try:
    #             dis = calculatedNode[popNodeid]
    #         except:
    #             dis = self.get_nearesttargetDistnace(fromNodeID=popNodeid,
    #                                                  svrNodeList=socNodeList)
    #             if dis is None:
    #                 dis = self.__outofcutoff
    #                 if self.debugging:
    #                     self.setProgressSubMsg("    >> get_nearesttargetDistnace [NODE-%s] 세생활권 %sm 이내에는 현재 생활SOC가 없습니다." % (str(popNodeid), str(self.cutoff)))
    #
    #             calculatedNode[popNodeid] = dis
    #
    #         if dis > self.__cutoff:
    #             issvr = 0
    #         else:
    #             issvr = 1
    #
    #         listpopID.append(popID)
    #         listpopNode.append(popNodeid)
    #         listpopCnt.append(poppnt)
    #         listissvrSOC.append(issvr)
    #         listpopAccscore.append(dis)
    #
    #
    #     rawData = {
    #         self.__poplyrID: listpopID,
    #         self.__nodeID: listpopNode,
    #         self.__popcntField: listpopCnt,
    #         outdistfidnm: listpopAccscore,
    #         outissvredfidnm: listissvrSOC}
    #
    #     self.dfResult = pd.DataFrame(rawData)
    #
    #
    #
    #     return self.dfResult

    def anal_efficiencyCurSOC_network(self):

        cursvrlist = [feature.attribute(self.__nodeID) for feature in self.__currentSOClayer.getFeatures()]

        tmppoplayer = self.__populationLayer
        totalcnt = tmppoplayer.featureCount()

        listpopID = []
        listpopNode = []
        listpopCnt = []
        listpopAccscore = []
        listissvrSOC = []
        calculatedNode = {}

        i = 0

        self.setProgressSubMsg("{} : {}  ".format("cur", cursvrlist))

        for feature in tmppoplayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            popID = feature[self.__poplyrID]
            popNodeid = feature[self.__nodeID]
            poppnt = feature[self.__popcntField]

            # dis는 서비스영역내 생활SOC 존재 여부. 있으면 0, 없으면 1
            try:
                dis = calculatedNode[popNodeid]
            except:
                dis = self.get_nearesttargetDistnace(fromNodeID=popNodeid,
                                                     svrNodeList=cursvrlist)

                # self.setProgressSubMsg("{} : {}  ".format(i, dis))

                if dis is None:
                    dis = self.__outofcutoff
                    if self.debugging:
                        self.setProgressSubMsg(
                            "    >> get_nearesttargetDistnace [NODE-%s] 세생활권 %sm 이내에는 현재 생활SOC가 없습니다."
                            % (str(popNodeid), str(self.cutoff))
                            )

                calculatedNode[popNodeid] = dis

            if dis > self.__cutoff:
                issvr = 0
            else:
                issvr = 1

            listpopID.append(popID),
            listpopNode.append(popNodeid)
            listpopCnt.append(poppnt)
            listissvrSOC.append(issvr)
            listpopAccscore.append(dis)

        rawData = {
            self.__poplyrID: listpopID,
            self.__nodeID: listpopNode,
            self.__popcntField: listpopCnt,
            'CUR_DIST': listpopAccscore,
            'CUR_ISSVRED': listissvrSOC}

        dfCur = pd.DataFrame(rawData)

        # self.anal_nearestSOC_network(socNodeList=cursvrlist,
        #                               outdistfidnm='CUR_DIST',
        #                               outissvredfidnm='CUR_ISSVRED')

        # 기존SOC시설로 커버되는 인구데이터는 모두 제거(CUR_ISSVRED == 0)
        # dfNotSvrPop = dfCur.loc[dfCur['CUR_ISSVRED'] == 1]
        self.__dfPop = dfCur

        # self.__dfPop = pd.merge(dfCur, dfNew[[self.__nodeID, "NEW_DIST", "NEW_ISSVRED"]], on=self.__nodeID)

        tempexcel = os.path.join(self.workpath, 'anal_NeartestCurSOC_network.csv')
        self.__dfPop.to_csv(tempexcel)

        return self.__dfPop

    def anal_efficiencyPotenSOC_straight(self):

        potenID = None
        popCnt = None
        svrdPOPDict = {}

        i = 0
        tmpPOPlyr = self.__populationLayer
        popFeacnt = tmpPOPlyr.featureCount()
        for feature in tmpPOPlyr.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / popFeacnt * 100))

            popCnt = feature[self.__popcntField]
            potenID = feature[self.__potentialID]

            try:
                addedpopCnt = svrdPOPDict[potenID]
            except:
                addedpopCnt = 0

            # 잠재적 위치 서비스 영역안에 인구데이터가 하나도 없는 경우
            # self.setProgressSubMsg(str(popCnt))

            if popCnt is None or str(popCnt) is None or str(popCnt) == 'NULL': popCnt = 0

            svrdPOPDict[potenID] = addedpopCnt + int(popCnt)

        rawData = {self.__potentialID: list(svrdPOPDict.keys()),
                   'EF_SCORE': list(svrdPOPDict.values())
                   }

        self.__dictFinalwithScore = svrdPOPDict
        self.__dtFinalwithsScore = pd.DataFrame(rawData)

        tempexcel = os.path.join(self.workpath, 'efscore.csv')
        self.__dtFinalwithsScore.to_csv(tempexcel)

        return self.__dtFinalwithsScore

    def anal_efficiencyPotenSOC_network(self, relpopNodeID, relpopcntfid):

        potenID = None
        popCnt = None
        popNodeKey = None
        potenNodeKey = None

        svrdPOPDict = {}

        i = 0
        tmpPOPlyr = self.__populationLayer
        popFeacnt = tmpPOPlyr.featureCount()
        self.setProgressSubMsg("tmpPOPlyr : {}개".format(popFeacnt))

        for feature in tmpPOPlyr.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / popFeacnt * 100))

            potenID = feature[self.__potentialID]
            potenNodeKey = feature[self.__nodeID]

            popCnt = feature[relpopcntfid]
            popNodeKey = feature[relpopNodeID]

            dist = self.get_Distance(potenNodeKey, popNodeKey)

            # 거리조락을 벗어나는 NODE들
            if dist is None: dist = self.__outofcutoff
            if dist > self.__cutoff: popCnt = 0

            try:
                addedpopCnt = svrdPOPDict[potenID]
            except:
                addedpopCnt = 0

            # 잠재적 위치 서비스 영역안에 인구데이터가 하나도 없는 경우
            if popCnt is None or str(popCnt) is None or str(popCnt) == 'NULL': popCnt = 0

            svrdPOPDict[potenID] = addedpopCnt + int(popCnt)

        rawData = {self.__potentialID: list(svrdPOPDict.keys()),
                   'EF_SCORE': list(svrdPOPDict.values())
                   }

        self.__dictFinalwithScore = svrdPOPDict
        self.__dtFinalwithsScore = pd.DataFrame(rawData)

        self.__dtFinalwithsScore.to_csv(os.path.join(self.workpath, 'efscore.csv'))

        return self.__dtFinalwithsScore

    def make_efficiencyscore(self, output):

        dictScore = self.__dictFinalwithScore
        finalKeyID = self.__potentialID
        dfScore = self.__dtFinalwithsScore

        ###################### 등급 산정 부분 ######################
        scorefield = 'EF_SCORE'
        step = 100 / self.__classify_count
        # classRange = [cls * step for cls in reversed(range(0, self.__classify_count + 1))]
        classRange = [cls * step for cls in (range(0, self.__classify_count + 1))]
        clsfy = np.nanpercentile(dfScore[scorefield], classRange, interpolation='linear')

        # 접근성 분석은 +지표, 이부분 지표 성격에 따라 다름(+지표 or 0지표)
        clsfy[0] = dfScore[scorefield].min(skipna=True) - 1
        clsfy[len(clsfy) - 1] = dfScore[scorefield].max(skipna=True) + 1

        if self.debugging:
            self.setProgressSubMsg("classify count : {}".format(len(clsfy)))
            # self.setProgressSubMsg(("Max : "))
            self.setProgressSubMsg("classify : {}".format(clsfy))

        grade = self.__classify_count + 1
        gradeval = None
        prevalue = None

        for gradeval in clsfy:
            if prevalue is not None:
                if prevalue != gradeval:
                    # 접근성 분석은 +지표, 이부분 지표 성격에 따라 다름(+지표 or 0지표)
                    dfScore.loc[
                        (prevalue < dfScore[scorefield]) & (dfScore[scorefield] <= gradeval), 'EF_GRADE'] = grade
                    if self.debugging:
                        self.setProgressSubMsg("{}등급 : {} < score <= {}".format(grade, prevalue, gradeval))
            prevalue = gradeval
            grade -= 1

        ########################################################################################

        nullvalgrade = dfScore['EF_GRADE'].max(skipna=True)
        if self.debugging: self.setProgressSubMsg("nullvalgrade : %s" % str(nullvalgrade))
        dfScore.to_csv(os.path.join(self.workpath, 'efgrade.csv'))

        dictefGrade = dict(zip(dfScore[finalKeyID].tolist(), dfScore['EF_GRADE'].tolist()))

        finanallayer = self.qgsutils.addField(input=self.__potentiallayer,
                                              fid="EF_GRADE",
                                              ftype=0,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=10,
                                              fprecision=8)

        # if self.debugging:
        finanallayer = self.qgsutils.addField(input=finanallayer,
                                              fid="EF_SCORE",
                                              ftype=1,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=20,
                                              fprecision=8)

        i = 0
        finanallayer.startEditing()
        potencnt = finanallayer.featureCount()

        for feature in finanallayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / potencnt * 100))

            finalkey = feature[finalKeyID]
            try:
                efscore = float(dictScore[finalkey])
                efgrade = float(dictefGrade[finalkey])
                # todo [CHECK] 같은 노드를 가지고 있는 경우는 0 (해당 노드 확인 필요)
                if efscore == 0:
                    efscore = 0.00000001
            except:
                # 잠재적의 서비스 영역 안에 인구 Feature가 하나도 검색되지 않은 경우
                efscore = 0.00000001
                efgrade = nullvalgrade

            # if self.debugging:
            feature["EF_SCORE"] = efscore
            feature["EF_GRADE"] = int(efgrade)

            finanallayer.updateFeature(feature)

        finanallayer.commitChanges()

        # 불필요한 필드 제거
        if not self.debugging:
            reqfiels = [finalKeyID, 'EF_GRADE', 'EF_SCORE']
            finanallayer = self.deleteFields(input=finanallayer, requredfields=reqfiels)

        if output is None:
            resultlayer = finanallayer
        else:
            resultlayer = self.vectoclayer2output(input=finanallayer, output=output)
            #
            # resultlayer = self.qgsutils.vectorlayer2ShapeFile(vectorlayer=finanallayer,
            #                                                   output=output,
            #                                                   destCRS=finanallayer.sourceCrs())
        return resultlayer

    def removeRelCurSOCInPoplayer(self):

        dfpopremovedSOC = self.__dfPop

        tmppoplayer = self.__populationLayer
        tmppoplayer.removeSelection()

        totalcnt = tmppoplayer.featureCount()
        tmppoplayer.startEditing()

        i = 0
        for feature in tmppoplayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            popID = feature[self.__poplyrID]

            isSvredCurSOC = dfpopremovedSOC['CUR_ISSVRED'].loc[dfpopremovedSOC[self.__poplyrID] == popID].values[0]

            if str(isSvredCurSOC) == '1':
                expression = "\"%s\"=%s" % (self.__poplyrID, str(popID))
                # if self.debugging: self.setProgressSubMsg("expression : %s" % expression)
                tmppoplayer.selectByExpression2(expression, QgsVectorLayer.AddToSelection)

        if self.debugging: self.setProgressSubMsg("선택된 객체 : %s " % str(len(list(tmppoplayer.getSelectedFeatures()))))

        bsuccess = tmppoplayer.deleteSelectedFeatures()

        if self.debugging: self.setProgressSubMsg("삭제 결과 : %s" % str(bsuccess))

        if bsuccess:
            tmppoplayer.commitChanges()
            # self.__populationLayer = tmppoplayer
            return tmppoplayer
        else:
            tmppoplayer.rollback(deleteBuffer=True)
            return None



