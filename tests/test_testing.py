# coding=utf-8
"""Resources test.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest

import numpy as np

import qps.testing
from osgeo import gdal
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes
from qgis.core import QgsProject, QgsApplication, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsProcessingRegistry, QgsLayerTree, QgsLayerTreeModel
from qgis.gui import QgsLayerTreeView, QgisInterface, QgsGui


class TestCasesClassTesting(unittest.TestCase):

    def setUp(self) -> None:
        app = QgsApplication.instance()
        import qgis.testing
        if hasattr(qgis.testing, 'QGISAPP'):
            qgis.testing.stop_app()

    def test_init(self):
        import qps.testing
        self.assertTrue(qps.testing is not None)

        qgis_app = qps.testing.start_app(options=qps.testing.StartOptions.All)

        self.assertIsInstance(qgis_app, QgsApplication)
        self.assertIsInstance(qgis_app.libexecPath(), str)

        self.assertTrue(len(qgis_app.processingRegistry().providers()) > 0)

        self.assertIsInstance(qgis_app.processingRegistry(), QgsProcessingRegistry)
        self.assertTrue(len(qgis_app.processingRegistry().algorithms()) > 0)

        self.assertIsInstance(QgsGui.instance(), QgsGui)
        self.assertTrue(len(QgsGui.instance().editorWidgetRegistry().factories()) > 0,
                        msg='Standard QgsEditorWidgetWrapper not initialized')

        # test iface
        import qgis.utils
        iface = qgis.utils.iface

        self.assertIsInstance(iface, QgisInterface)
        self.assertIsInstance(iface, qps.testing.QgisMockup)

        lyr1 = qps.testing.TestObjects.createVectorLayer()
        lyr2 = qps.testing.TestObjects.createVectorLayer()

        self.assertIsInstance(iface.layerTreeView(), QgsLayerTreeView)
        self.assertIsInstance(iface.layerTreeView().layerTreeModel(), QgsLayerTreeModel)
        root = iface.layerTreeView().layerTreeModel().rootGroup()
        self.assertIsInstance(root, QgsLayerTree)
        self.assertEqual(len(root.findLayers()), 0)

        # QgsProject.instance().layersAdded.connect(lambda : print('ADDED'))
        # QgsProject.instance().legendLayersAdded.connect(lambda: print('ADDED LEGEND'))

        QgsProject.instance().addMapLayer(lyr1, False)
        QgsProject.instance().addMapLayer(lyr2, True)

        QgsApplication.processEvents()

        self.assertTrue(lyr1.id() not in root.findLayerIds())
        self.assertTrue(lyr2.id() in root.findLayerIds())

        app = QgsApplication.instance()
        ENV = app.systemEnvVars()
        for k in sorted(ENV.keys()):
            print('{}={}'.format(k, ENV[k]))

    def test_init_minimal(self):
        qgis_app = qps.testing.start_app(options=qps.testing.StartOptions.Minimized)

        self.assertIsInstance(qgis_app, QgsApplication)
        self.assertIsInstance(qgis_app.libexecPath(), str)


class TestCasesTestObject(qps.testing.TestCase):

    def test_spectralProfiles(self):
        from qps.testing import TestObjects

        profiles = list(TestObjects.spectralProfiles(10))
        self.assertIsInstance(profiles, list)
        self.assertTrue(len(profiles) == 10)

    def test_VectorLayers(self):
        from qps.testing import TestObjects
        from osgeo import ogr

        ds = TestObjects.createVectorDataSet(wkb=ogr.wkbPoint)
        self.assertIsInstance(ds, ogr.DataSource)
        self.assertTrue(ds.GetLayerCount() == 1)
        lyr = ds.GetLayer(0)
        self.assertIsInstance(lyr, ogr.Layer)
        self.assertEqual(lyr.GetGeomType(), ogr.wkbPoint)
        self.assertTrue(lyr.GetFeatureCount() > 0)

        ds = TestObjects.createVectorDataSet(wkb=ogr.wkbLineString)
        self.assertIsInstance(ds, ogr.DataSource)
        self.assertTrue(ds.GetLayerCount() == 1)
        lyr = ds.GetLayer(0)
        self.assertIsInstance(lyr, ogr.Layer)

        self.assertTrue(lyr.GetFeatureCount() > 0)
        self.assertEqual(lyr.GetGeomType(), ogr.wkbLineString)

        wkbTypes = [QgsWkbTypes.PointGeometry, QgsWkbTypes.Point,
                    QgsWkbTypes.LineGeometry, QgsWkbTypes.LineString,
                    QgsWkbTypes.PolygonGeometry, QgsWkbTypes.Polygon]
        for wkbType in wkbTypes:
            lyr = TestObjects.createVectorLayer(wkbType)
            self.assertIsInstance(lyr, QgsVectorLayer)
            self.assertTrue(lyr.isValid())
            self.assertIsInstance(lyr.crs(), QgsCoordinateReferenceSystem)
            self.assertTrue(lyr.crs().isValid())
            for f in lyr.getFeatures():
                f: QgsFeature
                g: QgsGeometry = f.geometry()
                self.assertFalse(g.isNull())
                self.assertFalse(g.isEmpty())
                self.assertTrue(g.isGeosValid(), msg=f'{f.id()} {f.attributeMap()}')

    def test_coredata(self):
        from qps.testing import TestObjects
        import numpy as np
        array, wl, wlu, gt, wkt = TestObjects.coreData()
        self.assertIsInstance(array, np.ndarray)
        self.assertIsInstance(wl, np.ndarray)
        self.assertTrue(len(wl) > 0)
        self.assertIsInstance(wlu, str)
        self.assertTrue(len(gt) == 6)
        self.assertIsInstance(wkt, str)

    def test_RasterData(self):
        from qps.testing import TestObjects

        cl = TestObjects.createRasterDataset(10, 20, nc=7)
        self.assertIsInstance(cl, gdal.Dataset)
        self.assertEqual(cl.RasterCount, 1)
        self.assertEqual(cl.RasterXSize, 10)
        self.assertEqual(cl.RasterYSize, 20)

        classNames = cl.GetRasterBand(1).GetCategoryNames()
        self.assertEqual(len(classNames), 7)

        ns = 250
        nl = 100
        nb = 10
        ds = TestObjects.createRasterDataset(ns, nl, nb=nb, eType=gdal.GDT_Float32)
        self.assertIsInstance(ds, gdal.Dataset)
        from qps.utils import parseWavelength
        wl, wlu = parseWavelength(ds)
        self.assertIsInstance(wl, np.ndarray)
        self.assertIsInstance(wlu, str)

        self.assertEqual(ds.RasterCount, nb)
        self.assertEqual(ds.RasterXSize, ns)
        self.assertEqual(ds.RasterYSize, nl)
        self.assertEqual(ds.GetRasterBand(1).DataType, gdal.GDT_Float32)

        dsSrc = TestObjects.createRasterDataset(100, 100, 1)
        woptions = gdal.WarpOptions(dstSRS='EPSG:4326')
        pathDst = '/vsimem/warpDest.tif'
        dsDst = gdal.Warp(pathDst, dsSrc, options=woptions)
        self.assertIsInstance(dsDst, gdal.Dataset)

    def test_Speclibs(self):
        from qps.testing import TestObjects
        slib = TestObjects.createSpectralLibrary(7)
        self.assertIsInstance(slib, QgsVectorLayer)
        self.assertTrue(len(slib) == 7)


if __name__ == "__main__":
    unittest.main(buffer=False)
