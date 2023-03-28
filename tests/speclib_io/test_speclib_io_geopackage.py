# noinspection PyPep8Naming
import os
import unittest

from osgeo import ogr
from qgis.core import QgsVectorLayer, QgsFeature, QgsProcessingFeedback

from qps.speclib.core.spectrallibrary import SpectralLibraryUtils
from qps.speclib.core.spectrallibraryio import SpectralLibraryIO
from qps.speclib.io.geopackage import GeoPackageSpectralLibraryIO, GeoPackageSpectralLibraryExportWidget
from qps.testing import TestObjects, TestCaseBase, start_app2

start_app2()


class TestSpeclibIO_GPKG(TestCaseBase):
    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:
        super(TestSpeclibIO_GPKG, cls).setUpClass(*args, **kwds)
        cls.registerIO(cls)

    @classmethod
    def tearDownClass(cls):
        super(TestSpeclibIO_GPKG, cls).tearDownClass()

    def registerIO(self):
        ios = [GeoPackageSpectralLibraryIO()]
        SpectralLibraryIO.registerSpectralLibraryIO(ios)

    def test_write_profiles(self):
        IO = GeoPackageSpectralLibraryIO()

        exportWidget = IO.createExportWidget()
        self.assertIsInstance(exportWidget, GeoPackageSpectralLibraryExportWidget)
        sl: QgsVectorLayer = TestObjects.createSpectralLibrary()
        sl.startEditing()
        for f in sl.getFeatures():
            f: QgsFeature
            f.setAttribute('name', f'Name {f.id()}')
            sl.updateFeature(f)
        self.assertTrue(sl.commitChanges())

        exportWidget.setSpeclib(sl)
        testdir = self.createTestOutputDirectory() / 'Geopackage'
        os.makedirs(testdir, exist_ok=True)

        path = testdir / 'exported_profiles.gpkg'
        files = SpectralLibraryUtils.writeToSource(sl, path)
        self.assertTrue(len(files) == 1)

        # overwrite
        files = SpectralLibraryUtils.writeToSource(sl, path)
        self.assertTrue(len(files) == 1)

        exportSettings = dict()
        feedback = QgsProcessingFeedback()
        files = IO.exportProfiles(path.as_posix(), sl.getFeatures(), exportSettings, feedback)

        self.assertIsInstance(files, list)
        for file in files:
            ds = ogr.Open(file)
            self.assertIsInstance(ds, ogr.DataSource)
            lyr = QgsVectorLayer(file)
            self.assertIsInstance(lyr, QgsVectorLayer)
            self.assertTrue(lyr.isValid())
            self.assertTrue(lyr.featureCount() > 0)

        s = ""


if __name__ == '__main__':
    unittest.main(buffer=False)
