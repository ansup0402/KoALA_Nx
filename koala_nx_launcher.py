import os
import string
import random

class koala_nx_launcher:
    def __init__(self, feedback, context, parameters, debugging=False, workpath=None):
        self.debugging = debugging
        self.feedback = feedback
        self.context = context
        self.parameters = parameters
        self.workpath = workpath

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

        # 1. 노드, 링크 레이어 설정
        self.setProgressMsg('[1 단계] 노드, edge 레이어 초기화...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("[debug] 노드 : createspatialindex, 객체 할당")
        model.nodeIDfield = self.parameters['IN_NODE_ID']
        model.createspatialindex(self.parameters['IN_NODE'].sourceName())
        model.nodelayer = self.parameters['IN_NODE']

        self.setDebugProgressMsg("[debug] 링크 : createspatialindex, 객체 할당")
        model.linkFromnodefield = self.parameters['IN_LINK_FNODE']
        model.linkTonodefield = self.parameters['IN_LINK_TNODE']
        model.linklengthfield = self.parameters['IN_LINK_LENGTH']
        model.linkSpeed = self.parameters['IN_LINK_SPEED']
        model.createspatialindex(self.parameters['IN_LINK'].sourceName())
        model.linklayer = self.parameters['IN_LINK']


        # 2. 출발 레이어 설정
        self.setProgressMsg('[2 단계] 출발 레이어 초기화...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("[debug] source layer : createspatialindex, nearesthubpoints, 객체 할당...")
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


        # 3. 도착 레이어 설정(IN_TARGETLYR)
        self.setProgressMsg('[3 단계] 도착 레이어 초기화...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("[debug] target layer : createspatialindex, nearesthubpoints, 객체 할당...")
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


        # 4. 네트워크 데이터 설정
        self.setProgressMsg('[4 단계] 네트워크 분석을 위한 기초데이터 생성...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("[debug] nxGraph : initNXGraph...")
        isoneway = (self.parameters['IN_LINK_TYPE'] == 0)
        model.initNXGraph(isoneway=isoneway)
        self.setDebugProgressMsg("[debug] nxGraph : createNodeEdgeInGraph...")
        graph = model.createNodeEdgeInGraph()


        # 5. 분석 실행
        self.setProgressMsg('[5 단계] 네트워크 분석 실행...')
        if self.feedback.isCanceled(): return None
        checklayer = ("[debug] 데이터 확인... \n"
                      "\t nodelayer : {} ({}) \n"
                      "\t linklayer : {} ({}) \n"
                      "\t sourceLayer : {} ({}) \n"
                      "\t targetlayer : {} ({})")
        self.setDebugProgressMsg(checklayer.format(type(model.nodelayer),
                                                   len(model.nodelayer),
                                                   type(model.linklayer),
                                                   len(model.linklayer),
                                                   type(model.sourcelayer),
                                                   len(model.sourcelayer),
                                                   type(model.targetlayer),
                                                   len(model.targetlayer)))
        self.setDebugProgressMsg("[debug] anal_NetworkSum()...")
        out = model.anal_NetworkSum()


        # 6. 분석 결과 저장
        self.setProgressMsg('[6 단계] 분석결과 저장...')
        if self.feedback.isCanceled(): return None
        self.setDebugProgressMsg("[debug] make_networksumScore()...")
        # out_path = os.path.join(self.workpath, 'networksumScore.gpkg')
        finallayer = model.make_networksumScore(output=self.parameters["OUTPUT"])
        return finallayer


    def execute_nx_distance(self):

        finallayer = None

        return finallayer
