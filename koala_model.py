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
*                           [추가] addnearestNodeEdgeAsTargetlayer : 도착점의 최근린 노드까지의 거리 정보 추가
*                           [추가] calMinSpeedinLinklayer : 최저 속도 공통활용 위해 별도 분리(지점->노드, 속도누락링크)
*                           [createNodeEdgeInGraph] 속도 기반 분석시 단위를 km로 수정(/1000)
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

        self.__minSpeed = 0
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
    def nodelayer(self):
        return (self.__nodelayer)

    @nodelayer.setter
    def nodelayer(self, value):
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
        if self.__linkSpeed is not None: self.calMinSpeedinLinklayer()

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

    def multiparttosingleparts(self, input, onlyselected=False, output='TEMPORARY_OUTPUT'):
        return self.qgsutils.multiparttosingleparts(input=input, onlyselected=onlyselected, output=output)

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

    def vectoclayer2output(self, input, output):
        expression = "1 = 1"
        tmplayer = self.qgsutils.selectbyexpression2(input=input, expression=expression)
        return self.qgsutils.saveselectedfeatrues(input=tmplayer, output=output)


    #########################################################################################################
    def calMinSpeedinLinklayer(self):
        tmplayer = self.__linklayer
        tmplayer = self.qgsutils.selectbyexpression2(input=tmplayer, expression='%s > 0' % self.__linkSpeed)
        tmplayer = self.qgsutils.saveselectedfeatrues(input=tmplayer)

        if self.debugging: self.setProgressSubMsg("calMinSpeedinLinklayer\nnot zero feature(link) : {}".format(tmplayer.featureCount()))

        idx = tmplayer.fields().indexFromName(self.__linkSpeed)
        self.__minSpeed = tmplayer.minimumValue(idx)

        if self.debugging: self.setProgressSubMsg("minimumValue speed : {}".format(str(self.__minSpeed)))



    # NX+"NODE 값" : taget지점에서 최근린 노드까지 임의로 추가한 node, edge 정보임
    def addnearestNodeEdgeAsTargetlayer(self):
        i = 0
        totalcnt = 0
        minimumSpeed = self.__minSpeed
        fnodes = []
        tnodes = []
        weights = []
        totalcnt = self.__targetlayer.featureCount()
        for feature in self.__targetlayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            # tempNodes.append(feature.attribute(self.__nodeID))
            # tempNodes.append(feature.attribute(self.__toNodefield))

            fnodes.append(feature.attribute(self.__nodeID))
            tnodes.append("NX"+feature.attribute(self.__nodeID))
            length = feature.attribute("HubDist")

            if self.__linkSpeed is None:
                weights.append(length)
            else:
                speed = minimumSpeed
                linktime = length / 1000 / speed
                weights.append(linktime)

        allnodes = list(set(tnodes))
        tmplink = tuple(zip(fnodes, tnodes, weights))
        self.nxGraph.add_nodes_from(allnodes)
        self.nxGraph.add_weighted_edges_from(tmplink)

        return self.nxGraph


    def createNodeEdgeInGraph(self):

        fnodes = []
        tnodes = []
        weights = []

        tempNodes = []
        totalcnt = self.__linklayer.featureCount()
        if self.debugging:
            self.setProgressSubMsg("speed mode : {}, count of link :{}".format(str(self.__linkSpeed is not None), str(totalcnt)))

        minimumSpeed = self.__minSpeed

        i = 0
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


    def make_networksumScore(self, output=None):

        finanallayer = self.qgsutils.addField(input=self.__sourcelayer,
                                              fid="NX_SCORE",
                                              ftype=1,  # 0 — Integer, 1 — Float, 2 — String
                                              flen=10,
                                              fprecision=8)

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

        # NX+"NODEID" 필드: taget지점에서 최근린 노드까지 임의로 추가한 node, edge 정보임
        tmptargetNodelist = [feature.attribute(targetNodefid) for feature in self.__targetlayer.getFeatures()]
        targetNodelist = list(map(lambda x: "NX" + str(x), tmptargetNodelist))
        # if self.debugging: self.setProgressSubMsg("[debug] targetNodelist : {}".format(targetNodelist))

        i = 0
        totalcnt = sourcelayer.featureCount()
        for feature in sourcelayer.getFeatures():
            i += 1
            if self.feedback.isCanceled(): return None
            self.feedback.setProgress(int(i / totalcnt * 100))

            sourceNodeId = feature[sourceNodefid]
            tmpsourcenearNodeDist = feature['HubDist']

            if self.__linkSpeed is None:
                sourcenearNodeDist = tmpsourcenearNodeDist
            else:
                sourcenearNodeDist = tmpsourcenearNodeDist / 1000 / self.__minSpeed

            # 최단거리 분석
            shortest = nx.single_source_dijkstra_path_length(self.nxGraph, sourceNodeId, weight='weight')
            targetshortest = {idx: val for idsingle_source_dijkstra_path_lengthx, val in shortest.items() if (idx in targetNodelist)}
            shortestDistsum = sum(targetshortest.values())

            # if self.debugging: self.setProgressSubMsg("[debug] targetshortest : {}, shortestDistsum : {}".format(targetshortest, shortestDistsum))
            listsourceNodeID.append(sourceNodeId)
            listShortestSum.append(shortestDistsum+sourcenearNodeDist)

        rawData = {sourceNodefid: listsourceNodeID,
                   "NX_WEIGHT": listShortestSum}


        self.__networkSum = pd.DataFrame(rawData)

        if self.debugging:
            tempexcel = os.path.join(self.workpath, 'source_network.csv')
            self.__networkSum.to_csv(tempexcel)

        return self.__networkSum




