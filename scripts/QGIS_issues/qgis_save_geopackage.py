import pathlib
import pickle
import random

from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsField, QgsFields, QgsProcessingFeedback, QgsProject, \
    QgsVectorFileWriter, QgsWkbTypes
from qgis.PyQt.QtCore import QByteArray, QVariant

feedback = QgsProcessingFeedback()

saveVectorOptions = QgsVectorFileWriter.SaveVectorOptions()
saveVectorOptions.feedback = feedback
saveVectorOptions.driverName = 'GPKG'
saveVectorOptions.symbologyExport = QgsVectorFileWriter.SymbolLayerSymbology
saveVectorOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

path = pathlib.Path('~').expanduser() / 'test.gpkg'
# if path.is_file() and saveVectorOptions.actionOnExistingFile != QgsVectorFileWriter.CreateOrOverwriteLayer:
#    os.remove(path)
# assert not path.is_file()
print(f'file exists: {path}')
fields = QgsFields()
fields.append(QgsField('name', QMETATYPE_QSTRING))
fields.append(QgsField('num', QMETATYPE_INT))
fields.append(QgsField('binary', QVariant.ByteArray))

features = []
for i, n in enumerate(['A', 'B', 'C', 'D']):
    feature = QgsFeature(fields)
    feature.setAttribute('name', n)
    feature.setAttribute('num', random.randint(0, 100))
    pkl = QByteArray(pickle.dumps(dict(testdata=f'{i}:{n}')))
    feature.setAttribute('binary', pkl)
    features.append(feature)

transformContext = QgsProject.instance().transformContext()
writer = QgsVectorFileWriter.create(
    fileName=path.as_posix(),
    fields=fields,
    geometryType=QgsWkbTypes.NoGeometry,
    srs=QgsCoordinateReferenceSystem(),
    transformContext=transformContext,
    options=saveVectorOptions,
    # sinkFlags=None,
    # newLayer=newLayerName,
    newFilename=None
)
if writer.hasError() != QgsVectorFileWriter.NoError:
    raise Exception(f'Error when creating {path}: {writer.errorMessage()}')

for f in features:
    if not writer.addFeature(f):
        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise Exception(f'Error when creating feature: {writer.errorMessage()}')
