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
import xmlrunner

from qps.speclib.gui.spectrallibrarywidget import SpectralLibraryWidget
from qps.testing import TestObjects, TestCase

from qpstestdata import enmap, landcover
from qpstestdata import speclib as speclibpath

from qps.speclib.io.vectorsources import *
from qps.speclib.io.csvdata import *
from qps.speclib.io.envi import *
from qps.speclib.io.rastersources import *

from qps.utils import *
TEST_DIR = os.path.join(os.path.dirname(__file__), 'temp')


class TestIO(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:
        os.makedirs(TEST_DIR, exist_ok=True)
        super(TestIO, cls).setUpClass(*args, **kwds)

    @classmethod
    def tearDownClass(cls):
        super(TestIO, cls).tearDownClass()
        if os.path.isdir(TEST_DIR):
            import shutil
            shutil.rmtree(TEST_DIR)

    def setUp(self):
        super().setUp()
        QgsProject.instance().removeMapLayers(QgsProject.instance().mapLayers().keys())


    def test_VSI(self):

        slib1 = TestObjects.createSpectralLibrary()
        path = slib1.source()
        feedback = self.createProcessingFeedback()
        slib2 = SpectralLibrary.readFrom(path, feedback=feedback)
        self.assertIsInstance(slib2, SpectralLibrary)
        self.assertEqual(slib1, slib2)
        s = ""

    def test_jsonIO(self):

        slib = TestObjects.createSpectralLibrary()
        pathJSON = tempfile.mktemp(suffix='.json', prefix='tmpSpeclib')

        # no additional info, no JSON file
        # slib.writeJSONProperties(pathJSON)
        # self.assertFalse(os.path.isfile(pathJSON))

        # add categorical info
        slib.startEditing()
        slib.addAttribute(QgsField('class1', QVariant.String, 'varchar'))
        slib.addAttribute(QgsField('class2', QVariant.Int, 'int'))
        slib.commitChanges()
        slib.startEditing()

        from qps.classification.classificationscheme import ClassificationScheme, ClassInfo, EDITOR_WIDGET_REGISTRY_KEY, \
            classSchemeToConfig

        cs = ClassificationScheme()
        cs.insertClass(ClassInfo(name='unclassified'))
        cs.insertClass(ClassInfo(name='class a', color=QColor('red')))
        cs.insertClass(ClassInfo(name='class b', color=QColor('blue')))

        idx1 = slib.fields().lookupField('class1')
        idx2 = slib.fields().lookupField('class2')

        config = classSchemeToConfig(cs)
        setup1 = QgsEditorWidgetSetup(EDITOR_WIDGET_REGISTRY_KEY, config)
        setup2 = QgsEditorWidgetSetup(EDITOR_WIDGET_REGISTRY_KEY, config)
        slib.setEditorWidgetSetup(idx1, setup1)
        slib.setEditorWidgetSetup(idx2, setup2)

        slib.setEditorWidgetSetup(idx1, QgsEditorWidgetSetup('', {}))
        slib.setEditorWidgetSetup(idx2, QgsEditorWidgetSetup('', {}))
        data = slib.readJSONProperties(pathJSON)
        s = ""

    def test_readFromVector(self):

        from qpstestdata import enmap_pixel, landcover, enmap

        rl = QgsRasterLayer(enmap)
        vl = QgsVectorLayer(enmap_pixel)

        progressDialog = QProgressDialog()
        # progress_handler.show()

        info = 'Test read from \n' + \
               'Vector: {}\n'.format(vl.crs().description()) + \
               'Raster: {}\n'.format(rl.crs().description())
        print(info)

        sl = SpectralLibrary.readFromVector(vl, rl,
                                            all_touched=True,
                                            copy_attributes=True)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl) > 0, msg='Failed to read SpectralProfiles')
        n_pr = len(sl)
        n_px = rl.width() * rl.height()
        self.assertEqual(n_px, n_pr, msg=f'Expected {n_px} profiles but got {n_pr}')

        self.assertTrue(progressDialog.value(), [-1, progressDialog.maximum()])

        data = gdal.Open(enmap).ReadAsArray()
        nb, nl, ns = data.shape

        for p in sl:
            self.assertIsInstance(p, SpectralProfile)

            x = p.attribute('px_x')
            y = p.attribute('px_y')
            yValues = p.values()['y']
            yValues2 = list(data[:, y, x])
            self.assertListEqual(yValues, yValues2)
            s = ""

        # self.assertTrue(sl.crs() != vl.crs())

        info = 'Test read from \n' + \
               'Vector: {} (speclib)\n'.format(sl.crs().description()) + \
               'Raster: {}\n'.format(rl.crs().description())
        print(info)

        sl2 = SpectralLibrary.readFromVector(sl, rl, copy_attributes=True)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl2) > 0, msg='Failed to re-read SpectralProfiles')
        for p1, p2 in zip(sl[:], sl2[:]):
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            self.assertTrue(p1.geometry().equals(p2.geometry()))
            self.assertListEqual(p1.yValues(), p2.yValues())

        rl = QgsRasterLayer(enmap)
        vl = QgsVectorLayer(landcover)
        sl = SpectralLibrary.readFromVector(vl, rl)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl) > 0)

    def test_CSV2(self):
        from qpstestdata import speclib
        from qps.speclib.io.csvdata import CSVSpectralLibraryIO
        feedback = self.createProcessingFeedback()
        SLIB = SpectralLibrary.readFrom(speclib, feedback=feedback)
        pathCSV = tempfile.mktemp(suffix='.csv', prefix='tmpSpeclib')

        CSVSpectralLibraryIO.write(SLIB, pathCSV, feedback=feedback)

        self.assertTrue(os.path.isfile(pathCSV))
        dialect = CSVSpectralLibraryIO.canRead(pathCSV)
        self.assertTrue(dialect is not None)
        speclib2 = CSVSpectralLibraryIO.readFrom(pathCSV, dialect=dialect, feedback=feedback)
        self.assertTrue(len(SLIB) == len(speclib2))
        for i, (p1, p2) in enumerate(zip(SLIB[:], speclib2[:])):
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            if p1 != p2:
                s = ""
            self.assertEqual(p1, p2)

        SLIB = TestObjects.createSpectralLibrary()
        # pathCSV = os.data_source.join(os.data_source.dirname(__file__), 'speclibcvs2.out.csv')
        pathCSV = tempfile.mktemp(suffix='.csv', prefix='tmpSpeclib')
        print(pathCSV)
        CSVSpectralLibraryIO.write(SLIB, pathCSV, feedback=feedback)

        self.assertTrue(os.path.isfile(pathCSV))
        dialect = CSVSpectralLibraryIO.canRead(pathCSV)
        self.assertTrue(dialect is not None)
        speclib2 = CSVSpectralLibraryIO.readFrom(pathCSV, dialect=dialect, feedback=feedback)
        self.assertTrue(len(SLIB) == len(speclib2))
        for i, (p1, p2) in enumerate(zip(SLIB[:], speclib2[:])):
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            self.assertEqual(p1.xValues(), p2.xValues())
            self.assertEqual(p1.yValues(), p2.yValues())
            if p1 != p2:
                s = ""
            self.assertEqual(p1, p2)

        # self.assertEqual(SLIB, speclib2)

        # addresses issue #8
        from qpstestdata import speclib
        SL1 = SpectralLibrary.readFrom(speclib, feedback=feedback)
        self.assertIsInstance(SL1, SpectralLibrary)

        pathCSV = tempfile.mktemp(suffix='.csv', prefix='tmpSpeclib')
        print(pathCSV)
        for dialect in [pycsv.excel_tab, pycsv.excel]:
            pathCSV = tempfile.mktemp(suffix='.csv', prefix='tmpSpeclib')
            CSVSpectralLibraryIO.write(SL1, pathCSV, dialect=dialect, feedback=feedback)
            d = CSVSpectralLibraryIO.canRead(pathCSV)
            self.assertEqual(d, dialect)
            SL2 = CSVSpectralLibraryIO.readFrom(pathCSV, dialect=dialect, feedback=feedback)
            self.assertIsInstance(SL2, SpectralLibrary)
            self.assertTrue(len(SL1) == len(SL2))

            for p1, p2 in zip(SL1[:], SL2[:]):
                self.assertIsInstance(p1, SpectralProfile)
                self.assertIsInstance(p2, SpectralProfile)
                if p1 != p2:
                    s = ""
                self.assertEqual(p1, p2)

        # addresses issue #8 loading modified CSV values

        SL = SpectralLibrary.readFrom(speclib, feedback=feedback)

        pathCSV = tempfile.mktemp(suffix='.csv', prefix='tmpSpeclib')
        CSVSpectralLibraryIO.write(SL, pathCSV, feedback=feedback)

        with open(pathCSV, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # change band values of b1 and b3

        WKT = None
        delimiter = '\t'
        for i in range(len(lines)):
            line = lines[i]
            if line.strip() in ['']:
                continue
            if line.startswith('#'):
                continue

            if line.startswith('WKT'):
                WKT = line.split(delimiter)
                continue

            parts = line.split(delimiter)
            parts[WKT.index('b1')] = '42.0'
            parts[WKT.index('b100')] = '42'
            line = delimiter.join(parts)
            lines[i] = line

        with open(pathCSV, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        SL2 = CSVSpectralLibraryIO.readFrom(pathCSV, feedback=feedback)

        self.assertEqual(len(SL), len(SL2))

        for p in SL2:
            self.assertIsInstance(p, SpectralProfile)
            self.assertEqual(p.yValues()[0], 42)
            self.assertEqual(p.yValues()[99], 42)

    def test_vector2speclib(self):

        lyrRaster = QgsRasterLayer(enmap)
        h, w = lyrRaster.height(), lyrRaster.width()

        factor = [0, 0.5, 1.]
        pxPositions = []

        for x in factor:
            for y in factor:
                pxPositions.append(QPoint(int(x * (w - 1)), int(y * (h - 1))))

        speclib1 = SpectralLibrary.readFromRasterPositions(enmap, pxPositions)

        ds = gdal.Open(enmap)
        data = ds.ReadAsArray()
        for i, px in enumerate(pxPositions):
            vector = data[:, px.y(), px.x()]

            profile = speclib1[i]

            self.assertIsInstance(profile, SpectralProfile)
            vector2 = profile.yValues()
            self.assertListEqual(list(vector), vector2)

        progress = QProgressDialog()

        speclib2 = SpectralLibrary.readFromVector(speclib1, lyrRaster, progress_handler=progress)
        self.assertIsInstance(speclib2, SpectralLibrary)
        self.assertEqual(len(speclib1), len(speclib2))
        self.assertTrue(speclib1.crs().toWkt() == speclib2.crs().toWkt())

        profiles1 = sorted(speclib1[:], key=lambda f: f.id())
        profiles2 = sorted(speclib2[:], key=lambda f: f.id())

        for p1, p2 in zip(profiles1, profiles2):
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            self.assertListEqual(p1.yValues(), p2.yValues())
            self.assertTrue(p1.geometry().equals(p2.geometry()))

        vlLandCover = QgsVectorLayer(landcover)
        rlEnMAP = QgsRasterLayer(enmap)
        speclib3 = SpectralLibrary.readFromVector(vlLandCover, rlEnMAP, progress_handler=progress)

        self.assertIsInstance(speclib3, SpectralLibrary)
        self.assertTrue(len(speclib3) > 0)

        speclib4 = SpectralLibrary.readFromVector(vlLandCover, rlEnMAP, copy_attributes=True, progress_handler=progress)
        self.assertIsInstance(speclib3, SpectralLibrary)
        self.assertTrue(len(speclib3) > 0)
        self.assertTrue(len(speclib3.fieldNames()) < len(speclib4.fieldNames()))

        namesSL = [n.lower() for n in speclib4.fieldNames()]
        for fieldName in vlLandCover.fields().names():
            self.assertTrue(fieldName.lower() in namesSL)

    def test_reloadProfiles(self):
        lyr = QgsRasterLayer(enmap)
        QgsProject.instance().addMapLayer(lyr)
        lyr.setName('ENMAP')
        self.assertIsInstance(lyr, QgsRasterLayer)
        locations = []
        for x in range(lyr.width()):
            for y in range(lyr.height()):
                locations.append(QPoint(x, y))

        print('load speclibA', flush=True)
        speclibA = SpectralLibrary.readFromRasterPositions(lyr.source(), locations)
        self.assertIsInstance(speclibA, SpectralLibrary)

        print('load speclibREF', flush=True)
        speclibREF = SpectralLibrary.readFromRasterPositions(lyr.source(), locations)
        self.assertIsInstance(speclibREF, SpectralLibrary)
        speclibREF.setName('REF SPECLIB')
        self.assertIsInstance(speclibA, SpectralLibrary)
        self.assertTrue(len(locations) == len(speclibA))

        self.assertFalse(speclibA.isEditable())
        print('speclibA is editable', flush=True)

        # clean values
        self.assertTrue(speclibA.startEditing())
        idx = speclibA.fields().indexOf(FIELD_VALUES)

        n = 0
        for p in speclibA:
            n += 1
            # if n > 10:
            #    break
            print('Change attribute values profile {}'.format(p.id()), flush=True)
            self.assertIsInstance(p, SpectralProfile)
            speclibA.changeAttributeValue(p.id(), idx, None)
            QApplication.processEvents()

        print('Commit changes', flush=True)
        self.assertTrue(speclibA.commitChanges())

        print('Check yValues(', flush=True)

        for p in speclibA:
            self.assertIsInstance(p, SpectralProfile)
            self.assertListEqual(p.yValues(), [])
            QApplication.processEvents()

        QApplication.processEvents()
        # re-read values
        print('select all', flush=True)
        speclibA.selectAll()
        print('start editing', flush=True)
        speclibA.startEditing()
        QApplication.processEvents()
        print('reload spectral values', flush=True)
        speclibA.reloadSpectralValues(enmap)
        self.assertTrue(speclibA.commitChanges())

        print('Compare speclibA with speclibREF', flush=True)
        for a, b in zip(speclibA[:], speclibREF[:]):
            self.assertIsInstance(a, SpectralProfile)
            self.assertIsInstance(b, SpectralProfile)
            self.assertListEqual(a.xValues(), b.xValues())
            self.assertListEqual(a.yValues(), b.yValues())

        print('load SpectralLibraryWidget', flush=True)
        slw = SpectralLibraryWidget(speclib=speclibA)
        QApplication.processEvents()

        # clean values
        speclibA.startEditing()
        idx = speclibA.fields().indexOf(FIELD_VALUES)
        speclibA.beginEditCommand('Reset profile values')
        for p in speclibA:
            self.assertIsInstance(p, SpectralProfile)
            speclibA.changeAttributeValue(p.id(), idx, None)
        speclibA.endEditCommand()
        self.assertTrue(speclibA.commitChanges())
        QApplication.processEvents()
        self.showGui(slw)

    def test_EcoSIS(self):

        feedback = QgsProcessingFeedback()

        from qps.speclib.io.ecosis import EcoSISSpectralLibraryIO
        from qpstestdata import speclib
        self.assertFalse(EcoSISSpectralLibraryIO.canRead(speclib))

        # 1. read
        from qpstestdata import DIR_ECOSIS
        for path in file_search(DIR_ECOSIS, '*.csv'):
            print('Read {}...'.format(path))
            self.assertTrue(EcoSISSpectralLibraryIO.canRead(path), msg='Unable to read {}'.format(path))
            sl = EcoSISSpectralLibraryIO.readFrom(path, feedback=feedback)
            self.assertIsInstance(sl, SpectralLibrary)
            self.assertTrue(len(sl) > 0)

        # 2. write
        speclib = TestObjects.createSpectralLibrary(50)

        # remove x/y values from first profile. this profile should be skipped in the outputs
        p0 = speclib[0]
        self.assertIsInstance(p0, SpectralProfile)
        p0.setValues(x=[], y=[])
        speclib.startEditing()
        speclib.updateFeature(p0)
        self.assertTrue(speclib.commitChanges())

        pathCSV = os.path.join(TEST_DIR, 'speclib.ecosys.csv')
        csvFiles = EcoSISSpectralLibraryIO.write(speclib, pathCSV, feedback=QProgressDialog())
        csvFiles = EcoSISSpectralLibraryIO.write(speclib, pathCSV, feedback=None)
        n = 0
        for p in csvFiles:
            self.assertTrue(os.path.isfile(p))
            self.assertTrue(EcoSISSpectralLibraryIO.canRead(p))

            slPart = EcoSISSpectralLibraryIO.readFrom(p, feedback=QProgressDialog())
            self.assertIsInstance(slPart, SpectralLibrary)

            n += len(slPart)

        self.assertEqual(len(speclib) - 1, n)

    def test_SPECCHIO(self):

        from qps.speclib.io.specchio import SPECCHIOSpectralLibraryIO

        # 1. read
        from qpstestdata import DIR_SPECCHIO
        for path in reversed(list(file_search(DIR_SPECCHIO, '*.csv'))):

            self.assertTrue(SPECCHIOSpectralLibraryIO.canRead(path))
            sl = SPECCHIOSpectralLibraryIO.readFrom(path, feedback=QProgressDialog())
            self.assertIsInstance(sl, SpectralLibrary)
            self.assertTrue(len(sl) > 0)
            for p in sl:
                self.assertIsInstance(p, SpectralProfile)
                self.assertListEqual(p.xValues(), sorted(p.xValues()))
        # 2. write
        speclib = TestObjects.createSpectralLibrary(50, n_empty=1)
        pathCSV = os.path.join(TEST_DIR, 'speclib.specchio.csv')
        csvFiles = SPECCHIOSpectralLibraryIO.write(speclib, pathCSV, feedback=QProgressDialog())

        n = 0
        for p in csvFiles:
            self.assertTrue(os.path.isfile(p))
            self.assertTrue(SPECCHIOSpectralLibraryIO.canRead(p))

            slPart = SPECCHIOSpectralLibraryIO.readFrom(p, feedback=QProgressDialog())
            self.assertIsInstance(slPart, SpectralLibrary)
            for p in slPart:
                self.assertIsInstance(p, SpectralProfile)
                self.assertListEqual(p.xValues(), sorted(p.xValues()))

            n += len(slPart)

        self.assertEqual(len(speclib) - 1, n)

    def test_ADS_AS7(self):

        # read binary files
        from qps.speclib.io.asd import ASDSpectralLibraryIO, ASDBinaryFile
        from qpstestdata import DIR_ASD_AS7
        binaryFiles = list(file_search(DIR_ASD_AS7, '*.asd'))
        for path in binaryFiles:
            self.assertTrue(ASDSpectralLibraryIO.canRead(path))
            asdFile = ASDBinaryFile().readFromBinaryFile(path)
            self.assertIsInstance(asdFile, ASDBinaryFile)

    def test_ASD(self):

        # read binary files
        from qps.speclib.io.asd import ASDSpectralLibraryIO, ASDBinaryFile
        from qpstestdata import DIR_ASD_BIN, DIR_ASD_TXT

        binaryFiles = list(file_search(DIR_ASD_BIN, '*.asd'))
        pd = QProgressDialog()
        for path in binaryFiles:
            self.assertTrue(ASDSpectralLibraryIO.canRead(path))
            asdFile = ASDBinaryFile().readFromBinaryFile(path)

            self.assertIsInstance(asdFile, ASDBinaryFile)

            sl = ASDSpectralLibraryIO.readFrom(path, feedback=pd)
            self.assertIsInstance(sl, SpectralLibrary)
            self.assertEqual(len(sl), 1)

        sl = ASDSpectralLibraryIO.readFrom(binaryFiles, feedback=pd)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertEqual(len(sl), len(binaryFiles))

        textFiles = list(file_search(DIR_ASD_TXT, '*.asd.txt'))
        for path in textFiles:
            self.assertTrue(ASDSpectralLibraryIO.canRead(path))

            sl = ASDSpectralLibraryIO.readFrom(path, feedback=pd)
            self.assertIsInstance(sl, SpectralLibrary)
            self.assertEqual(len(sl), 1)

        sl = ASDSpectralLibraryIO.readFrom(textFiles, feedback=pd)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertEqual(len(sl), len(textFiles))

    def test_speclib2vector(self):

        testDir = self.createTestOutputDirectory() / 'speclib2vector'
        os.makedirs(testDir, exist_ok=True)

        from qps.speclib.io.vectorsources import VectorSourceSpectralLibraryIO

        slib = TestObjects.createSpectralLibrary(2, n_bands=[-1, 3, 24])
        self.assertIsInstance(slib, SpectralLibrary)
        self.assertTrue(len(slib) == 6)

        extensions = ['.json', '.geojson', '.geojsonl', '.csv', '.gpkg']

        hasLIBKML = isinstance(ogr.GetDriverByName('LIBKML'), ogr.Driver)
        if hasLIBKML:
            extensions.append('.kml')

        for ext in extensions:
            print('Test vector file type {}'.format(ext))
            path = testDir / f'speclib_{ext[1:]}{ext}'

            if ext == '.kml':
                s = ""

            # write
            writtenFiles = VectorSourceSpectralLibraryIO.write(slib, path, feedback=QProgressDialog())
            self.assertTrue(len(writtenFiles) == 1)


            # read
            file = writtenFiles[0]
            self.assertTrue(VectorSourceSpectralLibraryIO.canRead(file),
                            msg='Failed to read speclib from {}'.format(file))
            sl = VectorSourceSpectralLibraryIO.readFrom(file, feedback=QProgressDialog())
            self.assertIsInstance(sl, SpectralLibrary)
            self.assertEqual(len(sl), len(slib))

            for p1, p2 in zip(slib[:], sl[:]):
                self.assertIsInstance(p1, SpectralProfile)
                self.assertIsInstance(p2, SpectralProfile)
                self.assertEqual(p1.name(), p2.name())
                self.assertEqual(p1.xUnit(), p2.xUnit())
                self.assertEqual(p1.yUnit(), p2.yUnit())
                self.assertListEqual(p1.xValues(), p2.xValues())
                self.assertListEqual(p1.yValues(), p2.yValues())

    def test_AbstractSpectralLibraryIOs(self):
        """
        A generic test to check all AbstractSpectralLibraryIO implementations
        """
        slib = TestObjects.createSpectralLibrary()

        nFeatures = len(slib)
        nProfiles = 0
        for p in slib:
            if len(p.yValues()) > 0:
                nProfiles += 1

        for ioClass in allSubclasses(SpectralLibraryIO):
            print('Test {}'.format(ioClass.__name__))
            c = ioClass()
            path = tempfile.mktemp(suffix='.csv', prefix='tmpSpeclib')
            feedback = self.createProcessingFeedback()
            writtenFiles = c.write(slib, path, feedback=feedback)

            # if it can write, it should read the profiles too
            if len(writtenFiles) > 0:
                feedback = self.createProcessingFeedback()
                n = 0
                for path in writtenFiles:
                    self.assertTrue(os.path.isfile(path), msg='Failed to write file. {}'.format(c))
                    sl = c.readFrom(path, feedback=feedback)
                    self.assertIsInstance(sl, SpectralLibrary)
                    n += len(sl)

                self.assertTrue(n == nProfiles or n == nFeatures)

    def test_ARTMO(self):

        from qpstestdata import DIR_ARTMO

        p = os.path.join(DIR_ARTMO, 'directional_reflectance.txt')

        from qps.speclib.io.artmo import ARTMOSpectralLibraryIO

        self.assertTrue(ARTMOSpectralLibraryIO.canRead(p))
        pd = QProgressDialog()
        sl = ARTMOSpectralLibraryIO.readFrom(p, feedback=pd)

        self.assertIsInstance(sl, SpectralLibrary)
        self.assertEqual(len(sl), 10)

    def test_CSV(self):
        # TEST CSV writing

        speclib = TestObjects.createSpectralLibrary()

        dirTMP = self.createTestOutputDirectory() / 'speclib-tests'
        os.makedirs(dirTMP, exist_ok=True)
        # txt = CSVSpectralLibraryIO.asString(speclib)
        pathCSV1 = dirTMP / 'speclib1.csv'
        pathCSV2 = dirTMP / 'speclib2.csv'

        writtenFiles = CSVSpectralLibraryIO.write(speclib, pathCSV1, feedback=QProgressDialog())
        self.assertIsInstance(writtenFiles, list)
        self.assertTrue(len(writtenFiles) == 1)

        writtenFiles = speclib.write(pathCSV2)
        self.assertIsInstance(writtenFiles, list)
        self.assertTrue(len(writtenFiles) == 1)

        self.assertTrue(CSVSpectralLibraryIO.canRead(pathCSV1), msg='Unable to read {}'.format(pathCSV1))
        sl_read1 = CSVSpectralLibraryIO.readFrom(pathCSV1, feedback=QProgressDialog())

        self.assertTrue(VectorSourceSpectralLibraryIO.canRead(pathCSV2), msg='Unable to read {}'.format(pathCSV2))
        sl_read2 = SpectralLibrary.readFrom(pathCSV2, feedback=QProgressDialog())

        self.assertTrue(len(sl_read1) > 0)
        self.assertIsInstance(sl_read1, SpectralLibrary)
        self.assertIsInstance(sl_read2, SpectralLibrary)

        self.assertEqual(len(sl_read1), len(speclib),
                         msg='Should return {} instead of {} SpectralProfiles'.format(len(speclib), len(sl_read1)))

        self.assertEqual(len(sl_read2), len(speclib),
                         msg='Should return {} instead of {} SpectralProfiles'.format(len(speclib), len(sl_read2)))

        profilesR = sorted(speclib.profiles(), key=lambda p: p.id())
        profiles1 = sorted(sl_read1.profiles(), key=lambda p: p.attribute('fid'))
        profiles2 = sorted(sl_read2.profiles(), key=lambda p: p.attribute('fid'))

        for pR, p1, p2 in zip(profilesR, profiles1, profiles2):
            self.assertIsInstance(pR, SpectralProfile)
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            self.assertEqual(pR.name(), p1.name())
            self.assertEqual(pR.name(), p2.name())
            self.assertEqual(pR.xUnit(), p1.xUnit())
            self.assertEqual(pR.xUnit(), p2.xUnit())
            self.assertEqual(pR.yUnit(), p1.yUnit())
            self.assertEqual(pR.yUnit(), p2.yUnit())

        self.SPECLIB = speclib

        try:
            os.remove(pathCSV1)
        except:
            pass

    def test_enmapbox_issue_463(self):
        # see https://bitbucket.org/hu-geomatics/enmap-box/issues/463/string-attributes-not-correctly-imported
        # for details

        TESTDATA = pathlib.Path(r'D:\Repositories\enmap-box\enmapboxtestdata')

        landcover_points = TESTDATA / 'landcover_berlin_point.shp'
        enmap = TESTDATA / 'enmap_berlin.bsq'

        if os.path.isfile(landcover_points) and os.path.isfile(enmap):
            lyrV = QgsVectorLayer(landcover_points.as_posix())
            lyrR = QgsRasterLayer(enmap.as_posix())

            slib = SpectralLibrary.readFromVector(lyrV, lyrR,
                                                  copy_attributes=True,
                                                  name_field='level_1',
                                                  )

            for profile in slib:
                value = profile.attribute('level_2')
                self.assertIsInstance(value, str)
                self.assertTrue(len(value) > 0)

            # test speed by
            uri = '/vsimem/temppoly.gpkg'
            drv: ogr.Driver = ogr.GetDriverByName('GPKG')
            ds: ogr.DataSource = drv.CreateDataSource(uri)

            lyr: ogr.Layer = ds.CreateLayer('polygon',
                                            srs=osrSpatialReference(lyrR.crs()),
                                            geom_type=ogr.wkbPolygon)

            pd = QProgressDialog()

            f = ogr.Feature(lyr.GetLayerDefn())
            ext = SpatialExtent.fromLayer(lyrR)
            g = ogr.CreateGeometryFromWkt(ext.asWktPolygon())
            f.SetGeometry(g)
            lyr.CreateFeature(f)
            ds.FlushCache()

            t0 = datetime.datetime.now()
            slib = SpectralLibrary.readFromVector(uri, lyrR, progress_handler=pd)
            self.assertIsInstance(slib, SpectralLibrary)
            dt = datetime.datetime.now() - t0
            print(f'Loaded {len(slib)} speclib profiles in {dt}')

            self.assertTrue(pd.value() == -1)

            pd.setValue(0)

            t0 = datetime.datetime.now()
            profiles = SpectralLibrary.readFromVector(uri, lyrR, return_profile_list=True)

            self.assertIsInstance(profiles, list)
            dt = datetime.datetime.now() - t0
            print(f'Loaded {len(profiles)} profiles in {dt}')
            s = ""

    def test_csv_from_string(self):
        from qps.speclib.io.csvdata import CSVSpectralLibraryIO
        # see https://bitbucket.org/hu-geomatics/enmap-box/issues/321/error-when-dropping-a-raster-eg
        # test if CSVSpectralLibraryIO.fromString() handles obviously none-CSV data

        p = str(QUrl.fromLocalFile(pathlib.Path(__file__).resolve().as_posix()))
        result = CSVSpectralLibraryIO.fromString(p)
        self.assertTrue(result == None)

    def test_findEnviHeader(self):

        binarypath = speclibpath

        hdr, bin = findENVIHeader(speclibpath)

        self.assertTrue(os.path.isfile(hdr))
        self.assertTrue(os.path.isfile(bin))

        self.assertTrue(bin == speclibpath)
        self.assertTrue(hdr.endswith('.hdr'))

        headerPath = hdr

        # is is possible to use the *.hdr
        hdr, bin = findENVIHeader(headerPath)

        self.assertTrue(os.path.isfile(hdr))
        self.assertTrue(os.path.isfile(bin))

        self.assertTrue(bin == speclibpath)
        self.assertTrue(hdr.endswith('.hdr'))

        feedback = self.createProcessingFeedback()
        sl1 = SpectralLibrary.readFrom(binarypath, feedback=feedback)
        sl2 = SpectralLibrary.readFrom(headerPath, feedback=feedback)

        self.assertEqual(sl1, sl2)

        # this should fail

        pathWrong = enmap
        hdr, bin = findENVIHeader(pathWrong)
        self.assertTrue((hdr, bin) == (None, None))

    def test_ENVI(self):

        pathESL = speclibpath

        from qpstestdata import speclib

        self.assertTrue(EnviSpectralLibraryIO.canRead(speclib))

        sl = EnviSpectralLibraryIO.readFrom(speclib)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl) > 0)

        sl = SpectralLibrary.readFrom(speclib)
        self.assertIsInstance(sl, SpectralLibrary)
        self.assertTrue(len(sl) > 0)
        csv = readCSVMetadata(pathESL)

        sl1 = EnviSpectralLibraryIO.readFrom(pathESL, feedback=QProgressDialog())

        self.assertIsInstance(sl1, SpectralLibrary)
        p0 = sl1[0]
        self.assertIsInstance(p0, SpectralProfile)

        #self.assertEqual(sl1.fieldNames(), ['fid', 'name', 'source', 'values'])
        #self.assertEqual(p0.fieldNames(), ['fid', 'name', 'source', 'values'])

        #self.assertEqual(p0.attribute('name'), p0.name())
        feedback = self.createProcessingFeedback()
        sl2 = SpectralLibrary.readFrom(pathESL, feedback=feedback)
        self.assertIsInstance(sl2, SpectralLibrary)
        self.assertEqual(sl1, sl2)
        p1 = sl2[0]
        self.assertIsInstance(p1, SpectralProfile)
        self.assertIsInstance(p1.xValues(), list)

        # test ENVI Spectral Library
        pathTmp = tempfile.mktemp(prefix='tmpESL', suffix='.sli')
        writtenFiles = EnviSpectralLibraryIO.write(sl1, pathTmp, feedback=QProgressDialog())

        nWritten = 0
        for pathHdr in writtenFiles:
            self.assertTrue(os.path.isfile(pathHdr))
            self.assertTrue(pathHdr.endswith('.sli'))

            basepath = os.path.splitext(pathHdr)[0]
            pathHDR = basepath + '.hdr'
            pathCSV = basepath + '.csv'
            self.assertTrue(os.path.isfile(pathHDR))
            self.assertTrue(os.path.isfile(pathCSV))

            self.assertTrue(EnviSpectralLibraryIO.canRead(pathHdr))
            sl_read1 = EnviSpectralLibraryIO.readFrom(pathHdr, feedback=QProgressDialog())
            self.assertIsInstance(sl_read1, SpectralLibrary)

            for fieldA in sl1.fields():
                self.assertIsInstance(fieldA, QgsField)
                a = sl_read1.fields().lookupField(fieldA.name())
                self.assertTrue(a >= 0)
                fieldB = sl_read1.fields().at(a)
                self.assertIsInstance(fieldB, QgsField)
                # if fieldA.type() != fieldB.type():
                #    s  = ""
                # self.assertEqual(fieldA.type(), fieldB.type())

            sl_read2 = SpectralLibrary.readFrom(pathHdr, feedback=QProgressDialog())
            self.assertIsInstance(sl_read2, SpectralLibrary)

            print(sl_read1)

            self.assertTrue(len(sl_read1) > 0)
            self.assertEqual(sl_read1, sl_read2)
            nWritten += len(sl_read1)

        self.assertEqual(len(sl1), nWritten, msg='Written and restored {} instead {}'.format(nWritten, len(sl1)))

        # addresses issue #11:
        # No error is generated when trying (by accident) to read the ENVI header file instead of the .sli/.esl file itself.

        pathHdr = os.path.splitext(speclibpath)[0] + '.hdr'
        self.assertTrue(os.path.isfile(pathHdr))
        sl1 = SpectralLibrary.readFrom(speclibpath, feedback=QProgressDialog())
        sl2 = SpectralLibrary.readFrom(pathHdr, feedback=QProgressDialog())
        self.assertIsInstance(sl1, SpectralLibrary)
        self.assertTrue(len(sl1) > 0)

        for p1, p2 in zip(sl1[:], sl2[:]):
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            self.assertEqual(p1, p2)

    def test_rasterIO(self):

        testdir = self.createTestOutputDirectory() / 'speclibIO'
        os.makedirs(testdir, exist_ok=True)

        path = testdir / 'raster.tif'

        sl = TestObjects.createSpectralLibrary(n_bands=[10, 177])
        io = RasterSourceSpectralLibraryIO()
        files = io.write(sl, path)

        sl2 = SpectralLibrary()
        self.assertTrue(sl2.startEditing())
        for f in files:
            self.assertTrue(os.path.isfile(f))
            sl = io.readFrom(f)
            self.assertIsInstance(sl, SpectralLibrary)
            sl2.addSpeclib(sl)
        self.assertTrue(sl2.commitChanges())
        self.assertEqual(len(sl), len(sl2))

    def test_ENVILabeled(self):

        from qpstestdata import speclib_labeled as pathESL
        from qpstestdata import speclib as pathSLI

        sl = SpectralLibrary.readFrom(pathSLI)
        for p in sl:
            self.assertIsInstance(p, SpectralProfile)
            print([p.attribute(a) for a in p.fieldNames() if a != FIELD_VALUES])
        s = ""

        from qps import registerEditorWidgets
        from qps.classification.classificationscheme import EDITOR_WIDGET_REGISTRY_KEY as RasterClassificationKey
        registerEditorWidgets()

        sl1 = EnviSpectralLibraryIO.readFrom(pathESL, feedback=QProgressDialog())

        self.assertIsInstance(sl1, SpectralLibrary)
        p0 = sl1[0]
        self.assertIsInstance(p0, SpectralProfile)
        for n in ['fid', 'name', 'source', 'values', 'level_1', 'level_2', 'level_3']:
            self.assertTrue(n in sl1.fieldNames())

        setupTypes = []
        setupConfigs = []
        for i in range(sl1.fields().count()):
            setup = sl1.editorWidgetSetup(i)
            self.assertIsInstance(setup, QgsEditorWidgetSetup)
            setupTypes.append(setup.type())
            setupConfigs.append(setup.config())

        classValueFields = ['level_1', 'level_2', 'level_3']
        for name in classValueFields:
            i = sl1.fields().indexFromName(name)
            self.assertEqual(setupTypes[i], RasterClassificationKey)

        sl = SpectralLibrary()
        sl.startEditing()
        sl.addSpeclib(sl1)
        self.assertTrue(sl.commitChanges())

        for name in classValueFields:
            i = sl.fields().indexFromName(name)
            j = sl1.fields().indexFromName(name)
            self.assertTrue(i > 0)
            self.assertTrue(j > 0)
            setupNew = sl.editorWidgetSetup(i)
            setupOld = sl1.editorWidgetSetup(j)
            self.assertEqual(setupOld.type(), RasterClassificationKey)
            self.assertEqual(setupNew.type(), RasterClassificationKey,
                             msg='EditorWidget type is "{}" not "{}"'.format(setupNew.type(), setupOld.type()))

        sl = SpectralLibrary()
        sl.startEditing()
        sl.addSpeclib(sl1, copyEditorWidgetSetup=False)
        self.assertTrue(sl.commitChanges())

        for name in classValueFields:
            i = sl.fields().indexFromName(name)
            j = sl1.fields().indexFromName(name)
            self.assertTrue(i > 0)
            self.assertTrue(j > 0)
            setupNew = sl.editorWidgetSetup(i)
            setupOld = sl1.editorWidgetSetup(j)
            self.assertEqual(setupOld.type(), RasterClassificationKey)
            self.assertNotEqual(setupNew.type(), RasterClassificationKey)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)