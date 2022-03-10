import os
import pathlib
import sys
import typing

from qgis.PyQt import sip
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsVectorFileWriter, QgsField, QgsProject, QgsWkbTypes, QgsVectorLayer, \
    QgsExpressionContext, QgsFields, QgsProcessingFeedback, QgsFeature, \
    QgsCoordinateReferenceSystem
from ..core import is_profile_field
from ..core.spectrallibraryio import SpectralLibraryImportWidget, SpectralLibraryIO, \
    SpectralLibraryExportWidget
from ..core.spectralprofile import encodeProfileValueDict, decodeProfileValueDict


class GeoJsonSpectralLibraryExportWidget(SpectralLibraryExportWidget):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def formatName(self) -> str:
        return GeoJsonSpectralLibraryIO.formatName()

    def supportsMultipleSpectralSettings(self) -> bool:
        return True

    def supportsMultipleProfileFields(self) -> bool:
        return True

    def supportsLayerName(self) -> bool:
        return True

    def spectralLibraryIO(cls) -> 'SpectralLibraryIO':
        return SpectralLibraryIO.spectralLibraryIOInstances(GeoJsonSpectralLibraryIO)

    def filter(self) -> str:
        return "GeoJSON (*.geojson)"

    def exportSettings(self, settings: dict) -> dict:
        speclib = self.speclib()
        if isinstance(speclib, QgsVectorLayer):
            settings['crs'] = speclib.crs()
            settings['wkbType'] = speclib.wkbType()
        return settings


class GeoJsonSpectralLibraryImportWidget(SpectralLibraryImportWidget):

    def __init__(self, *args, **kwds):
        super(GeoJsonSpectralLibraryImportWidget, self).__init__(*args, **kwds)

        self.mSource: QgsVectorLayer = None

    def spectralLibraryIO(cls) -> 'SpectralLibraryIO':
        return SpectralLibraryIO.spectralLibraryIOInstances(GeoJsonSpectralLibraryIO)

    def filter(self) -> str:
        return "GeoJSON (*.geojson)"

    def setSource(self, source: str):
        lyr = QgsVectorLayer(source)
        if isinstance(lyr, QgsVectorLayer) and lyr.isValid():
            lyr.loadDefaultStyle()
            self.mSource = lyr
        self.sigSourceChanged.emit()

    def sourceFields(self) -> QgsFields:
        if isinstance(self.mSource, QgsVectorLayer):
            return self.mSource.fields()
        else:
            return QgsFields()

    def sourceCrs(self) -> QgsCoordinateReferenceSystem:
        if isinstance(self.mSource, QgsVectorLayer):
            return self.mSource.crs()
        else:
            return None

    def createExpressionContext(self) -> QgsExpressionContext:
        context = QgsExpressionContext()

        return context


class GeoJsonFieldValueConverter(QgsVectorFileWriter.FieldValueConverter):

    def __init__(self, fields: QgsFields):
        super(GeoJsonFieldValueConverter, self).__init__()
        self.mFields: QgsFields = QgsFields(fields)

        # define converter functions
        self.mFieldDefinitions = dict()
        self.mFieldConverters = dict()

        for field in self.mFields:
            name = field.name()
            idx = self.mFields.lookupField(name)
            if field.type() != QVariant.String and is_profile_field(field):
                convertedField = QgsField(name=name, type=QVariant.String)
                self.mFieldDefinitions[name] = convertedField
                if False:
                    self.mFieldConverters[idx] = lambda v: 'dummy'
                else:
                    self.mFieldConverters[idx] = lambda v, f=convertedField: \
                        encodeProfileValueDict(decodeProfileValueDict(v), convertedField)
            else:
                self.mFieldDefinitions[name] = QgsField(super().fieldDefinition(field))
                self.mFieldConverters[idx] = lambda v: v

    def clone(self) -> QgsVectorFileWriter.FieldValueConverter:
        return GeoJsonFieldValueConverter(self.mFields)

    def convert(self, fieldIdxInLayer: int, value: typing.Any) -> typing.Any:
        return self.mFieldConverters[fieldIdxInLayer](value)

    def fieldDefinition(self, field: QgsField) -> QgsField:
        return QgsField(self.mFieldDefinitions[field.name()])


class GeoJsonSpectralLibraryIO(SpectralLibraryIO):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    @classmethod
    def formatName(cls) -> str:
        return 'GeoJSON'

    @classmethod
    def createExportWidget(cls) -> SpectralLibraryExportWidget:
        return GeoJsonSpectralLibraryExportWidget()

    @classmethod
    def createImportWidget(cls) -> SpectralLibraryImportWidget:
        return GeoJsonSpectralLibraryImportWidget()

    @classmethod
    def exportProfiles(cls,
                       path: str,
                       exportSettings: dict,
                       profiles: typing.Iterable[QgsFeature],
                       feedback: QgsProcessingFeedback) -> typing.List[str]:

        """
        :param fileName: file name to write to
        :param fields: fields to write
        :param geometryType: geometry type of output file
        :param srs: spatial reference system of output file
        :param transformContext: coordinate transform context
        :param options: save options
        """
        # writer: QgsVectorFileWriter = None
        # saveVectorOptions = QgsVectorFileWriter.SaveVectorOptions()
        # saveVectorOptions.feedback = feedback
        # saveVectorOptions.driverName = 'GPKG'
        # saveVectorOptions.symbologyExport = QgsVectorFileWriter.SymbolLayerSymbology
        # saveVectorOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        # saveVectorOptions.layerOptions = ['OVERWRITE=YES', 'TRUNCATE_FIELDS=YES']
        newLayerName = exportSettings.get('layer_name', '')
        if newLayerName == '':
            newLayerName = os.path.basename(newLayerName)

        path = pathlib.Path(path).as_posix()
        datasourceOptions = exportSettings.get('options', dict())
        assert isinstance(datasourceOptions, dict)

        ogrDataSourceOptions = ['ATTRIBUTES_SKIP=NO', 'DATE_AS_STRING=YES', 'ARRAY_AS_STRING=YES']
        ogrLayerOptions = ['NATIVE_DATA=True']

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
        options.feedback = feedback
        options.datasourceOptions = ogrDataSourceOptions
        options.layerOptions = ogrLayerOptions
        options.fileEncoding = 'UTF-8'
        options.skipAttributeCreation = False
        options.driverName = 'GeoJSON'

        wkbType = exportSettings.get('wkbType', QgsWkbTypes.NoGeometry)
        crs = QgsCoordinateReferenceSystem(exportSettings.get('crs', QgsCoordinateReferenceSystem()))

        # writer: QgsVectorFileWriter = None
        transformContext = QgsProject.instance().transformContext()

        converter: GeoJsonFieldValueConverter = None
        writer: QgsVectorFileWriter = None
        fields: QgsFields = None
        for i, profile in enumerate(profiles):
            if writer is None:

                fields = profile.fields()
                converter = GeoJsonFieldValueConverter(fields)
                options.fieldValueConverter = converter
                writer = QgsVectorFileWriter.create(path, fields, wkbType, crs, transformContext, options)

                if writer.hasError() != QgsVectorFileWriter.NoError:
                    raise Exception(f'Error when creating {path}: {writer.errorMessage()}')

            if not writer.addFeature(profile):
                if writer.errorCode() != QgsVectorFileWriter.NoError:
                    raise Exception(f'Error when creating feature: {writer.errorMessage()}')

        del writer

        # set profile column styles etc.
        lyr = QgsVectorLayer(path)

        if lyr.isValid() and isinstance(fields, QgsFields):
            for name in fields.names():
                i = lyr.fields().lookupField(name)
                if i >= 0:
                    lyr.setEditorWidgetSetup(i, fields.field(name).editorWidgetSetup())
            msg, success = lyr.saveDefaultStyle()
            if success is False:
                print(msg, file=sys.stderr)
        del lyr
        return [path]

    @classmethod
    def importProfiles(cls,
                       path: str,
                       importSettings: dict,
                       feedback: QgsProcessingFeedback) -> typing.List[QgsFeature]:
        lyr = QgsVectorLayer(path)
        # todo: add filters
        features = list(lyr.getFeatures())

        sip.delete(lyr)
        del lyr
        return features
