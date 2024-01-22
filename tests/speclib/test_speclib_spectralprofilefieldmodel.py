import unittest

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QTableView, QComboBox, QWidget, QPushButton, QHBoxLayout
from qgis.core import QgsField
from qgis.gui import QgsGui, QgsEditorWidgetFactory

from qgis.core import edit
from qps.speclib.core import profile_fields
from qps.speclib.core.spectrallibrary import SpectralLibraryUtils
from qps.speclib.gui.spectrallibrarywidget import SpectralLibraryWidget
from qps.speclib.gui.spectralprofilefieldmodel import SpectralProfileFieldActivatorModel, \
    SpectralProfileFieldActivatorDialog, SpectralProfileFieldListModel
from qps.testing import start_app, TestCase, TestObjects

start_app()


class TestSpectralProfileFieldModel(TestCase):

    def test_fieldListModel(self):
        from qps import registerEditorWidgets
        registerEditorWidgets()
        vl = TestObjects.createSpectralLibrary()

        with edit(vl):
            vl.addAttribute(QgsField('nofield1', QVariant.Int))
            vl.addAttribute(QgsField('nofield2', QVariant.Double))
            vl.addAttribute(QgsField('nofield3', QVariant.String, len=255))
            b1 = SpectralLibraryUtils.addSpectralProfileField(vl, 'profile1')
            b2 = SpectralLibraryUtils.addSpectralProfileField(vl, 'profile2')

        reg: QgsEditorWidgetFactory = QgsGui.editorWidgetRegistry()

        assert SpectralLibraryUtils.makeToProfileField(vl, 'profile1')
        assert SpectralLibraryUtils.makeToProfileField(vl, 'profile2')
        pmodel = SpectralProfileFieldListModel()
        pmodel.setLayer(vl)

        self.assertEqual(pmodel.indexFromName('profile1').row(), 1)
        self.assertEqual(pmodel.indexFromName('profile2').row(), 2)

        def unsetProfileColumn(*args):

            for field in profile_fields(vl):
                SpectralLibraryUtils.removeProfileField(vl, field)

        def setProfileColumns(*args):
            for field in vl.fields():
                SpectralLibraryUtils.makeToProfileField(vl, field)
            # pmodel.updateFields()

        w = QWidget()
        layout = QHBoxLayout()
        w.setLayout(layout)

        cb = QComboBox()
        cb.setModel(pmodel)

        btnAdd = QPushButton('+')
        btnAdd.clicked.connect(setProfileColumns)
        btnRem = QPushButton('-')
        btnRem.clicked.connect(unsetProfileColumn)

        layout.addWidget(btnAdd)
        layout.addWidget(btnRem)
        layout.addWidget(cb)

        self.showGui(w)

    def test_fieldActivatorModel(self):

        vl = TestObjects.createSpectralLibrary()

        with edit(vl):
            vl.addAttribute(QgsField('nofield1', QVariant.Int))
            vl.addAttribute(QgsField('nofield2', QVariant.Double))
            vl.addAttribute(QgsField('nofield3', QVariant.String, len=255))
            vl.addAttribute(QgsField('profile1', QVariant.String, len=0))
            vl.addAttribute(QgsField('profile2', QVariant.String, len=-1))
            vl.addAttribute(QgsField('profile3', QVariant.ByteArray))

        model = SpectralProfileFieldActivatorModel()
        model.setLayer(vl)

        tv = QTableView()
        tv.setModel(model)

        self.showGui(tv)

    def test_fieldActivator(self):
        from qps import registerEditorWidgets
        registerEditorWidgets()
        vl = TestObjects.createSpectralLibrary()

        with edit(vl):
            vl.addAttribute(QgsField('nofield1', QVariant.Int))
            vl.addAttribute(QgsField('nofield2', QVariant.Double))
            vl.addAttribute(QgsField('nofield3', QVariant.String, len=255))
            vl.addAttribute(QgsField('profile1', QVariant.String, len=0))
            vl.addAttribute(QgsField('profile2', QVariant.String, len=-1))
            vl.addAttribute(QgsField('profile3', QVariant.ByteArray))

        d = SpectralProfileFieldActivatorDialog()

        pmodel = SpectralProfileFieldListModel()
        pmodel.setLayer(vl)
        cb = QComboBox()
        cb.setModel(pmodel)
        d.layout().addWidget(cb)

        d.setLayer(vl)
        slw = SpectralLibraryWidget(speclib=vl)
        self.showGui(slw)


if __name__ == '__main__':
    unittest.main()