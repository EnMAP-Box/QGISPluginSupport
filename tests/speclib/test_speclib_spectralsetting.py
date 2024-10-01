import unittest

from osgeo import gdal

from qgis.core import QgsProcessingContext, QgsRasterBlockFeedback, QgsRasterFileWriter, QgsRasterLayer, QgsRasterPipe
from qps.speclib.core.spectralprofile import SpectralSetting
from qps.testing import start_app, TestCase, TestObjects
from qps.utils import parseWavelength

start_app()


class TestCore(TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:
        super(TestCore, cls).setUpClass(*args, **kwds)
        from qps.speclib.core.spectrallibraryio import initSpectralLibraryIOs
        initSpectralLibraryIOs()

    def test_SpectralSetting(self):
        from qpstestdata import enmap
        lyr1: QgsRasterLayer = TestObjects.createRasterLayer(nb=10)
        lyr2: QgsRasterLayer = QgsRasterLayer(enmap.as_posix(), 'EnMAP Tiff', 'gdal')

        test_dir = self.createTestOutputDirectory()

        for i, lyr in enumerate([lyr1, lyr2]):
            rasterblockFeedback = QgsRasterBlockFeedback()
            processingContext = QgsProcessingContext()
            processingFeedback = processingContext.feedback()

            settingA: SpectralSetting = SpectralSetting.fromRasterLayer(lyr)
            self.assertIsInstance(settingA, SpectralSetting)

            file_name = test_dir / f'layer_{i}.tiff'
            file_name = file_name.as_posix()
            file_writer = QgsRasterFileWriter(file_name)

            dp = lyr.dataProvider().clone()
            pipe = QgsRasterPipe()
            self.assertTrue(pipe.set(dp), msg=f'Cannot set pipe provider to write {file_name}')
            error = file_writer.writeRaster(
                pipe,
                dp.xSize(),
                dp.ySize(),
                dp.extent(),
                dp.crs(),
                processingContext.transformContext(),
                rasterblockFeedback
            )

            del file_writer
            self.assertTrue(error == QgsRasterFileWriter.WriterError.NoError, msg='Error')
            settingA.writeToLayer(file_name)

            self.assertEqual(settingA.n_bands(), lyr.bandCount())
            settingB = SpectralSetting.fromRasterLayer(file_name)
            self.assertIsInstance(settingB, SpectralSetting)

            ds: gdal.Dataset = gdal.Open(file_name)

            wl, wlu = parseWavelength(ds)
            del ds
            self.assertListEqual(settingB.x(), wl.tolist())
            self.assertEqual(settingB.xUnit(), wlu)
            self.assertEqual(settingA, settingB)


if __name__ == '__main__':
    unittest.main(buffer=False)
