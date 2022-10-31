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

    def execute_nx(self):
        try:
            from .koala_model import koala_model
        except ImportError:
            from koala_model import koala_model


        self.workpath = self.getSubworkspace(self.workpath)
        os.mkdir(self.workpath)
        model = koala_model(feedback=self.feedback, context=self.context, debugmode=self.debugging, workpath=self.workpath)


        ######################################## CSV 경로 테스트
        # self.setDebugProgressMsg(self.parameters['OUT_CSV'])
        # csvfilename = os.path.abspath(self.parameters['OUT_CSV'])
        # csvfilename = csvfilename
        # # csvfilename = 'C://Users//ansup//Documents//ws_ansup//Private_gdrv//test_nodelink//[2021-07-13]NODELINKDATA//vvvv.csv'
        # # csvfilename = r"C:\Users\ansup\Documents\ws_ansup\Private_gdrv\test_nodelink\[2021-07-13]NODELINKDATA\vvvv.csv"
        # self.setProgressMsg("aaa: " + csvfilename)
        # csv_file = open(csvfilename, "w")
        # n = csv_file.write("AAA")
        # csv_file.close()
        # return None
        ######################################################





        # 1. 노드, 링크 레이어 설정
        self.setProgressMsg('[1 단계] 노드, edge 레이어 초기화...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("노드 : createspatialindex, 객체 할당")
        model.nodeIDfield = self.parameters['IN_NODE_ID']
        model.createspatialindex(self.parameters['IN_NODE'].sourceName())
        model.nodelayer = self.parameters['IN_NODE']

        self.setDebugProgressMsg("링크 : createspatialindex, 객체 할당")
        model.linkFromnodefield = self.parameters['IN_LINK_FNODE']
        model.linkTonodefield = self.parameters['IN_LINK_TNODE']
        model.linklengthfield = self.parameters['IN_LINK_LENGTH']


        model.linkSpeed = self.parameters['IN_LINK_SPEED']
        model.createspatialindex(self.parameters['IN_LINK'].sourceName())
        model.linklayer = self.parameters['IN_LINK']


        # 2. 출발 레이어 설정
        self.setProgressMsg('[2 단계] 출발 레이어 초기화...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("source layer : createspatialindex, nearesthubpoints, 객체 할당...")
        model.createspatialindex(self.parameters['IN_SOURCELYR'].sourceName())
        sourcelayer = self.parameters['IN_SOURCELYR']
        out_path = None
        sourceLayerWithNode = model.nearesthubpoints(input=sourcelayer,
                                                     onlyselected=False,
                                                     sf_hub=model.nodelayer,
                                                     hubfield=model.nodeIDfield,
                                                     output=out_path
                                                     )

        out_path = None
        if self.debugging: out_path = os.path.join(self.workpath, 'sourceLayerWithNode.gpkg')
        sourceID = "NX_ID"
        self.setDebugProgressMsg("source layer ID 필드 추가: {}...".format(sourceID))
        sourcelayeraddedID = model.addIDField(input=sourceLayerWithNode, idfid=sourceID, output=out_path)
        model.sourceIDfield = sourceID

        if isinstance(sourcelayeraddedID, str):
            model.sourcelayer = model.writeAsVectorLayer(sourcelayeraddedID)
        else:
            model.sourcelayer = sourcelayeraddedID


        # 3. 도착 레이어 설정(IN_TARGETLYR)
        self.setProgressMsg('[3 단계] 도착 레이어 초기화...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("target layer : createspatialindex, nearesthubpoints, 객체 할당...")
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

        self.setDebugProgressMsg("nxGraph : initNXGraph...")
        isoneway = (self.parameters['IN_LINK_TYPE'] == 0)
        model.initNXGraph(isoneway=isoneway)
        self.setDebugProgressMsg("nxGraph : createNodeEdgeInGraph...")
        graph = model.createNodeEdgeInGraph()


        # 최근린 노드까지의 거리를 계산하기 위해 가상의 Nodelink 추가 필요.. -> 속도일때는 최소 값 정해줌,
        self.setDebugProgressMsg("target layer의 최근린 노드 추가 : addnearestNodeEdgeAsTargetlayer()...")
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("최근린 노드 추가 전 : 노드{}, 엣지{}".format(graph.number_of_nodes(), graph.number_of_edges()))
        graph = model.addnearestNodeEdgeAsTargetlayer()
        self.setDebugProgressMsg("최근린 노드 추가 후 : 노드{}, 엣지{}".format(graph.number_of_nodes(), graph.number_of_edges()))


        # 5. 분석 실행
        self.setProgressMsg('[5 단계] 네트워크 분석 실행...')
        if self.feedback.isCanceled(): return None
        checklayer = ("데이터 확인... \n"
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


        self.setDebugProgressMsg("anal_NetworkSum()...")
        model.includeIndivisualShortest = self.parameters['IN_ISDIVISUAL']
        model.namefieldofsourcelayer = self.parameters['IN_SOURCENAMEFIELD']
        model.namefieldoftargetlayer = self.parameters['IN_TARGETNAMEFIELD']

        shortestSum, shortestIndividual = model.anal_NetworkSum()


        # 6. 분석 결과 저장
        self.setProgressMsg('[6 단계] 분석결과 저장...')

        # 개별 지점까지의 거리
        if self.parameters['IN_ISDIVISUAL'] == True:
            csvfilename = ''
            if self.parameters['OUT_CSV'] == 'TEMPORARY_OUTPUT':
                import tempfile
                tmpcsv, tmppath = tempfile.mkstemp()
                csvfilename = os.path.join(tmppath, tmpcsv)                       # 임시파일 경로 지정
            else:
                csvfilename = self.parameters['OUT_CSV']

            csvfilename = os.path.abspath(csvfilename)
            csv_file = open(csvfilename, "w")
            n = csv_file.write(shortestIndividual)
            csv_file.close()
            self.setProgressMsg("다음 위치에 CSV 파일이 생성되었습니다. : {}".format(csv_file))


        if self.feedback.isCanceled(): return None
        self.setDebugProgressMsg("make_networksumScore()...")
        # out_path = os.path.join(self.workpath, 'networksumScore.gpkg')
        finallayer = model.make_networksumScore(output=self.parameters["OUTPUT"])



        return finallayer


    def execute_nx_distance(self):

        finallayer = None

        return finallayer
