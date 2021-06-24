import pathlib
import unittest

class TestTemporaryDirectory(unittest.TestCase):
    def test_create_tempdir(self):
        from common import TemporaryDirectory
        with TemporaryDirectory(pathlib.Path("test_filename.odb")) as temp_dir:
            self.assertTrue(pathlib.Path("test_filename_odb_tempdir0").exists())

    def test_create_additional_tempdir(self):
        from common import TemporaryDirectory
        with TemporaryDirectory(pathlib.Path("test_filename.odb")) as temp_dir:
            with TemporaryDirectory(pathlib.Path("test_filename.odb")) as temp_dir:
                self.assertTrue(pathlib.Path("test_filename_odb_tempdir1").exists())

    def test_cleanup(self):
        from common import TemporaryDirectory
        with TemporaryDirectory(pathlib.Path("test_filename.odb")) as temp_dir:
            try:
                raise ValueError("Just to raise something")
            except ValueError:
                pass
        self.assertFalse(pathlib.Path("test_filename_odb_tempdir0").exists())