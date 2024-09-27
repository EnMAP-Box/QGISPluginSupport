import datetime
import json
import warnings
from typing import Any, Dict, List
from uuid import uuid4

import numpy as np
from osgeo.ogr import DataSource, Driver, GetDriverByName, Layer
from osgeo.osr import SpatialReference

from qgis.PyQt.QtCore import QDate, QDateTime, QLocale, Qt, QTime
from qgis.core import QgsEditorWidgetSetup, QgsExpressionContext, QgsField, QgsFields, QgsProperty, \
    QgsPropertyTransformer, QgsRemappingSinkDefinition, QgsVectorDataProvider, QgsVectorFileWriter, QgsVectorLayer
from .qgisenums import QMETATYPE_QDATE, QMETATYPE_QDATETIME, QMETATYPE_QSTRING, QMETATYPE_QTIME, \
    QMETATYPE_QVARIANTMAP
from .speclib import EDITOR_WIDGET_REGISTRY_KEY
from .speclib.core import is_profile_field
from .speclib.core.spectralprofile import decodeProfileValueDict, encodeProfileValueDict, ProfileEncoding


def create_vsimemfile(extension) -> DataSource:
    driver = QgsVectorFileWriter.driverForExtension(extension)
    assert driver != ''
    path = f'/vsimem/example.{driver.replace(' ', '_')}.{uuid4()}{extension}'

    try:
        drv: Driver = GetDriverByName(driver)

        ds: DataSource = drv.CreateDataSource(path)
        srs: SpatialReference = SpatialReference()
        srs.ImportFromEPSG(4326)
        lyr: Layer = ds.CreateLayer('layer', srs=srs)
        from osgeo import ogr
        lyr.CreateField(ogr.FieldDefn('name', field_type=ogr.OFTString))
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField('name', 'dummy')
        lyr.CreateFeature(f)
        ds.FlushCache()
    except Exception as ex:
        warnings.warn(f'Unable to get native types for {extension}:\n {ex}')
        return None
    return ds


__NATIVE_TYPES: Dict[str, List[QgsVectorDataProvider.NativeType]] = dict()


def collect_native_types() -> Dict[str, List[QgsVectorDataProvider.NativeType]]:
    if len(__NATIVE_TYPES) == 0:

        for extension in ['.csv', '.gpkg', '.geojson', '.shp', '.kml', '.sqlite']:
            ds = create_vsimemfile(extension)
            if not isinstance(ds, DataSource):
                warnings.warn(f'Unable to collect native types for files of type: {extension}')
                continue

            drv: Driver = ds.GetDriver()
            path = ds.GetDescription()
            vl = QgsVectorLayer(path)
            assert vl.isValid()
            __NATIVE_TYPES[drv.name] = vl.dataProvider().nativeTypes()

            del vl, ds
            r = drv.DeleteDataSource(path)

        # add in-memory vector types
        vl = QgsVectorLayer("point?crs=epsg:4326&field=id:integer", "Scratch point layer", "memory")
        __NATIVE_TYPES['memory'] = vl.dataProvider().nativeTypes()

    return __NATIVE_TYPES


class GenericPropertyTransformer(QgsPropertyTransformer):
    """
    A QgsPropertyTransformer to transform encoded spectral profile dictionaries,
    e.g. as returned by QgsProperty expressions, into the correct encoding as
    required by a QgsField data type (str, json or bytes).
    """

    def __init__(self, dstField: QgsField):
        super().__init__()
        self.mDstField: QgsField = QgsField(dstField)

        self.mTransformFunction = self.fieldValueTransformFunction(self.mDstField)

    def clone(self) -> 'QgsPropertyTransformer':
        return GenericPropertyTransformer(self.mDstField)

    def transform(self, context: QgsExpressionContext, value: Any) -> Any:
        if self.mTransformFunction:
            value = self.mTransformFunction(value)
        else:
            s = ""
        return value

    @staticmethod
    def fieldValueTransformFunction(dstField: QgsField):
        if is_profile_field(dstField):
            encoding = ProfileEncoding.fromInput(dstField)
            return lambda v, e=encoding: encodeProfileValueDict(decodeProfileValueDict(v), encoding)
        elif dstField.type() == QMETATYPE_QSTRING:
            return lambda v: GenericPropertyTransformer.toString(v)
        elif dstField.type() == QMETATYPE_QDATETIME:
            return lambda v: GenericPropertyTransformer.toDateTime(v)
        elif dstField.type() == QMETATYPE_QDATE:
            return lambda v: GenericPropertyTransformer.toDate(v)
        elif dstField.type() == QMETATYPE_QTIME:
            return lambda v: GenericPropertyTransformer.toTime(v)
        elif dstField.type() == QMETATYPE_QVARIANTMAP:
            return lambda v: GenericPropertyTransformer.toMap(v)
        return lambda v: v

    @staticmethod
    def toMap(value) -> dict:
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                data = json.loads(value)
                if isinstance(data, dict):
                    return data
                else:
                    s = ""
            except Exception as ex:
                return None
        else:
            return None

    @staticmethod
    def toString(value) -> str:
        return str(value)

    @staticmethod
    def toDateTime(v) -> QDateTime:
        if isinstance(v, QDateTime):
            return v
        elif isinstance(v, datetime.datetime):
            return QDateTime.fromString(v.isoformat(), Qt.ISODateWithMs)
        elif isinstance(v, datetime.date):
            return QDateTime(QDate.fromString(v.isoformat(), Qt.ISODate), QTime())
        elif isinstance(v, QDate):
            return QDateTime(v, QTime())
        elif isinstance(v, str):
            # try to parse datetime from string
            for fmt in [Qt.ISODate, Qt.ISODateWithMs, Qt.TextDate, Qt.RFC2822Date]:
                if (r := QDateTime.fromString(v, fmt)).isValid():
                    return r
            locale = QLocale()
            for fmt in [QLocale.LongFormat, QLocale.ShortFormat, QLocale.NarrowFormat]:
                if (r := locale.toDateTime(v, fmt)).isValid():
                    return r
        return None

    @staticmethod
    def toDate(v) -> QDate:
        if isinstance(v, QDate):
            return v
        elif isinstance(v, (datetime.datetime, QDateTime)):
            return GenericPropertyTransformer.toDateTime(v).date()
        elif isinstance(v, datetime.date):
            return QDate.fromString(v.isoformat(), Qt.ISODate)
        elif isinstance(v, str):
            for fmt in [Qt.ISODate, Qt.ISODateWithMs, Qt.RFC2822Date]:
                if (r := QDate.fromString(v, fmt)).isValid():
                    return r
            locale = QLocale()
            for fmt in [QLocale.LongFormat, QLocale.ShortFormat, QLocale.NarrowFormat]:
                if (r := locale.toDate(v, fmt)).isValid():
                    return r

            if (r := GenericPropertyTransformer.toDateTime(v)).isValid():
                return r.date()

        return None

    @staticmethod
    def toTime(v) -> QTime:
        if isinstance(v, QTime):
            return v
        elif isinstance(v, datetime.time):
            return QTime.fromString(v.isoformat(), Qt.ISODateWithMs)
        elif isinstance(v, (QDateTime, datetime.datetime)):
            return GenericPropertyTransformer.toDateTime(v).time()
        elif isinstance(v, str):

            for fmt in [Qt.ISODate, Qt.ISODateWithMs, Qt.RFC2822Date]:
                if (r := QTime.fromString(v, fmt)).isValid():
                    return r
            locale = QLocale()
            for fmt in [QLocale.LongFormat, QLocale.ShortFormat, QLocale.NarrowFormat]:
                if (r := locale.toTime(v, fmt)).isValid():
                    return r

            if (r := GenericPropertyTransformer.toDateTime(v)).isValid():
                return r.time()

        return None


class GenericFieldValueConverter(QgsVectorFileWriter.FieldValueConverter):

    def __init__(self, srcFields: QgsFields, dstFields: QgsFields):
        super().__init__()
        self.mSrcFields: QgsFields = QgsFields(srcFields)
        self.mDstFields: QgsFields = QgsFields(dstFields)

        self.mFieldConverters = dict()

        for i, (fSrc, fDst) in enumerate(zip(self.mSrcFields, self.mDstFields)):

            fSrc: QgsField
            fDst: QgsField

            idxSrc = self.mSrcFields.lookupField(fSrc.name())
            idxDst = self.mDstFields.lookupField(fDst.name())

            if is_profile_field(fSrc):
                if fDst.type() in [QMETATYPE_QVARIANTMAP, QMETATYPE_QSTRING]:
                    func = lambda value, f=fDst: self.convertProfileField(value, f)
                s = ""
            elif fDst.type() == QMETATYPE_QSTRING:
                func = lambda value: GenericPropertyTransformer.toString(value)
            elif fDst.type() == QMETATYPE_QDATETIME:
                func = lambda value: GenericPropertyTransformer.toDateTime(value)
            elif fDst.type() == QMETATYPE_QDATE:
                func = lambda value: GenericPropertyTransformer.toDate(value)
            elif fDst.type() == QMETATYPE_QTIME:
                func = lambda value: GenericPropertyTransformer.toTime(value)
            else:
                # default: don't convert
                func = lambda value: value

            self.mFieldConverters[i] = func

    @staticmethod
    def compatibleTargetFields(srcFields: QgsFields, targetDriver: str) -> QgsFields:
        NATIVE_TYPES = collect_native_types()
        if targetDriver not in NATIVE_TYPES:
            if (t2 := QgsVectorFileWriter.driverForExtension(targetDriver)) and t2 in NATIVE_TYPES:
                targetDriver = t2

        if targetDriver not in NATIVE_TYPES:
            warnings.warn(f'Unknown native types for driver: {targetDriver}')
            return QgsFields(srcFields)

        native_types = NATIVE_TYPES[targetDriver]
        tsn_list = [(nt.mType, nt.mSubType, nt.mTypeName) for nt in native_types]

        supports_json: QgsVectorDataProvider.NativeType = None
        supports_map: QgsVectorDataProvider.NativeType = None

        string_types = [n for n in native_types if n.mType == QMETATYPE_QSTRING]
        if len(string_types) == 0:
            warnings.warn('Unable to convert to string')
            return QgsFields(srcFields)
        elif len(string_types) > 0:
            # use the longest string type possible
            string_types = sorted(string_types, key=lambda v: v.mMaxLen)
            supports_string = string_types[0] if string_types[0].mMaxLen == -1 else string_types[-1]
        else:
            supports_string: QgsVectorDataProvider.NativeType = string_types[0]

        for n in native_types:
            if supports_string is None and n.mType == QMETATYPE_QSTRING:
                supports_string = n
            if n.mTypeName.lower() == 'json':
                supports_json = n
            if n.mTypeName.lower() == 'map':
                supports_map = n

        dstFields = QgsFields()
        for srcF in srcFields:
            dstF = None
            tsn = (srcF.type(), srcF.subType(), srcF.typeName())
            if tsn not in tsn_list:
                # this field needs to be transformed

                if is_profile_field(srcF):
                    if supports_json:
                        dstF = QgsField(name=srcF.name(),
                                        type=supports_json.mType,
                                        typeName=supports_json.mTypeName,
                                        subType=supports_json.mSubType,
                                        comment=srcF.comment())

                    elif supports_map:
                        dstF = QgsField(name=srcF.name(),
                                        type=supports_map.mType,
                                        typeName=supports_json.mTypeName,
                                        subType=supports_map.mSubType,
                                        comment=srcF.comment())

                    else:
                        dstF = QgsField(name=srcF.name(),
                                        type=supports_string.mType,
                                        typeName=supports_string.mTypeName,
                                        subType=supports_string.mSubType,
                                        comment=srcF.comment())
                    dstF.setEditorWidgetSetup(QgsEditorWidgetSetup(EDITOR_WIDGET_REGISTRY_KEY, {}))

                elif srcF.type() == QMETATYPE_QVARIANTMAP:
                    if supports_json:
                        dstF = QgsField(name=srcF.name(),
                                        type=supports_json.mType,
                                        subType=supports_json.mSubType,
                                        typeName=supports_json.mTypeName,
                                        comment=srcF.comment())
                    elif supports_map:
                        dstF = QgsField(name=srcF.name(),
                                        type=supports_map.mType,
                                        typeName=supports_map.mTypeName,
                                        subType=supports_map.mSubType,
                                        comment=srcF.comment())

                # the last resort: convert to longest string data type
                if dstF is None:
                    dstF = QgsField(name=srcF.name(),
                                    type=supports_string.mType,
                                    subType=supports_string.mSubType,
                                    typeName=supports_string.mTypeName,
                                    comment=srcF.comment())
            else:
                dstF = QgsField(srcF)
            dstFields.append(dstF)
        return dstFields

        s = ""

    def convertProfileField(self, value, field: QgsField) -> Any:
        d = decodeProfileValueDict(value, numpy_arrays=True)
        d['y'] = d['y'].astype(np.float32)
        text = encodeProfileValueDict(d, field)
        return text

    def clone(self) -> QgsVectorFileWriter.FieldValueConverter:
        return GenericFieldValueConverter(self.mSrcFields, self.mDstFields)

    def convert(self, fieldIdxInLayer: int, value: Any) -> Any:
        """
        Convert the provided value, for field fieldIdxInLayer.
        """
        return self.mFieldConverters[fieldIdxInLayer](value)

    def fieldDefinition(self, field: QgsField) -> QgsField:
        """
        Returns a possibly modified field definition.
        """
        return QgsField(self.mDstFields[field.name()])


class GenericRemappingSinkDefinition(QgsRemappingSinkDefinition):

    def __init__(self, *args, **kwds):
        super(*args, **kwds)

        self.mTransformers = []

        self.mFieldMap: Dict[str, QgsProperty] = dict()

    def setDestinationFields(self, fields: QgsFields):
        super().setDestinationFields(fields)
        self.updatePropertyMap()

    def updatePropertyMap(self):
        self.mFieldMap.clear()
        self.mTransformers.clear()

        for dstField in self.destinationFields():
            transformer = GenericPropertyTransformer(dstField)
            self.mTransformers.append(transformer)
            property = QgsProperty.fromField(dstField)

            # srcProp.setTransformer(transformer)

            transformer = GenericFieldValueConverter()
            property.setTransformer(GenericFieldValueConverter)
            self.mFieldMappropertyMap[dstField] = property
        s = ""