import subprocess, time, httplib, cStringIO, ConfigParser

class Unittest_BadRequests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global serverp, connection, fresh_request, void
        void = open('/dev/null','w')
        serverp = subprocess.Popen(['python', '-c', '"import gMiner.gm_server as srv; srv.gmServer(port=7520).serve()"'])
        print "\nWaiting for server to start"
        time.sleep(2)
        print "Finished waiting"        
        connection = httplib.HTTPConnection('localhost')
        fresh_request = '''
[gMiner]
version=0.1.5
track1=/scratch/tracks/qual/sql/ribosome_genesis.sql
track1_name="Bad request track 1"
track2=/scratch/tracks/qual/sql/ribosome_proteins.sql
track2_name="Bad request track 2"
operation_type=desc_stat
characteristic=number_of_features
        '''

    @classmethod
    def tearDownClass(cls):
        global serverp
        serverp.terminate()
        void.close()

    #----------------------------#
    def request_make_fresh(self):
        global fresh_request
        self.config = ConfigParser.ConfigParser()
        file = cStringIO.StringIO()
        file.write(fresh_request)
        file.seek(0)
        self.config.readfp(file)

    def request_generate_text(self):
        file = cStringIO.StringIO()
        self.config.write(file)
        file.seek(0)
        return file.read()

    def execute_request(self, body):
        global connection
        connection.request('POST','/gMiner/', body)
        r = connection.getresponse()
        return r.status, r.reason, r.read()
    
    def no_timeout(self, body):
        status = 408
        while status == 408:
            status, reason, data = self.execute_request(body)
            if status == 500: print data
        return status, reason, data   

    #----------------------------#
    def test_basic(self):
        self.assertEqual(self.no_timeout('')[0], 411)
        self.assertEqual(self.no_timeout('nDiWfdJ')[0], 400)

    def test_invalid(self):
        params = ['operation_type', 'characteristic', 'selected_regions', 'track1']
        regions = ['0000', ':::', '1:2:3;:::', ';;;:::;;;']
        for param in params:
            for region in regions:
                #print (param, region)
                self.request_make_fresh()
                self.config.set("gMiner",param,region)
                self.assertEqual(self.no_timeout(self.request_generate_text())[0], 400)

    def todo(self):
        regions = [False, True]
        for region in regions:
            self.request_make_fresh()
            self.config.set("gMiner","selected_regions",region)
            self.assertEqual(self.no_timeout(self.request_generate_text())[0], 400)

    def test_success(self):
        self.request_make_fresh()
        self.assertEqual(self.no_timeout(self.request_generate_text())[0], 200)

# Add it #
if __name__ == '__main__':
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Unittest_BadRequests))
