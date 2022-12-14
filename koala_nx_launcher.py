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


        # 1. ??????, ?????? ????????? ??????
        self.setProgressMsg('[1 ??????] ??????, edge ????????? ?????????...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("?????? : createspatialindex, ?????? ??????")
        model.nodeIDfield = self.parameters['IN_NODE_ID']
        model.createspatialindex(self.parameters['IN_NODE'].sourceName())
        model.nodelayer = self.parameters['IN_NODE']

        self.setDebugProgressMsg("?????? : createspatialindex, ?????? ??????")
        model.linkFromnodefield = self.parameters['IN_LINK_FNODE']
        model.linkTonodefield = self.parameters['IN_LINK_TNODE']
        model.linklengthfield = self.parameters['IN_LINK_LENGTH']


        model.linkSpeed = self.parameters['IN_LINK_SPEED']
        model.createspatialindex(self.parameters['IN_LINK'].sourceName())
        model.linklayer = self.parameters['IN_LINK']


        # 2. ?????? ????????? ??????
        self.setProgressMsg('[2 ??????] ?????? ????????? ?????????...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("source layer : createspatialindex, nearesthubpoints, ?????? ??????...")
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
        self.setDebugProgressMsg("source layer ID ?????? ??????: {}...".format(sourceID))
        sourcelayeraddedID = model.addIDField(input=sourceLayerWithNode, idfid=sourceID, ftype=2, formula="""'nx' + to_string($id)""", output=out_path)
        model.sourceIDfield = sourceID

        if isinstance(sourcelayeraddedID, str):
            model.sourcelayer = model.writeAsVectorLayer(sourcelayeraddedID)
        else:
            model.sourcelayer = sourcelayeraddedID


        # 3. ?????? ????????? ??????(IN_TARGETLYR)
        self.setProgressMsg('[3 ??????] ?????? ????????? ?????????...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("target layer : createspatialindex, nearesthubpoints, ?????? ??????...")
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


        # 4. ???????????? ????????? ??????
        self.setProgressMsg('[4 ??????] ???????????? ????????? ?????? ??????????????? ??????...')
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("nxGraph : initNXGraph...")
        isoneway = (self.parameters['IN_LINK_TYPE'] == 0)
        model.initNXGraph(isoneway=isoneway)
        self.setDebugProgressMsg("nxGraph : createNodeEdgeInGraph...")
        graph = model.createNodeEdgeInGraph()


        # ????????? ??????????????? ????????? ???????????? ?????? ????????? Nodelink ?????? ??????.. -> ??????????????? ?????? ??? ?????????,
        self.setDebugProgressMsg("target layer??? ????????? ?????? ?????? : addnearestNodeEdgeAsTargetlayer()...")
        if self.feedback.isCanceled(): return None

        self.setDebugProgressMsg("????????? ?????? ?????? ??? : ??????{}, ??????{}".format(graph.number_of_nodes(), graph.number_of_edges()))
        graph = model.addnearestNodeEdgeAsTargetlayer()
        self.setDebugProgressMsg("????????? ?????? ?????? ??? : ??????{}, ??????{}".format(graph.number_of_nodes(), graph.number_of_edges()))


        # 5. ?????? ??????
        self.setProgressMsg('[5 ??????] ???????????? ?????? ??????...')
        if self.feedback.isCanceled(): return None
        checklayer = ("????????? ??????... \n"
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


        # 6. ?????? ?????? ??????
        self.setProgressMsg('[6 ??????] ???????????? ??????...')

        # ?????? ??????????????? ??????
        finalcsv = None
        if self.parameters['IN_ISDIVISUAL'] == True:
            csvfilename = ''
            if self.parameters['OUT_CSV'] == 'TEMPORARY_OUTPUT':
                import tempfile
                tmpcsv, tmppath = tempfile.mkstemp()
                csvfilename = os.path.join(tmppath, tmpcsv)                       # ???????????? ?????? ??????
            else:
                csvfilename = self.parameters['OUT_CSV']

            csvfilename = os.path.abspath(csvfilename)
            csv_file = open(csvfilename, "w")
            n = csv_file.write(shortestIndividual)
            csv_file.close()
            finalcsv = csvfilename
            self.setProgressMsg("?????? ????????? CSV ????????? ?????????????????????. : {}".format(csv_file))


        if self.feedback.isCanceled(): return None
        self.setDebugProgressMsg("make_networksumScore()...")
        # out_path = os.path.join(self.workpath, 'networksumScore.gpkg')
        finallayer = model.make_networksumScore(output=self.parameters["OUTPUT"])



        return finallayer, finalcsv


    def execute_nx_distance(self):

        finallayer = None

        return finallayer
