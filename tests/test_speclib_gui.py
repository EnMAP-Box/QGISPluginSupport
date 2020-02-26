# -*- coding: utf-8 -*-

"""
***************************************************************************

    ---------------------
    Date                 : 30.11.2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin jakimow at geo dot hu-berlin dot de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming
import unittest
from qps.testing import TestObjects, TestCase, StartOptions


from qpstestdata import enmap, hymap
from qpstestdata import speclib as speclibpath

from qps.speclib.io.envi import *
from qps.speclib.io.asd import *
from qps.speclib.gui import *

TEST_DIR = os.path.join(os.path.dirname(__file__), 'temp')

class TestSpeclibWidgets(TestCase):


    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:
        os.makedirs(TEST_DIR, exist_ok=True)
        options = StartOptions.All

        super(TestSpeclibWidgets, cls).setUpClass(*args, options=options)

        from qps import initAll
        initAll()

        gdal.UseExceptions()
        gdal.PushErrorHandler(TestSpeclibWidgets.gdal_error_handler)
        ogr.UseExceptions()


    @staticmethod
    def gdal_error_handler(err_class, err_num, err_msg):
        errtype = {
            gdal.CE_None: 'None',
            gdal.CE_Debug: 'Debug',
            gdal.CE_Warning: 'Warning',
            gdal.CE_Failure: 'Failure',
            gdal.CE_Fatal: 'Fatal'
        }
        err_msg = err_msg.replace('\n', ' ')
        err_class = errtype.get(err_class, 'None')
        print('Error Number: %s' % (err_num))
        print('Error Type: %s' % (err_class))
        print('Error Message: %s' % (err_msg))


    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
        QApplication.processEvents()

    @classmethod
    def tearDownClass(cls):
        super(TestSpeclibWidgets, cls).tearDownClass()
        if os.path.isdir(TEST_DIR):
            import shutil
            shutil.rmtree(TEST_DIR)

    @unittest.skipIf(False, '')
    def test_PyQtGraphPlot(self):
        import qps.externals.pyqtgraph as pg
        #pg.systemInfo()

        plotWidget = pg.plot(title="Three plot curves")

        item1 = pg.PlotItem(x=[1,2,3],   y=[2, 3, 4], color='white')
        plotWidget.plotItem.addItem(item1)
        self.assertIsInstance(plotWidget, pg.PlotWidget)

        self.showGui(plotWidget)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPlotWidgetSimple(self):

        speclib = TestObjects.createSpectralLibrary(10)
        w = SpectralLibraryPlotWidget()
        w.setSpeclib(speclib)

        self.showGui(w)

    @unittest.skipIf(False, '')
    def test_SpectraLibraryPlotDataItem(self):

        sl = TestObjects.createSpectralLibrary(10)
        profile = sl[0]
        sp = SpectralProfilePlotDataItem(profile)

        plotStyle = defaultCurvePlotStyle()
        plotStyle.apply(sp)

        ps2 = PlotStyle.fromPlotDataItem(sp)

        self.assertEqual(plotStyle, ps2)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPlotWidget(self):

        speclib = SpectralLibrary.readFrom(speclibpath)

        pw = SpectralLibraryPlotWidget()
        self.assertIsInstance(pw, SpectralLibraryPlotWidget)
        self.assertTrue(pw.xUnit(), BAND_INDEX)

        p = speclib[0]
        sl = SpectralLibrary()
        sl.startEditing()
        pw.setSpeclib(sl)

        sl.addProfiles([p])
        self.assertTrue(pw.xUnit(), p.xUnit())


        w = QWidget()
        w.setLayout(QVBoxLayout())
        pw = SpectralLibraryPlotWidget()

        btn = QPushButton('Add speclib')
        btn.clicked.connect(lambda : pw.setSpeclib(speclib))
        w.layout().addWidget(pw)
        w.layout().addWidget(btn)


        self.assertIsInstance(pw.plotItem, pg.PlotItem)
        self.assertIsInstance(pw.plotItem.getViewBox(), SpectralViewBox)
        self.assertIsInstance(pw.plotItem.getAxis('bottom'), SpectralXAxis)



        plotItem = pw.getPlotItem()
        self.assertIsInstance(plotItem, pg.PlotItem)
        self.assertTrue(len(plotItem.dataItems) == 0)
        pw.setSpeclib(speclib)
        pw.updateSpectralProfilePlotItems()
        n = len([sp for sp in plotItem.dataItems if isinstance(sp, SpectralProfilePlotDataItem)])
        self.assertTrue(n == len(speclib))

        pw.setXUnit('nm')
        self.showGui(w)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPlotWidgetSimple(self):

        speclib = TestObjects.createSpectralLibrary(10)
        w = SpectralLibraryPlotWidget()
        w.setSpeclib(speclib)

        self.showGui(w)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPlotColorScheme(self):

        self.assertIsInstance(SpectralLibraryPlotColorScheme.default(), SpectralLibraryPlotColorScheme)
        self.assertIsInstance(SpectralLibraryPlotColorScheme.dark(), SpectralLibraryPlotColorScheme)
        self.assertIsInstance(SpectralLibraryPlotColorScheme.bright(), SpectralLibraryPlotColorScheme)
        self.assertIsInstance(SpectralLibraryPlotColorScheme.fromUserSettings(), SpectralLibraryPlotColorScheme)

        b = SpectralLibraryPlotColorScheme.bright()
        b.saveToUserSettings()
        self.assertEqual(b, SpectralLibraryPlotColorScheme.fromUserSettings())
        d = SpectralLibraryPlotColorScheme.default()
        d.saveToUserSettings()
        self.assertEqual(d, SpectralLibraryPlotColorScheme.fromUserSettings())

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPlotColorSchemeWidget(self):

        w = SpectralLibraryPlotColorSchemeWidget()
        self.assertIsInstance(w, SpectralLibraryPlotColorSchemeWidget)
        self.showGui(w)



    @unittest.skipIf(False, '')
    def test_SpectralProfileValueTableModel(self):

        speclib = TestObjects.createSpectralLibrary()
        p3 = speclib[2]
        self.assertIsInstance(p3, SpectralProfile)

        xUnit = p3.xUnit()
        yUnit = p3.yUnit()

        if yUnit is None:
            yUnit = '-'
        if xUnit is None:
            xUnit = '-'

        m = SpectralProfileValueTableModel()

        self.assertIsInstance(m, SpectralProfileValueTableModel)
        self.assertTrue(m.rowCount() == 0)
        self.assertTrue(m.columnCount() == 2)
        self.assertEqual('Y [-]', m.headerData(0, orientation=Qt.Horizontal, role=Qt.DisplayRole))
        self.assertEqual('X [-]', m.headerData(1, orientation=Qt.Horizontal, role=Qt.DisplayRole))

        m.setProfileData(p3)
        self.assertTrue(m.rowCount() == len(p3.xValues()))
        self.assertEqual('Y [{}]'.format(yUnit), m.headerData(0, orientation=Qt.Horizontal, role=Qt.DisplayRole))
        self.assertEqual('X [{}]'.format(xUnit), m.headerData(1, orientation=Qt.Horizontal, role=Qt.DisplayRole))

        m.setColumnValueUnit(0, '')


    @unittest.skipIf(False, '')
    def test_SpectralProfileEditorWidget(self):

        import qps
        qps.initResources()

        self.assertIsInstance(QgsApplication.instance(), QgsApplication)
        SLIB = TestObjects.createSpectralLibrary()
        self.assertIsInstance(SLIB, SpectralLibrary)
        w = SpectralProfileEditorWidget()
        self.assertIsInstance(w, QWidget)

        p = SLIB[-1]
        w.setProfileValues(p)

        self.showGui(w)
        self.assertTrue(True)

    @unittest.skipIf(False, '')
    def test_toolbarStackedActions(self):

        tb = QToolBar()
        a1 = tb.addAction('Action1')
        a2 = tb.addAction('ActionA2')

        a21 = QAction('A2.1')
        a22 = QAction('A2.2')
        a22.setCheckable(True)

        setToolButtonDefaultActionMenu(a2, [a21, a22])


        btn2 = tb.findChildren(QToolButton)[2]
        self.assertIsInstance(btn2, QToolButton)

        self.showGui(tb)

    @unittest.skipIf(False, '')
    def test_SpectralProfileEditorWidgetFactory(self):


        reg = QgsGui.editorWidgetRegistry()
        if len(reg.factories()) == 0:
            reg.initEditors()


        registerSpectralProfileEditorWidget()

        self.assertTrue(EDITOR_WIDGET_REGISTRY_KEY in reg.factories().keys())
        factory = reg.factories()[EDITOR_WIDGET_REGISTRY_KEY]
        self.assertIsInstance(factory, SpectralProfileEditorWidgetFactory)

        vl = TestObjects.createSpectralLibrary()

        am = vl.actions()
        self.assertIsInstance(am, QgsActionManager)

        c = QgsMapCanvas()
        w = QWidget()
        w.setLayout(QVBoxLayout())

        print('STOP 1', flush=True)
        dv = QgsDualView()
        print('STOP 2', flush=True)
        dv.init(vl, c)
        print('STOP 3', flush=True)
        dv.setView(QgsDualView.AttributeTable)
        print('STOP 4', flush=True)
        dv.setAttributeTableConfig(vl.attributeTableConfig())
        print('STOP 5', flush=True)
        cb = QCheckBox()
        cb.setText('Show Editor')

        def onClicked(b:bool):
            if b:
                dv.setView(QgsDualView.AttributeEditor)
            else:
                dv.setView(QgsDualView.AttributeTable)
        cb.clicked.connect(onClicked)
        w.layout().addWidget(dv)
        w.layout().addWidget(cb)

        w.resize(QSize(300, 250))
        print(vl.fields().names())
        look = vl.fields().lookupField
        print('STOP 4', flush=True)
        parent = QWidget()
        configWidget = factory.configWidget(vl, look(FIELD_VALUES), None)
        self.assertIsInstance(configWidget, SpectralProfileEditorConfigWidget)

        self.assertIsInstance(factory.createSearchWidget(vl, 0, dv), QgsSearchWidgetWrapper)

        eww = factory.create(vl, 0, None, dv )
        self.assertIsInstance(eww, SpectralProfileEditorWidgetWrapper)
        self.assertIsInstance(eww.widget(), SpectralProfileEditorWidget)

        eww.valueChanged.connect(lambda v: print('value changed: {}'.format(v)))

        fields = vl.fields()
        vl.startEditing()
        value = eww.value()
        f = vl.getFeature(1)
        self.assertTrue(vl.updateFeature(f))

        self.showGui([w, configWidget])

    @unittest.skipIf(False, '')
    def test_SpectralLibraryWidget_ClassFields(self):
        from qps import registerEditorWidgets
        registerEditorWidgets()
        w = SpectralLibraryWidget()
        from qpstestdata import speclib_labeled
        sl = SpectralLibrary.readFrom(speclib_labeled)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl) > 0)
        w.addSpeclib(sl)
        self.showGui(w)


    @unittest.skipIf(False, '')
    def test_SpectralLibraryWidget(self):

        from qpstestdata import enmap, landcover, enmap_pixel

        l1 = QgsRasterLayer(enmap, 'EnMAP')
        l2 = QgsVectorLayer(landcover, 'LandCover')
        l3 = QgsVectorLayer(enmap_pixel, 'Points of Interest')
        QgsProject.instance().addMapLayers([l1, l2, l3])

        pd = QProgressDialog()
        speclib = SpectralLibrary.readFrom(speclibpath, progressDialog=pd)
        slw = SpectralLibraryWidget(speclib=speclib)
        pd.close()
        QgsProject.instance().addMapLayer(slw.speclib())

        self.assertEqual(slw.speclib(), speclib)
        self.assertIsInstance(slw.speclib(), SpectralLibrary)
        fieldNames = slw.speclib().fieldNames()
        self.assertIsInstance(fieldNames, list)

        for mode in list(SpectralLibraryWidget.CurrentProfilesMode):
            assert isinstance(mode, SpectralLibraryWidget.CurrentProfilesMode)
            slw.setCurrentProfilesMode(mode)
            assert slw.currentProfilesMode() == mode

        cs = [speclib[0], speclib[3], speclib[-1]]
        l = len(speclib)
        self.assertTrue(slw.speclib() == speclib)

        self.assertTrue(len(slw.currentSpectra()) == 0)
        slw.setCurrentProfilesMode(SpectralLibraryWidget.CurrentProfilesMode.block)
        slw.setCurrentSpectra(cs)
        self.assertTrue(len(slw.currentSpectra()) == 0)

        slw.setCurrentProfilesMode(SpectralLibraryWidget.CurrentProfilesMode.automatically)
        slw.setCurrentSpectra(cs)
        self.assertTrue(len(slw.currentSpectra()) == 0)

        slw.setCurrentProfilesMode(SpectralLibraryWidget.CurrentProfilesMode.normal)
        slw.setCurrentSpectra(cs)
        self.assertTrue(len(slw.currentSpectra()) == 3)

        speclib.selectByIds([1, 2, 3])

        n = len(speclib)
        sids = speclib.selectedFeatureIds()

        self.assertTrue(len(sids) > 0)
        slw.copySelectedFeatures()
        slw.cutSelectedFeatures()
        slw.pasteFeatures()

        self.assertEqual(n, len(speclib))



        self.showGui(slw)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPanel(self):

        sp = SpectralLibraryPanel()
        self.showGui(sp)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryWidgetCanvas(self):

        # speclib = self.createSpeclib()

        lyr = QgsRasterLayer(hymap)
        h, w = lyr.height(), lyr.width()
        speclib = SpectralLibrary.readFromRasterPositions(enmap, [QPoint(0,0), QPoint(w-1, h-1), QPoint(2, 2)])
        slw = SpectralLibraryWidget(speclib=speclib)


        QgsProject.instance().addMapLayers([lyr, slw.speclib()])

        canvas = QgsMapCanvas()

        canvas.setLayers([lyr, slw.speclib()])
        canvas.setDestinationCrs(slw.speclib().crs())
        canvas.setExtent(slw.speclib().extent())


        def setLayers():
            canvas.mapSettings().setDestinationCrs(slw.mCanvas.mapSettings().destinationCrs())
            canvas.setExtent(slw.canvas().extent())
            canvas.setLayers(slw.canvas().layers())

        slw.sigMapCenterRequested.connect(setLayers)
        slw.sigMapExtentRequested.connect(setLayers)

        self.showGui([canvas, slw])

    @unittest.skipIf(False, '')
    def test_editing(self):

        slib = TestObjects.createSpectralLibrary()
        self.assertTrue(len(slib) > 0)
        slw = SpectralLibraryWidget()
        slw.speclib().startEditing()
        slw.speclib().addSpeclib(slib)

        slw.actionToggleEditing.setChecked(True)

        #self.assertTrue()
        self.showGui(slw)

    @unittest.skipIf(False, '')
    def test_speclibAttributeWidgets(self):

        import qps
        qps.registerEditorWidgets()
        speclib = TestObjects.createSpectralLibrary()


        slw = SpectralLibraryWidget(speclib=speclib)

        import qps.layerproperties
        propertiesDialog = qps.layerproperties.LayerPropertiesDialog(speclib, None)
        self.assertIsInstance(propertiesDialog, QgsOptionsDialogBase)
        self.showGui([slw, propertiesDialog])



    @unittest.skipIf(False, '')
    def test_SpectralLibraryWidgetThousands(self):

        import qpstestdata

        pathSL = os.path.join(os.path.dirname(qpstestdata.__file__), 'roberts2017_urban.sli')

        if True and os.path.exists(pathSL):
            t0 = datetime.datetime.now()
            speclib = SpectralLibrary.readFrom(pathSL)

            dt = datetime.datetime.now() - t0
            print('Reading required : {}'.format(dt))
        else:
            speclib = TestObjects.createSpectralLibrary(5000)

        t0 = datetime.datetime.now()

        w = SpectralLibraryWidget()

        w.addSpeclib(speclib)
        dt = datetime.datetime.now() - t0
        print('Adding speclib required : {}'.format(dt))

        self.showGui(w)






    def test_speclibImportSpeed(self):

        pathRaster = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapboxtestdata\enmap_berlin.bsq'
        # pathPoly = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapboxtestdata\landcover_berlin_polygon.shp'
        pathPoly = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapboxtestdata\landcover_berlin_point.shp'

        for p in [pathRaster, pathPoly]:
            if not os.path.isfile(p):
                return

        progressDialog = QProgressDialog()
        # progressDialog.show()
        vl = QgsVectorLayer(pathPoly)
        vl.setName('Polygons')
        rl = QgsRasterLayer(pathRaster)
        rl.setName('Raster Data')
        if not vl.isValid() and rl.isValid():
            return

        max_spp = 1  # seconds per profile

        def timestats(t0, sl, info='time'):
            dt = time.time() - t0
            spp = dt / len(sl)
            pps = len(sl) / dt
            print('{}: dt={}sec spp={} pps={}'.format(info, dt, spp, pps))
            return dt, spp, pps

        t0 = time.time()
        sl = SpectralLibrary.readFromVector(vl, rl, progressDialog=progressDialog)
        dt, spp, pps = timestats(t0, sl, info='read profiles')
        self.assertTrue(spp <= max_spp, msg='{} seconds per profile are too much!')

        self.assertTrue(progressDialog.value() == -1)
        t0 = time.time()
        sl.startEditing()
        sl.addSpeclib(sl)
        sl.commitChanges()
        dt, spp, pps = timestats(t0, sl, info='merge speclibs')
        self.assertTrue(spp <= max_spp, msg='too slow!')

        sl0 = SpectralLibrary()
        t0 = time.time()
        sl0.startEditing()
        sl0.addSpeclib(sl)
        dt, spp, pps = timestats(t0, sl, info='merge speclibs2')
        self.assertTrue(spp <= max_spp, msg='too slow!')

        w = SpectralLibraryWidget()

        t0 = time.time()
        w.addSpeclib(sl)

        dt = time.time() - t0

        QgsProject.instance().addMapLayers([vl, rl])
        w = SpectralLibraryWidget()
        self.showGui(w)



    def test_SpectralProfileImportPointsDialog(self):

        lyrRaster = QgsRasterLayer(enmap)
        lyrRaster.setName('EnMAP')
        h, w = lyrRaster.height(), lyrRaster.width()

        pxPositions = [QPoint(0, 0), QPoint(w - 1, h - 1)]

        speclib1 = SpectralLibrary.readFromRasterPositions(enmap, pxPositions)
        speclib1.setName('Extracted Spectra')
        self.assertIsInstance(speclib1, SpectralLibrary)
        self.assertTrue(len(speclib1) > 0)

        vl1 = TestObjects.createVectorLayer(QgsWkbTypes.Polygon)
        vl2 = TestObjects.createVectorLayer(QgsWkbTypes.LineGeometry)
        vl3 = TestObjects.createVectorLayer(QgsWkbTypes.Point)

        layers = [speclib1, vl1, vl2, vl3]
        layers = [speclib1]

        QgsProject.instance().addMapLayers(layers)
        from qps.speclib.io.rastersources import SpectralProfileImportPointsDialog

        def onFinished(code):
            self.assertTrue(code in [QDialog.Accepted, QDialog.Rejected])

            if code == QDialog.Accepted:
                slib = d.speclib()
                self.assertTrue(d.isFinished())
                self.assertIsInstance(slib, SpectralLibrary)
                self.assertIsInstance(d.profiles(), list)
                self.assertTrue(len(d.profiles()) == len(slib))
                print('Returned {} profiles from {} and {}'.format(len(slib), d.vectorSource().source(), d.rasterSource().source()))


        for vl in layers:
            d = SpectralProfileImportPointsDialog()
            self.assertIsInstance(d, SpectralProfileImportPointsDialog)
            d.setRasterSource(lyrRaster)
            d.setVectorSource(vl)
            d.show()
            self.assertEqual(lyrRaster, d.rasterSource())
            self.assertEqual(vl, d.vectorSource())

            d.finished.connect(onFinished)
            d.run()
            while not d.isFinished():
                QApplication.processEvents()
            d.hide()
            d.close()


        #self.showGui(d)


    def test_AttributeDialog(self):

        SLIB = TestObjects.createSpectralLibrary()
        d = AddAttributeDialog(SLIB)
        self.showGui(d)

    def test_SpectralLibraryWidgetProgressDialog(self):

        slib = TestObjects.createSpectralLibrary(3000)
        self.assertIsInstance(slib, SpectralLibrary)
        self.assertTrue(slib.isValid())

    def test_SpectralLibraryWidgetCurrentProfilOverlayerXUnit(self):

        sw = SpectralLibraryWidget()
        self.assertIsInstance(sw, SpectralLibraryWidget)
        pw = sw.plotWidget()
        self.assertIsInstance(pw, SpectralLibraryPlotWidget)
        self.assertEqual(pw.xUnit(), BAND_INDEX)
        slib = TestObjects.createSpectralLibrary(10)

        xunits = []
        for p in slib:
            self.assertIsInstance(p, SpectralProfile)
            u = p.xUnit()
            if u not in xunits:
                xunits.append(u)

        sw = SpectralLibraryWidget(speclib=slib)
        self.assertEqual(sw.speclib(), slib)
        sw.applyAllPlotUpdates()

        sw = SpectralLibraryWidget()
        sp = slib[0]
        sw.setCurrentProfiles([sp])
        sw.applyAllPlotUpdates()

if __name__ == '__main__':

    unittest.main()


