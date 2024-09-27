# noinspection PyPep8Naming
import pathlib
import re
import unittest
from datetime import datetime
from typing import List

from qps.speclib.core import is_spectral_feature, profile_field_names
from qps.speclib.core.spectrallibraryio import SpectralLibraryImportDialog, initSpectralLibraryIOs
from qps.speclib.core.spectralprofile import decodeProfileValueDict, isProfileValueDict, validateProfileValueDict
from qps.speclib.io.svc import SVCSigFile, SVCSpectralLibraryIO
from qps.testing import TestCase, TestObjects, start_app
from qps.utils import file_search

start_app()


class TestSpeclibIO_SVC(TestCase):

    def registerIO(self):
        initSpectralLibraryIOs()

    def test_read_sigFile(self):

        for file in self.svcFiles():
            print(f'read {file}')
            svc = SVCSigFile(file)
            self.assertIsInstance(svc, SVCSigFile)
            self.assertTrue(isProfileValueDict(svc.reference()))
            self.assertTrue(isProfileValueDict(svc.target()))
            self.assertIsInstance(svc.targetTime(), datetime)
            self.assertIsInstance(svc.referenceTime(), datetime)
            self.assertIsInstance(svc.metadata(), dict)
            profile = svc.asFeature()
            self.assertTrue(is_spectral_feature(profile))

        for file in self.svcFiles():
            settings = {}
            profiles = SVCSpectralLibraryIO.importProfiles(file, importSettings=settings)
            self.assertIsInstance(profiles, list)
            self.assertTrue(len(profiles) > 0)
            for p in profiles:
                self.assertTrue(is_spectral_feature(p))

                for name in profile_field_names(p):
                    data = decodeProfileValueDict(p.attribute(name))
                    self.assertTrue(validateProfileValueDict(data))
                    s = ""

    def svcFiles(self) -> List[str]:
        import qpstestdata
        svc_dir = pathlib.Path(qpstestdata.__file__).parent / 'svc'
        return list(file_search(svc_dir, re.compile(r'.*\.sig$'), recursive=True))

    @unittest.skipIf(TestCase.runsInCI(), 'Skipped QDialog test in CI')
    def test_dialog(self):
        self.registerIO()
        sl = TestObjects.createSpectralLibrary()
        import qpstestdata.asd
        root = pathlib.Path(qpstestdata.__file__).parent / 'svc'

        SpectralLibraryImportDialog.importProfiles(sl, defaultRoot=root.as_posix())


if __name__ == '__main__':
    unittest.main(buffer=False)