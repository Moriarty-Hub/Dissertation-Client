import unittest
import os

import Monitor
import Constants


class MonitorTest(unittest.TestCase):
    def test_initializeConstantVariables(self):
        self.assertEqual(Constants.ENV_WORKSPACE, None)
        self.assertEqual(Constants.DATABASE_CONNECTION, None)
        self.assertEqual(Constants.DATABASE_CURSOR, None)
        Monitor.initializeConstantVariables()
        self.assertEqual(Constants.ENV_WORKSPACE, os.getcwd())
        self.assertNotEqual(Constants.DATABASE_CONNECTION, None)
        self.assertNotEqual(Constants.DATABASE_CURSOR, None)

    def test_updatePocInfo(self):
        pass

    def test_updateDatabase(self):
        pass

    def test_clearPocInfo(self):
        pass

    def test_collectPocInfoFromWebsite(self):
        pass

    def test_insertPocInfoIntoDatabase(self):
        pass

    def test_updateLocalPocFile(self):
        pass

    def test_removeLocalPocFile(self):
        pass

    def test_collectPocFileUrlFromWebsite(self):
        pass

    def test_downloadPocFile(self):
        pass

    def test_releaseResources(self):
        pass


if __name__ == '__main__':
    unittest.main()
