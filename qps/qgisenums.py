
# This autogenerated file provides unified access to enums which
# were removed between different QGIS API version.
# Do not modify, change create_qgisenums.py instead!

from qgis.PyQt.QtCore import QVariant, QMetaType
from qgis.core import Qgis


#  Import old locations
from qgis.core import (QgsAction, QgsAggregateCalculator, QgsArcGisPortalUtils, QgsAttributeEditorElement, QgsColorRampShader, QgsCoordinateReferenceSystem, QgsDataProvider, QgsEditFormConfig, QgsFeatureRequest, QgsFeatureSource, QgsFields, QgsGpsInformation, QgsGradientFillSymbolLayer, QgsGraduatedSymbolRenderer, QgsLabeling, QgsLabelingEngineSettings, QgsLayoutItemPicture, QgsMapLayerProxyModel, QgsMapLayerType, QgsPainting, QgsPalLayerSettings, QgsProcessing, QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeatureSource, QgsProcessingFeatureSourceDefinition, QgsProcessingParameterDateTime, QgsProcessingParameterDefinition, QgsProcessingParameterField, QgsProcessingParameterFile, QgsProcessingParameterNumber, QgsProcessingParameterTinInputLayers, QgsProcessingParameterType, QgsProcessingProvider, QgsProject, QgsProperty, QgsProviderMetadata, QgsRandomMarkerFillSymbolLayer, QgsRaster, QgsRasterBandStats, QgsRasterDataProvider, QgsRasterFileWriter, QgsRasterInterface, QgsRasterLayer, QgsRelation, QgsScaleBarSettings, QgsSimpleMarkerSymbolLayerBase, QgsStatisticalSummary, QgsStringStatisticalSummary, QgsStringUtils, QgsTemporalNavigationObject, QgsTextFormat, QgsTextRenderer, QgsUnitTypes, QgsVectorDataProvider, QgsVectorFileWriter, QgsVectorSimplifyMethod, QgsWkbTypes)
from qgis.gui import (QgsActionMenu, QgsMapLayerAction)
from qgis._3d import (QgsPoint3DSymbol)
from qgis.analysis import (QgsZonalStatistics)

#  API Switches

# QgsField - since QGIS 3.38, use the method with a QMetaType::Type argument instead
QMETATYPE_QSTRING = QMetaType.QString if Qgis.versionInt() >= 33800 else QVariant.String
QMETATYPE_BOOL = QMetaType.Bool if Qgis.versionInt() >= 33800 else QVariant.Bool
QMETATYPE_INT = QMetaType.Int if Qgis.versionInt() >= 33800 else QVariant.Int
QMETATYPE_DOUBLE = QMetaType.Double if Qgis.versionInt() >= 33800 else QVariant.Double
QMETATYPE_UINT = QMetaType.UInt if Qgis.versionInt() >= 33800 else QVariant.UInt
# QMETATYPE_ULONG = QMetaType.ULong if Qgis.versionInt() >= 33800 else QVariant.ULong
QMETATYPE_ULONGLONG = QMetaType.ULongLong if Qgis.versionInt() >= 33800 else QVariant.ULongLong
QMETATYPE_QTIME = QMetaType.QTime if Qgis.versionInt() >= 33800 else QVariant.Time
QMETATYPE_QDATE = QMetaType.QDate if Qgis.versionInt() >= 33800 else QVariant.Date
QMETATYPE_QDATETIME = QMetaType.QDateTime if Qgis.versionInt() >= 33800 else QVariant.DateTime
QMETATYPE_QVARIANTMAP = QMetaType.QVariantMap if Qgis.versionInt() >= 33800 else QVariant.Map
QMETATYPE_QBYTEARRAY = QMetaType.QByteArray if Qgis.versionInt() >= 33800 else QVariant.ByteArray


QGIS_ACTIONTYPE = Qgis.ActionType if Qgis.versionInt() >= 32900 else QgsActionMenu.ActionType
QGIS_AGGREGATE = Qgis.Aggregate if Qgis.versionInt() >= 33500 else QgsAggregateCalculator.Aggregate
QGIS_ANGLEUNIT = Qgis.AngleUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.AngleUnit
QGIS_ANIMATIONSTATE = Qgis.AnimationState if Qgis.versionInt() >= 33500 else QgsTemporalNavigationObject.AnimationState
QGIS_ARCGISRESTSERVICETYPE = Qgis.ArcGisRestServiceType if Qgis.versionInt() >= 32500 else QgsArcGisPortalUtils.ItemType
QGIS_AREAUNIT = Qgis.AreaUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.AreaUnit
QGIS_ATTRIBUTEACTIONTYPE = Qgis.AttributeActionType if Qgis.versionInt() >= 32900 else QgsAction.ActionType
QGIS_ATTRIBUTEEDITORTYPE = Qgis.AttributeEditorType if Qgis.versionInt() >= 33100 else QgsAttributeEditorElement.AttributeEditorType
QGIS_ATTRIBUTEFORMLAYOUT = Qgis.AttributeFormLayout if Qgis.versionInt() >= 33100 else QgsEditFormConfig.EditorLayout
QGIS_ATTRIBUTEFORMPYTHONINITCODESOURCE = Qgis.AttributeFormPythonInitCodeSource if Qgis.versionInt() >= 33100 else QgsEditFormConfig.PythonInitCodeSource
QGIS_ATTRIBUTEFORMSUPPRESSION = Qgis.AttributeFormSuppression if Qgis.versionInt() >= 33100 else QgsEditFormConfig.FeatureFormSuppress
QGIS_AVOIDINTERSECTIONSMODE = Qgis.AvoidIntersectionsMode if Qgis.versionInt() >= 32500 else QgsProject.AvoidIntersectionsMode
QGIS_BLENDMODE = Qgis.BlendMode if Qgis.versionInt() >= 32900 else QgsPainting.BlendMode
QGIS_CAPITALIZATION = Qgis.Capitalization if Qgis.versionInt() >= 32300 else QgsStringUtils.Capitalization
QGIS_CRSIDENTIFIERTYPE = Qgis.CrsIdentifierType if Qgis.versionInt() >= 33500 else QgsCoordinateReferenceSystem.IdentifierType
QGIS_CRSWKTVARIANT = Qgis.CrsWktVariant if Qgis.versionInt() >= 33500 else QgsCoordinateReferenceSystem.WktVariant
QGIS_DATAITEMPROVIDERCAPABILITY = Qgis.DataItemProviderCapability if Qgis.versionInt() >= 33500 else QgsDataProvider.DataCapability
QGIS_DATAPROVIDERREADFLAG = Qgis.DataProviderFlag if Qgis.versionInt() >= 33900 else QgsDataProvider.ReadFlag
QGIS_DISTANCEUNIT = Qgis.DistanceUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.DistanceUnit
QGIS_DISTANCEUNITTYPE = Qgis.DistanceUnitType if Qgis.versionInt() >= 32900 else QgsUnitTypes.DistanceUnitType
QGIS_FEATUREAVAILABILITY = Qgis.FeatureAvailability if Qgis.versionInt() >= 33500 else QgsFeatureSource.FeatureAvailability
QGIS_FEATUREREQUESTFILTERTYPE = Qgis.FeatureRequestFilterType if Qgis.versionInt() >= 33500 else QgsFeatureRequest.FilterType
QGIS_FEATUREREQUESTFLAG = Qgis.FeatureRequestFlag if Qgis.versionInt() >= 33500 else QgsFeatureRequest.Flag
QGIS_FEATURESYMBOLOGYEXPORT = Qgis.FeatureSymbologyExport if Qgis.versionInt() >= 33100 else QgsVectorFileWriter.SymbologyExport
QGIS_FIELDORIGIN = Qgis.FieldOrigin if Qgis.versionInt() >= 33700 else QgsFields.FieldOrigin
QGIS_FILEFILTERTYPE = Qgis.FileFilterType if Qgis.versionInt() >= 33100 else QgsProviderMetadata.FilterType
QGIS_GEOMETRYTYPE = Qgis.GeometryType if Qgis.versionInt() >= 32900 else QgsWkbTypes
QGIS_GPSFIXSTATUS = Qgis.GpsFixStatus if Qgis.versionInt() >= 32900 else QgsGpsInformation.FixStatus
QGIS_GRADIENTCOLORSOURCE = Qgis.GradientColorSource if Qgis.versionInt() >= 32300 else QgsGradientFillSymbolLayer.GradientColorType
QGIS_GRADIENTSPREAD = Qgis.GradientSpread if Qgis.versionInt() >= 32300 else QgsGradientFillSymbolLayer.GradientSpread
QGIS_GRADIENTTYPE = Qgis.GradientType if Qgis.versionInt() >= 32300 else QgsGradientFillSymbolLayer.GradientType
QGIS_GRADUATEDMETHOD = Qgis.GraduatedMethod if Qgis.versionInt() >= 32500 else QgsGraduatedSymbolRenderer.GraduatedMethod
QGIS_INVALIDGEOMETRYCHECK = Qgis.InvalidGeometryCheck if Qgis.versionInt() >= 33500 else QgsFeatureRequest.InvalidGeometryCheck
QGIS_LABELLINEPLACEMENTFLAG = Qgis.LabelLinePlacementFlag if Qgis.versionInt() >= 33100 else QgsLabeling.LinePlacementFlag
QGIS_LABELMULTILINEALIGNMENT = Qgis.LabelMultiLineAlignment if Qgis.versionInt() >= 32500 else QgsPalLayerSettings.MultiLineAlign
QGIS_LABELOFFSETTYPE = Qgis.LabelOffsetType if Qgis.versionInt() >= 32500 else QgsPalLayerSettings.OffsetType
QGIS_LABELPLACEMENT = Qgis.LabelPlacement if Qgis.versionInt() >= 32500 else QgsPalLayerSettings.Placement
QGIS_LABELPLACEMENTENGINEVERSION = Qgis.LabelPlacementEngineVersion if Qgis.versionInt() >= 32900 else QgsLabelingEngineSettings.PlacementEngineVersion
QGIS_LABELPOLYGONPLACEMENTFLAG = Qgis.LabelPolygonPlacementFlag if Qgis.versionInt() >= 33100 else QgsLabeling.PolygonPlacementFlag
QGIS_LABELPREDEFINEDPOINTPOSITION = Qgis.LabelPredefinedPointPosition if Qgis.versionInt() >= 32500 else QgsPalLayerSettings.PredefinedPointPosition
QGIS_LABELQUADRANTPOSITION = Qgis.LabelQuadrantPosition if Qgis.versionInt() >= 32500 else QgsPalLayerSettings.QuadrantPosition
QGIS_LABELINGFLAG = Qgis.LabelingFlag if Qgis.versionInt() >= 32900 else QgsLabelingEngineSettings.Flag
QGIS_LAYERFILTER = Qgis.LayerFilter if Qgis.versionInt() >= 33300 else QgsMapLayerProxyModel.Filter
QGIS_LAYERTYPE = Qgis.LayerType if Qgis.versionInt() >= 32900 else QgsMapLayerType
QGIS_LAYOUTUNIT = Qgis.LayoutUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.LayoutUnit
QGIS_LAYOUTUNITTYPE = Qgis.LayoutUnitType if Qgis.versionInt() >= 32900 else QgsUnitTypes.LayoutUnitType
QGIS_MAPLAYERACTIONFLAG = Qgis.MapLayerActionFlag if Qgis.versionInt() >= 32900 else QgsMapLayerAction.Flag
QGIS_MAPLAYERACTIONTARGET = Qgis.MapLayerActionTarget if Qgis.versionInt() >= 32900 else QgsMapLayerAction.Target
QGIS_MARKERSHAPE = Qgis.MarkerShape if Qgis.versionInt() >= 32300 else QgsSimpleMarkerSymbolLayerBase.Shape
QGIS_PICTUREFORMAT = Qgis.PictureFormat if Qgis.versionInt() >= 34000 else QgsLayoutItemPicture.Format
QGIS_POINT3DSHAPE = Qgis.Point3DShape if Qgis.versionInt() >= 33500 else QgsPoint3DSymbol.Shape
QGIS_POINTCOUNTMETHOD = Qgis.PointCountMethod if Qgis.versionInt() >= 32300 else QgsRandomMarkerFillSymbolLayer.CountMethod
QGIS_PROCESSINGALGORITHMFLAG = Qgis.ProcessingAlgorithmFlag if Qgis.versionInt() >= 33500 else QgsProcessingAlgorithm.Flag
QGIS_PROCESSINGDATETIMEPARAMETERDATATYPE = Qgis.ProcessingDateTimeParameterDataType if Qgis.versionInt() >= 33500 else QgsProcessingParameterDateTime.Type
QGIS_PROCESSINGFEATURESOURCEDEFINITIONFLAG = Qgis.ProcessingFeatureSourceDefinitionFlag if Qgis.versionInt() >= 33500 else QgsProcessingFeatureSourceDefinition.Flag
QGIS_PROCESSINGFEATURESOURCEFLAG = Qgis.ProcessingFeatureSourceFlag if Qgis.versionInt() >= 33500 else QgsProcessingFeatureSource.Flag
QGIS_PROCESSINGFIELDPARAMETERDATATYPE = Qgis.ProcessingFieldParameterDataType if Qgis.versionInt() >= 33500 else QgsProcessingParameterField.DataType
QGIS_PROCESSINGFILEPARAMETERBEHAVIOR = Qgis.ProcessingFileParameterBehavior if Qgis.versionInt() >= 33500 else QgsProcessingParameterFile.Behavior
QGIS_PROCESSINGLOGLEVEL = Qgis.ProcessingLogLevel if Qgis.versionInt() >= 33500 else QgsProcessingContext.LogLevel
QGIS_PROCESSINGNUMBERPARAMETERTYPE = Qgis.ProcessingNumberParameterType if Qgis.versionInt() >= 33500 else QgsProcessingParameterNumber.Type
QGIS_PROCESSINGPARAMETERFLAG = Qgis.ProcessingParameterFlag if Qgis.versionInt() >= 33500 else QgsProcessingParameterDefinition.Flag
QGIS_PROCESSINGPARAMETERTYPEFLAG = Qgis.ProcessingParameterTypeFlag if Qgis.versionInt() >= 33500 else QgsProcessingParameterType.ParameterFlag
QGIS_PROCESSINGPROPERTYAVAILABILITY = Qgis.ProcessingPropertyAvailability if Qgis.versionInt() >= 33500 else QgsProcessingAlgorithm.PropertyAvailability
QGIS_PROCESSINGPROVIDERFLAG = Qgis.ProcessingProviderFlag if Qgis.versionInt() >= 33500 else QgsProcessingProvider.Flag
QGIS_PROCESSINGSOURCETYPE = Qgis.ProcessingSourceType if Qgis.versionInt() >= 33500 else QgsProcessing.SourceType
QGIS_PROCESSINGTININPUTLAYERTYPE = Qgis.ProcessingTinInputLayerType if Qgis.versionInt() >= 33500 else QgsProcessingParameterTinInputLayers.Type
QGIS_PROJECTFILEFORMAT = Qgis.ProjectFileFormat if Qgis.versionInt() >= 32500 else QgsProject.FileFormat
QGIS_PROJECTREADFLAG = Qgis.ProjectReadFlag if Qgis.versionInt() >= 32500 else QgsProject.ReadFlag
QGIS_PROPERTYTYPE = Qgis.PropertyType if Qgis.versionInt() >= 33500 else QgsProperty.Type
QGIS_RASTERBANDSTATISTIC = Qgis.RasterBandStatistic if Qgis.versionInt() >= 33500 else QgsRasterBandStats.Stats
QGIS_RASTERBUILDPYRAMIDOPTION = Qgis.RasterBuildPyramidOption if Qgis.versionInt() >= 32900 else QgsRaster.RasterBuildPyramids
QGIS_RASTERCOLORINTERPRETATION = Qgis.RasterColorInterpretation if Qgis.versionInt() >= 32900 else QgsRaster.ColorInterpretation
QGIS_RASTERDRAWINGSTYLE = Qgis.RasterDrawingStyle if Qgis.versionInt() >= 32900 else QgsRaster.DrawingStyle
QGIS_RASTEREXPORTTYPE = Qgis.RasterExportType if Qgis.versionInt() >= 33100 else QgsRasterFileWriter.Mode
QGIS_RASTERFILEWRITERRESULT = Qgis.RasterFileWriterResult if Qgis.versionInt() >= 33100 else QgsRasterFileWriter.WriterError
QGIS_RASTERIDENTIFYFORMAT = Qgis.RasterIdentifyFormat if Qgis.versionInt() >= 32900 else QgsRaster.IdentifyFormat
QGIS_RASTERINTERFACECAPABILITY = Qgis.RasterInterfaceCapability if Qgis.versionInt() >= 33700 else QgsRasterInterface.Capability
QGIS_RASTERLAYERTYPE = Qgis.RasterLayerType if Qgis.versionInt() >= 32900 else QgsRasterLayer.LayerType
QGIS_RASTERPROVIDERCAPABILITY = Qgis.RasterProviderCapability if Qgis.versionInt() >= 33700 else QgsRasterDataProvider.ProviderCapability
QGIS_RASTERPYRAMIDFORMAT = Qgis.RasterPyramidFormat if Qgis.versionInt() >= 32900 else QgsRaster.RasterPyramidsFormat
QGIS_RELATIONSHIPSTRENGTH = Qgis.RelationshipStrength if Qgis.versionInt() >= 32700 else QgsRelation.RelationStrength
QGIS_RELATIONSHIPTYPE = Qgis.RelationshipType if Qgis.versionInt() >= 32700 else QgsRelation.RelationType
QGIS_RENDERUNIT = Qgis.RenderUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.RenderUnit
QGIS_SCALEBARALIGNMENT = Qgis.ScaleBarAlignment if Qgis.versionInt() >= 34000 else QgsScaleBarSettings.Alignment
QGIS_SCALEBARDISTANCELABELHORIZONTALPLACEMENT = Qgis.ScaleBarDistanceLabelHorizontalPlacement if Qgis.versionInt() >= 34000 else QgsScaleBarSettings.LabelHorizontalPlacement
QGIS_SCALEBARDISTANCELABELVERTICALPLACEMENT = Qgis.ScaleBarDistanceLabelVerticalPlacement if Qgis.versionInt() >= 34000 else QgsScaleBarSettings.LabelVerticalPlacement
QGIS_SCALEBARSEGMENTSIZEMODE = Qgis.ScaleBarSegmentSizeMode if Qgis.versionInt() >= 34000 else QgsScaleBarSettings.SegmentSizeMode
QGIS_SHADERCLASSIFICATIONMETHOD = Qgis.ShaderClassificationMethod if Qgis.versionInt() >= 33700 else QgsColorRampShader.ClassificationMode
QGIS_SHADERINTERPOLATIONMETHOD = Qgis.ShaderInterpolationMethod if Qgis.versionInt() >= 33700 else QgsColorRampShader.Type
QGIS_SPATIALINDEXPRESENCE = Qgis.SpatialIndexPresence if Qgis.versionInt() >= 33500 else QgsFeatureSource.SpatialIndexPresence
QGIS_STATISTIC = Qgis.Statistic if Qgis.versionInt() >= 33500 else QgsStatisticalSummary.Statistic
QGIS_STRINGSTATISTIC = Qgis.StringStatistic if Qgis.versionInt() >= 33500 else QgsStringStatisticalSummary.Statistic
QGIS_SYMBOLCOORDINATEREFERENCE = Qgis.SymbolCoordinateReference if Qgis.versionInt() >= 32300 else QgsGradientFillSymbolLayer.GradientCoordinateMode
QGIS_SYSTEMOFMEASUREMENT = Qgis.SystemOfMeasurement if Qgis.versionInt() >= 32900 else QgsUnitTypes.SystemOfMeasurement
QGIS_TEMPORALNAVIGATIONMODE = Qgis.TemporalNavigationMode if Qgis.versionInt() >= 33500 else QgsTemporalNavigationObject.NavigationMode
QGIS_TEMPORALUNIT = Qgis.TemporalUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.TemporalUnit
QGIS_TEXTCOMPONENT = Qgis.TextComponent if Qgis.versionInt() >= 32700 else QgsTextRenderer.TextPart
QGIS_TEXTHORIZONTALALIGNMENT = Qgis.TextHorizontalAlignment if Qgis.versionInt() >= 32700 else QgsTextRenderer.HAlignment
QGIS_TEXTLAYOUTMODE = Qgis.TextLayoutMode if Qgis.versionInt() >= 32700 else QgsTextRenderer.DrawMode
QGIS_TEXTORIENTATION = Qgis.TextOrientation if Qgis.versionInt() >= 32700 else QgsTextFormat.TextOrientation
QGIS_TEXTVERTICALALIGNMENT = Qgis.TextVerticalAlignment if Qgis.versionInt() >= 32700 else QgsTextRenderer.VAlignment
QGIS_UNITTYPE = Qgis.UnitType if Qgis.versionInt() >= 32900 else QgsUnitTypes.UnitType
QGIS_UPSIDEDOWNLABELHANDLING = Qgis.UpsideDownLabelHandling if Qgis.versionInt() >= 32500 else QgsPalLayerSettings.UpsideDownLabels
QGIS_VECTORPROVIDERCAPABILITY = Qgis.VectorProviderCapability if Qgis.versionInt() >= 34000 else QgsVectorDataProvider.Capability
QGIS_VECTORRENDERINGSIMPLIFICATIONFLAG = Qgis.VectorRenderingSimplificationFlag if Qgis.versionInt() >= 33700 else QgsVectorSimplifyMethod.SimplifyHint
QGIS_VECTORSIMPLIFICATIONALGORITHM = Qgis.VectorSimplificationAlgorithm if Qgis.versionInt() >= 33700 else QgsVectorSimplifyMethod.SimplifyAlgorithm
QGIS_VOLUMEUNIT = Qgis.VolumeUnit if Qgis.versionInt() >= 32900 else QgsUnitTypes.VolumeUnit
QGIS_WKBTYPE = Qgis.WkbType if Qgis.versionInt() >= 32900 else QgsWkbTypes.Type
QGIS_ZONALSTATISTIC = Qgis.ZonalStatistic if Qgis.versionInt() >= 33500 else QgsZonalStatistics.Statistic
QGIS_ZONALSTATISTICRESULT = Qgis.ZonalStatisticResult if Qgis.versionInt() >= 33500 else QgsZonalStatistics.Result
