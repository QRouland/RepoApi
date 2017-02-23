import unittest
from tempfile import TemporaryDirectory


class ApkfinderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.apk_list = ("someapk-1.0.0.apk", "someapk-1.0.1.apk", "someapk-2.0.0.apk", "someotherapk-0.0.1.apk")
        self.bad_file_list = ("someapk-1.0.0.txt", "badfile.ze", "radomfile")
        self.apk_folder = TemporaryDirectory()
        for files in (self.apk_list, self.bad_file_list):
            for file in files:
                open("{}/{}".format(self.apk_folder.name, file), 'a').close()

    def tearDown(self):
        pass

    def test_find_pacakge(self):
        # TODO Tests :D
        pass
