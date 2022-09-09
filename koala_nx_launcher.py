import os
import string
import random

class koala_nx_launcher:
    def __init__(self, feedback, context, parameters, debugging=False, workpath=None):
        self.debugging = debugging
        self.feedback = feedback
        self.context = context
        self.parameters = parameters

        # 'OUTPUT': 'ogr:dbname=\'C:/Users/ansup/Downloads/aaaaa.gpkg\' table=\"bbbb\" (geom)', 'SEGMENTS': 5}

        self.workpath = workpath

        # self.cutoffconst_acc = 1000000
        # self.cutoffconst_eff = 1000000
        # self.cutoffconst_equ = 1000000

        self.enablelogmsg = False


    def setDebugProgressMsg(self, msg, output=None):
        if self.debugging or self.enablelogmsg:
            import time
            now = time.localtime()

            snow = "%04d-%02d-%02d %02d:%02d:%02d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

            # self.feedback.pushConsoleInfo("\n%s %s" % (snow, msg))
            outputmessage = "{} [debug] {}".format(snow, msg)
            if not output is None:
                outputmessage = outputmessage + "\n{}".format(output)

            # self.feedback.pushCommandInfo(outputmessage)
            self.feedback.pushDebugInfo(outputmessage)
            # self.feedback.pushInfo("\n%s %s" % (snow, msg))
            # self.feedback.pushConsoleInfo("\n%s %s" % (snow, msg))
            # self.feedback.pushDebugInfo("\n%s %s" % (snow, msg))

    def setProgressMsg(self, msg):
        import time
        now = time.localtime()

        snow = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

        # self.feedback.pushConsoleInfo("\n%s %s" % (snow, msg))
        self.feedback.pushCommandInfo("\n%s %s" % (snow, msg))
        # self.feedback.pushInfo("\n%s %s" % (snow, msg))
        # self.feedback.pushConsoleInfo("\n%s %s" % (snow, msg))
        # self.feedback.pushDebugInfo("\n%s %s" % (snow, msg))

    def getSubworkspace(self, basepath, lengh=10):
        # To change the workspace for batch processing
        string_pool = string.ascii_lowercase
        result = ""
        for i in range(lengh):
            result += random.choice(string_pool)

        workspace = os.path.join(basepath, result)

        return workspace

    def execute_nx_speed(self):
        try:
            from .koala_model import koala_model
        except ImportError:
            from koala_model import koala_model

        self.workpath = self.getSubworkspace(self.workpath)
        os.mkdir(self.workpath)
        model = koala_model(feedback=self.feedback, context=self.context, debugmode=self.debugging, workpath=self.workpath)

        # 1. 노드 레이어 설정
        self.setDebugProgressMsg("[Start] 1. 노드 레이어 설정...")
        model.nodeIDfield = self.parameters['IN_NODE_ID']
        model.createspatialindex(self.parameters['IN_NODE'].sourceName())
        model.nodelayer = self.parameters['IN_NODE']

        # 2. 링크 레이어 설정
        self.setDebugProgressMsg("[Start] 2. 링크 레이어 설정...")
        model.linkFromnodefield = self.parameters['IN_LINK_FNODE']
        model.linkTonodefield = self.parameters['IN_LINK_TNODE']
        model.linklengthfield = self.parameters['IN_LINK_LENGTH']
        model.linkSpeed = self.parameters['IN_LINK_SPEED']

        model.createspatialindex(self.parameters['IN_LINK'].sourceName())
        model.linklayer = self.parameters['IN_LINK']


        # 3. 출발 레이어 설정
        self.setDebugProgressMsg("[Start] 3. 출발 레이어 설정...")
        model.createspatialindex(self.parameters['IN_SOURCELYR'].sourceName())
        sourcelayer = self.parameters['IN_SOURCELYR']
        out_path = None
        if self.debugging: out_path = os.path.join(self.workpath, 'sourceLayerWithNode.gpkg')
        sourceLayerWithNode = model.nearesthubpoints(input=sourcelayer,
                                                onlyselected=False,
                                                sf_hub=model.nodelayer,
                                                hubfield=model.nodeIDfield,
                                                output=out_path
                                                )
        if isinstance(sourceLayerWithNode, str):
            model.sourcelayer = model.writeAsVectorLayer(sourceLayerWithNode)
        else:
            model.sourcelayer = sourceLayerWithNode


        # 프로젝트 좌표계를 설정하지 않은 경우 최근린 노드의 거리값이 나오지 않음


        # 4. 도착 레이어 설정(IN_TARGETLYR)
        self.setDebugProgressMsg("[Start] 4. 도착 레이어 설정...")
        model.createspatialindex(self.parameters['IN_TARGETLYR'].sourceName())
        targetlayer = self.parameters['IN_TARGETLYR']
        out_path = None
        if self.debugging: out_path = os.path.join(self.workpath, 'targetLayerWithNode.gpkg')
        # source2 = model.vectorlayer2ShapeFile(sourcelayer, out_path)
        targetLayerWithNode = model.nearesthubpoints(input=targetlayer,
                                                onlyselected=False,
                                                sf_hub=model.nodelayer,
                                                hubfield=model.nodeIDfield,
                                                output=out_path
                                                )
        if isinstance(targetLayerWithNode, str):
            model.targetlayer = model.writeAsVectorLayer(targetLayerWithNode)
        else:
            model.targetlayer = targetLayerWithNode
        # self.setDebugProgressMsg("targetlayer : {} ({})".format(type(model.targetlayer), len(model.targetlayer)))


        # 5. 네트워크 데이터 설정
        self.setProgressMsg('[3 단계] 최단 거리 분석 위한 기초 자료를 생성합니다....')
        if self.feedback.isCanceled(): return None
        isoneway = (self.parameters['IN_LINK_TYPE'] == 0)
        model.initNXGraph(isoneway=isoneway)
        self.setDebugProgressMsg("링크데이터를 활용하여 networkx의 graph객체를 생성합니다...")
        graph = model.createNodeEdgeInGraph()


        # 6. 분석 시작
        self.setProgressMsg('[3 단계] 네트워크 분석을 시작합니다....')
        self.setDebugProgressMsg("nodelayer : {} ({})".format(type(model.nodelayer), len(model.nodelayer)))
        self.setDebugProgressMsg("linklayer : {} ({})".format(type(model.linklayer), len(model.linklayer)))
        self.setDebugProgressMsg("sourceLayer : {} ({})".format(type(model.sourcelayer), len(model.sourcelayer)))
        self.setDebugProgressMsg("targetlayer : {} ({})".format(type(model.targetlayer), len(model.targetlayer)))
        out = model.anal_NetworkSum()


        # 5-3 형평성 분석 결과 평가
        if self.feedback.isCanceled(): return None
        self.setDebugProgressMsg("네트워크 분석 결과를 저장합니다...")
        # out_path = os.path.join(self.workpath, 'networksumScore.gpkg')
        finallayer = model.make_networksumScore(output=self.parameters["OUTPUT"])
        return finallayer

    def execute_nx_distance(self):

        finallayer = None

        return finallayer
