import typing
from xml.sax.saxutils import escape, unescape

import numpy as np
from PyQt5.QtCore import QVariant

from qgis.PyQt.QtCore import Qt, QModelIndex, pyqtSignal, QMimeData, QObject
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel, QColor, QIcon, QPen
from qgis.PyQt.QtWidgets import QWidget, QComboBox, QSizePolicy, QHBoxLayout
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.PyQt import sip
from qgis._core import QgsXmlUtils
from qgis.core import QgsField, QgsPropertyDefinition, QgsProperty, QgsExpressionContext, QgsRasterLayer, \
    QgsRasterRenderer, QgsMultiBandColorRenderer, QgsHillshadeRenderer, QgsSingleBandPseudoColorRenderer, \
    QgsPalettedRasterRenderer, QgsRasterContourRenderer, QgsSingleBandColorDataRenderer, QgsSingleBandGrayRenderer, \
    QgsVectorLayer, QgsExpression, QgsExpressionContextScope, QgsRenderContext, QgsFeatureRenderer, QgsFeature
from qgis.gui import QgsFieldExpressionWidget, QgsColorButton, QgsPropertyOverrideButton

from ...externals.htmlwidgets import HTMLComboBox
from ...plotstyling.plotstyling import PlotStyle, PlotStyleButton
from ...pyqtgraph.pyqtgraph import InfiniteLine, PlotDataItem
from ...speclib.core import create_profile_field
from ...unitmodel import UnitConverterFunctionModel, BAND_NUMBER, BAND_INDEX
from ...utils import parseWavelength

WARNING_ICON = QIcon(r':/images/themes/default/mIconWarning.svg')


class SpectralProfileColorPropertyWidget(QWidget):
    """
    Widget to specify the SpectralProfile colors.

    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.mContext: QgsExpressionContext = QgsExpressionContext()
        self.mRenderContext: QgsRenderContext = QgsRenderContext()
        self.mRenderer: QgsFeatureRenderer = None
        self.mDefaultColor = QColor('green')
        self.mColorButton = QgsColorButton()
        self.mColorButton.colorChanged.connect(self.onButtonColorChanged)

        self.mColorButton.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.mPropertyOverrideButton = QgsPropertyOverrideButton()
        self.mPropertyOverrideButton.registerLinkedWidget(self.mColorButton)
        # self.mPropertyOverrideButton.aboutToShowMenu.connect(self.updateOverrideMenu)
        hl = QHBoxLayout()
        hl.addWidget(self.mColorButton)
        hl.addWidget(self.mPropertyOverrideButton)
        hl.setSpacing(2)
        hl.setContentsMargins(0, 0, 0, 0)
        self.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)
        self.setLayout(hl)

        self.mPropertyDefinition = QgsPropertyDefinition()
        self.mPropertyDefinition.setName('Profile line color')

    def updateOverrideMenu(self, *args):

        s = ""

    def setLayer(self, layer: QgsVectorLayer):

        self.mPropertyOverrideButton.registerExpressionContextGenerator(layer)
        self.mPropertyOverrideButton.setVectorLayer(layer)
        self.mPropertyOverrideButton.updateFieldLists()

        self.mContext = layer.createExpressionContext()
        feature: QgsFeature = None
        for f in layer.getFeatures():
            feature = f
            break
        if isinstance(feature, QgsFeature):
            self.mContext.setFeature(f)
            self.mRenderContext.setExpressionContext(self.mContext)
            self.mRenderer = layer.renderer().clone()
            # self.mRenderer.startRender(self.mRenderContext, layer.fields())
            # symbol = self.mRenderer.symbolForFeature(feature, self.mRenderContext)
            # scope = symbol.symbolRenderContext().expressionContextScope()
            # self.mContext.appendScope(scope)

            # self.mTMP = [renderContext, scope, symbol, renderer]
            s = ""

    def onButtonColorChanged(self, color: QColor):
        self.mPropertyOverrideButton.setActive(False)

    def setDefaultColor(self, color: QColor):
        self.mDefaultColor = QColor(color)

    def setToProperty(self, property: QgsProperty):
        assert isinstance(property, QgsProperty)

        if property.propertyType() == QgsProperty.StaticProperty:
            self.mColorButton.setColor(property.valueAsColor(self.mContext, self.mDefaultColor)[0])
            self.mPropertyOverrideButton.setActive(False)
        else:
            self.mPropertyOverrideButton.setActive(True)
            self.mPropertyOverrideButton.setToProperty(property)
        # self.mColorButton.setColor(property.valueAsColor())

    def toProperty(self) -> QgsProperty:

        if self.mPropertyOverrideButton.isActive():
            return self.mPropertyOverrideButton.toProperty()
        else:
            prop = QgsProperty()
            prop.setStaticValue(self.mColorButton.color())
            return prop


class LabelItem(QStandardItem):
    def __init__(self, *args, tooltip: str = None, **kwds):
        super().__init__(*args, *kwds)
        if tooltip is None:
            tooltip = self.text()
        self.setToolTip(tooltip)
        self.setEditable(False)


class PropertyItemGroupSignals(QObject):
    requestRemoval = pyqtSignal()
    requestPlotUpdate = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


class PropertyItemBase(QStandardItem):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def firstColumnSpanned(self) -> bool:
        return len(self.propertyRow()) == 1

    def propertyRow(self) -> typing.List[QStandardItem]:
        return [self]

    def readXml(self, parentNode: QDomElement):
        pass

    def writeXml(self, parentNode: QDomElement, doc: QDomDocument):
        pass

    def model(self) -> QStandardItemModel:
        return super().model()


class PropertyItemGroup(PropertyItemBase):
    XML_FACTORIES: typing.Dict[str, 'PropertyItemGroup'] = dict()

    @staticmethod
    def registerXmlFactory(grp: 'PropertyItemGroup', xml_tag: str = None):
        assert isinstance(grp, PropertyItemGroup)
        if xml_tag is None:
            xml_tag = grp.__class__.__name__
        assert xml_tag not in PropertyItemGroup.XML_FACTORIES.keys()
        PropertyItemGroup.XML_FACTORIES[xml_tag] = grp.__class__

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.mMissingValues: bool = False
        self.mZValue = 0
        self.mSignals = PropertyItemGroupSignals()
        self.mFirstColumnSpanned = True

    def zValue(self) -> int:
        return self.mZValue

    def plotDataItems(self) -> typing.List[PlotDataItem]:
        """
        Returns a list with all pyqtgraph plot data items
        """
        return []

    def initWithProfilePlotModel(self, model):
        """
        This method is called
        """
        pass

    def propertyItems(self) -> typing.List['PropertyItem']:
        items = []
        for r in range(self.rowCount()):
            child = self.child(r, 1)
            if isinstance(child, PropertyItem):
                items.append(child)
        return items

    def initBasicSettings(self):
        self.setCheckable(True)
        self.setCheckState(Qt.Checked)
        self.setUserTristate(False)
        self.setDropEnabled(False)
        self.setDragEnabled(False)

        # connect requestPlotUpdate signal
        for propertyItem in self.propertyItems():
            propertyItem: PropertyItem
            propertyItem.signals().requestPlotUpdate.connect(self.signals().requestPlotUpdate.emit)

    def signals(self) -> PropertyItemGroupSignals:
        return self.mSignals

    def __hash__(self):
        return hash(id(self))

    def setValuesMissing(self, missing: bool):
        self.mMissingValues = missing

    def setCheckState(self, checkState: Qt.CheckState) -> None:
        super().setCheckState(checkState)

        c = QColor() if self.isVisible() else QColor('grey')

        for r in range(self.rowCount()):
            self.child(r, 0).setForeground(c)

    def setVisible(self, visible: bool):
        if visible in [Qt.Checked, visible is True]:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

    def isVisible(self) -> bool:
        """
        Returns True if plot items related to this control item should be visible in the plot
        """
        return self.checkState() == Qt.Checked

    def data(self, role: int = ...) -> typing.Any:
        if role == Qt.UserRole:
            return self
        if role == Qt.ForegroundRole:
            if not self.isVisible():
                return QColor('grey')
        if role == Qt.DecorationRole and self.mMissingValues:
            return QIcon(WARNING_ICON)

        return super().data(role)

    def setData(self, value: typing.Any, role: int = ...) -> None:
        super().setData(value, role)

        if role == Qt.CheckStateRole:
            # self.mSignals.requestPlotUpdate.emit()
            is_visible = self.isVisible()
            for item in self.plotDataItems():
                item.setVisible(is_visible)

    def update(self):
        pass

    MIME_TYPE = 'application/SpectralProfilePlot/PropertyItems'

    @staticmethod
    def toMimeData(propertyGroups: typing.List['PropertyItemGroup']):

        for g in propertyGroups:
            assert isinstance(g, PropertyItemGroup)

        md = QMimeData()

        doc = QDomDocument()
        root = doc.createElement('PropertyItemGroups')
        for grp in propertyGroups:
            for xml_tag, cl in PropertyItemGroup.XML_FACTORIES.items():
                if cl == grp.__class__:
                    grpNode = doc.createElement(xml_tag)
                    grp.writeXml(grpNode, doc)
                    root.appendChild(grpNode)
                    break

        doc.appendChild(root)
        md.setData(PropertyItemGroup.MIME_TYPE, doc.toByteArray())
        return md

    @staticmethod
    def fromMimeData(mimeData: QMimeData) -> typing.List['ProfileVisualization']:
        groups = []
        if mimeData.hasFormat(PropertyItemGroup.MIME_TYPE):
            ba = mimeData.data(PropertyItemGroup.MIME_TYPE)
            doc = QDomDocument()
            doc.setContent(ba)
            root = doc.firstChildElement('PropertyItemGroups')
            if not root.isNull():
                grpNode = root.firstChild().toElement()
                while not grpNode.isNull():
                    classname = grpNode.nodeName()
                    class_ = PropertyItemGroup.XML_FACTORIES.get(classname)
                    if class_:
                        grp = class_()
                        if isinstance(grp, PropertyItemGroup):
                            grp.readXml(grpNode)
                        groups.append(grp)
                    grpNode = grpNode.nextSibling()
        return groups


class PropertyLabel(QStandardItem):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setCheckable(False)
        self.setEditable(False)
        self.setDropEnabled(False)
        self.setDragEnabled(False)
        s = ""


class PropertyItemSignals(QObject):
    requestPlotUpdate = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


class PropertyItem(PropertyItemBase):

    def __init__(self, key: str, *args, labelName: str = None, **kwds):
        super().__init__(*args, **kwds)
        assert isinstance(key, str) and ' ' not in key
        self.mKey = key
        self.setEditable(False)
        self.setDragEnabled(False)
        self.setDropEnabled(False)
        if labelName is None:
            labelName = key
        self.mLabel = PropertyLabel(labelName)
        self.mSignals = PropertyItemSignals()

    def signals(self):
        return self.mSignals

    def speclib(self) -> QgsVectorLayer:
        model = self.model()
        from ...speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotModel
        if isinstance(model, SpectralProfilePlotModel):
            return model.speclib()
        else:
            return model

    def createEditor(self, parent):

        return None

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        pass

    def setModelData(self, w, bridge, index):
        pass

    def key(self) -> str:
        return self.mKey

    def label(self) -> PropertyLabel:
        return self.mLabel

    def data(self, role: int = ...) -> typing.Any:
        if role == Qt.UserRole:
            return self

        return super().data(role)

    def propertyRow(self) -> typing.List[QStandardItem]:
        return [self.label(), self]

    def writeXml(self, parentNode: QDomElement, doc: QDomDocument, attribute: bool = False):
        xml_tag = self.key()
        if attribute:
            parentNode.setAttribute(xml_tag, self.text())
        else:
            node = doc.createElement(xml_tag)
            node.setNodeValue(self.text())
            parentNode.appendChild(node)

    def readXml(self, parentNode: QDomElement, attribute: bool = False):
        xml_tag = self.key()
        if attribute:
            if parentNode.hasAttribute(xml_tag):
                self.setText(parentNode.attribute(xml_tag))
        else:
            node = parentNode.firstChildElement(xml_tag)
            if not node.isNull():
                self.setText(node.nodeValue())


class PlotStyleItem(PropertyItem):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.mPlotStyle = PlotStyle()
        self.setEditable(True)

    def setPlotStyle(self, plotStyle):
        self.mPlotStyle = plotStyle
        self.emitDataChanged()
        self.signals().requestPlotUpdate.emit()

    def plotStyle(self) -> PlotStyle:
        return self.mPlotStyle

    def createEditor(self, parent):
        w = PlotStyleButton(parent=parent)
        w.setMinimumSize(5, 5)
        w.setPlotStyle(self.plotStyle())
        w.setColorWidgetVisibility(False)
        w.setVisibilityCheckboxVisible(False)
        w.setToolTip('Set curve style')
        return w

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        if isinstance(editor, PlotStyleButton):
            editor.setPlotStyle(self.plotStyle())

    def setModelData(self, w, bridge, index):
        if isinstance(w, PlotStyleButton):
            self.setPlotStyle(w.plotStyle())

    def writeXml(self, parentNode: QDomElement, doc: QDomDocument, attribute: bool = False):
        xml_tag = self.key()
        node = doc.createElement(xml_tag)
        self.mPlotStyle.writeXml(node, doc)
        parentNode.appendChild(node)

    def readXml(self, parentNode: QDomElement, attribute: bool = False):
        node = parentNode.firstChildElement(self.key()).toElement()
        if not node.isNull():
            style = PlotStyle.readXml(node)
            if isinstance(style, PlotStyle):
                self.setPlotStyle(style)


class FieldItem(PropertyItem):
    def __init__(self, *args, **kwds):
        self.mField: QgsField = None
        super().__init__(*args, **kwds)

        self.setEditable(True)

    def field(self) -> QgsField:
        return self.mField

    def data(self, role: int = ...) -> typing.Any:

        b = isinstance(self.field(), QgsField)
        if role == Qt.DisplayRole:
            return self.field().name() if b else '<not set>'

        if role == Qt.ForegroundRole:
            return None if b else QColor('red')

        return super().data(role)

    def setField(self, field: QgsField):
        assert isinstance(field, QgsField)
        self.mField = field
        self.emitDataChanged()

    def createEditor(self, parent):
        w = HTMLComboBox(parent=parent)
        model = self.model()

        from ...speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotModel
        if isinstance(model, SpectralProfilePlotModel):
            w.setModel(model.profileFieldsModel())
        w.setToolTip('Select a field with profile data')
        return w

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        model = self.model()
        if isinstance(editor, QComboBox) and isinstance(self.field(), QgsField):

            idx = editor.model().indexFromName(self.field().name()).row()
            if idx == -1:
                idx = 0
            editor.setCurrentIndex(idx)

    def setModelData(self, w, bridge, index):
        if isinstance(w, QComboBox):
            i = w.currentIndex()
            if i >= 0:
                field: QgsField = w.model().fields().at(i)
                self.setField(field)

    def writeXml(self, parentNode: QDomElement, doc: QDomDocument, attribute: bool = False):
        field: QgsField = self.field()
        if attribute:
            fieldNode = parentNode
        else:
            fieldNode = doc.createElement('field')

        fieldNode.setAttribute('name', field.name())
        fieldNode.setAttribute('typeName', field.typeName())
        fieldNode.setAttribute('type', field.type())
        fieldNode.setAttribute('prec', field.precision())
        fieldNode.setAttribute('subType', field.subType())
        fieldNode.setAttribute('comment', field.comment())
        if not attribute:
            parentNode.appendChild(fieldNode)

    def readXml(self, parentNode: QDomElement, attribute: bool = False):

        if attribute:
            fieldNode = parentNode
        else:
            fieldNode = parentNode.firstChildElement('field')

        if not fieldNode.isNull():
            fname = fieldNode.attribute('name')
            ftype = int(fieldNode.attribute('type'))
            ftypeName = fieldNode.attribute('typeName')
            field = QgsField(name=fname,
                             type=ftype,
                             typeName=ftypeName,
                             len=flen,
                             prec=fprec,
                             comment=fcomment,
                             subType=fsubType)
            self.setField(field)


class QgsPropertyItem(PropertyItem):

    def __init__(self, *args, **kwds):
        self.mProperty = None
        super().__init__(*args, **kwds)
        self.mProperty: QgsProperty = None
        self.mDefinition: QgsPropertyDefinition = None
        self.setEditable(True)

        self.mIsSpectralProfileField: bool = False


    def __eq__(self, other):
        return isinstance(other, QgsPropertyItem) \
               and self.mDefinition == other.definition() \
               and self.mProperty == other.property()

    def update(self):
        self.setText(self.mProperty.valueAsString(QgsExpressionContext()))

    def writeXml(self, parentNode: QDomElement, doc: QDomDocument, attribute: bool = False):
        xml_tag = self.key()
        node = QgsXmlUtils.writeVariant(self.property(), doc)
        node.setTagName(xml_tag)
        parentNode.appendChild(node)

    def readXml(self, parentNode: QDomElement, attribute: bool = False) -> bool:

        xml_tag = self.key()
        child = parentNode.firstChildElement(xml_tag).toElement()
        if not child.isNull():
            property = QgsXmlUtils.readVariant(child)
            if isinstance(property, QgsProperty):
                # workaround https://github.com/qgis/QGIS/issues/47127
                property.setActive(True)
                self.setProperty(property)
                return True
        return False

    def property(self) -> QgsProperty:
        return self.mProperty

    def setProperty(self, property: QgsProperty):
        assert isinstance(property, QgsProperty)
        assert isinstance(self.mDefinition, QgsPropertyDefinition), 'Call setDefinition(propertyDefinition) first'
        self.mProperty = property
        self.emitDataChanged()
        self.signals().requestPlotUpdate.emit()

    def setDefinition(self, propertyDefinition: QgsPropertyDefinition):
        assert isinstance(propertyDefinition, QgsPropertyDefinition)
        assert self.mDefinition is None, 'property definition is immutable and already set'
        self.mDefinition = propertyDefinition
        self.label().setText(propertyDefinition.name())
        self.label().setToolTip(propertyDefinition.comment())

    def definition(self) -> QgsPropertyDefinition:
        return self.mDefinition

    def data(self, role: int = ...) -> typing.Any:

        if self.mProperty is None:
            return None
        p = self.property()

        if role == Qt.DisplayRole:
            if p.propertyType() == QgsProperty.ExpressionBasedProperty:
                return p.expressionString()
            elif p.propertyType() == QgsProperty.FieldBasedProperty:
                return p.field()
            else:
                v, success = p.value(QgsExpressionContext())
                if success:
                    if isinstance(v, QColor):
                        return v.name()
                    else:
                        return v
        if role == Qt.DecorationRole:
            if self.isColorProperty():
                v, success = p.value(QgsExpressionContext())
                if success and isinstance(v, QColor):
                    return v

        if role == Qt.ToolTipRole:
            return self.definition().description()

        return super().data(role)

    def setIsProfileFieldProperty(self, b:bool):
        self.mIsSpectralProfileField = b is True

    def isProfileFieldProperty(self) -> bool:
        return self.mIsSpectralProfileField

    def isColorProperty(self) -> bool:
        return self.definition().standardTemplate() in [QgsPropertyDefinition.ColorWithAlpha,
                                                        QgsPropertyDefinition.ColorNoAlpha]

    def createEditor(self, parent):
        speclib: QgsVectorLayer = self.speclib()
        if self.isColorProperty():
            w = SpectralProfileColorPropertyWidget(parent=parent)
        elif self.isProfileFieldProperty():

            w = HTMLComboBox(parent=parent)
            model = self.model()
            from ...speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotModel
            if isinstance(model, SpectralProfilePlotModel):
                w.setModel(model.profileFieldsModel())
            w.setToolTip(self.definition().description())

        else:
            w = QgsFieldExpressionWidget(parent=parent)
            w.setAllowEmptyFieldName(True)
            w.setExpressionDialogTitle(self.definition().name())
            w.setToolTip(self.definition().description())
            w.setExpression(self.property().expressionString())

            if isinstance(speclib, QgsVectorLayer):
                w.setLayer(speclib)
        return w

    def setEditorData(self, editor: QWidget, index: QModelIndex):

        speclib: QgsVectorLayer = self.speclib()

        if isinstance(editor, QgsFieldExpressionWidget):
            editor.setProperty('lastexpr', self.property().expressionString())
            if isinstance(speclib, QgsVectorLayer):
                editor.setLayer(speclib)
        elif isinstance(editor, SpectralProfileColorPropertyWidget):
            editor.setToProperty(self.property())
            if isinstance(speclib, QgsVectorLayer):
                editor.setLayer(speclib)

        elif self.isProfileFieldProperty() and isinstance(editor, QComboBox):
            fieldName = self.property().field()
            idx = editor.model().indexFromName(fieldName).row()
            if idx == -1:
                idx = 0
            editor.setCurrentIndex(idx)

    def setModelData(self, w, bridge, index):
        if isinstance(w, QgsFieldExpressionWidget):
            expr = w.asExpression()
            if w.isValidExpression() or expr == '' and w.allowEmptyFieldName():
                #  _p = w.property('')
                self.property().setExpressionString(expr)
        elif isinstance(w, SpectralProfileColorPropertyWidget):
            self.setProperty(w.toProperty())
        elif self.isProfileFieldProperty() and isinstance(w, QComboBox):
                i = w.currentIndex()
                if i >= 0:
                    field: QgsField = w.model().fields().at(i)
                    self.property().setField(field.name())
        self.signals().requestPlotUpdate.emit()


class ProfileCandidateItem(PlotStyleItem):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.label().setCheckable(True)
        self.label().setCheckState(Qt.Checked)
        self.mCellKey: typing.Tuple[int, str] = None

        from .spectrallibraryplotitems import SpectralProfilePlotDataItem
        self.mPlotItem = SpectralProfilePlotDataItem()

    def setCellKey(self, fid: int, field: str):
        self.mCellKey = (fid, field)
        self.label().setText(f'{fid} {field}')

    def cellKey(self) -> typing.Tuple[int, str]:
        return self.mCellKey

    def plotItem(self) -> PlotDataItem:
        return self.mPlotItem


class ProfileCandidates(PropertyItemGroup):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.mZValue = 1
        self.setIcon(QIcon(':/qps/ui/icons/profile_candidate.svg'))
        self.setData('Profile Candidates', Qt.DisplayRole)
        self.setData('Defines the style of temporary profiles candidates', Qt.ToolTipRole)
        self.mIsVisible: bool = True
        self.mDefaultPlotStyle = PlotStyleItem('DEFAULT')
        self.mDefaultPlotStyle.label().setText('Style')
        self.mDefaultPlotStyle.label().setToolTip('Default plot style of temporary profiles before they '
                                                  'are added into the spectral library')
        # self.appendRow(self.mDefaultPlotStyle.propertyRow())
        self.mCandidateStyleItems: typing.Dict[typing.Tuple[int, str], PlotStyleItem] = dict()

        self.initBasicSettings()
        self.mMissingValues = False
        # self.setEditable(False)

    def plotDataItems(self) -> typing.List[PlotDataItem]:
        return [item.plotItem() for item in self.candidateItems()]

    def syncCandidates(self):

        temp_fids = [fid for fid in self.model().speclib().allFeatureIds() if fid < 0]
        to_remove = [k for k in self.mCandidateStyleItems.keys() if k[0] not in temp_fids]
        self.removeCandidates(to_remove)
        s = ""

    def setCandidates(self, candidateStyles: typing.Dict[typing.Tuple[int, str], PlotStyle]):
        self.clearCandidates()
        i = 0
        for (fid, field), style in candidateStyles.items():
            i += 1
            item = ProfileCandidateItem(f'Candidate{i}')
            item.setCellKey(fid, field)
            item.label().setCheckable(True)
            item.label().setCheckState(Qt.Checked)

            item.label().setToolTip(f'Feature ID: {fid} field: {field}')
            item.setPlotStyle(style)
            self.mCandidateStyleItems[(fid, field)] = item
            self.appendRow(item.propertyRow())

    def candidateStyle(self, fid: int, field: str) -> PlotStyle:
        item = self.mCandidateStyleItems.get((fid, field), None)
        if isinstance(item, PlotStyleItem):
            return item.plotStyle()
        return None

    def candidateKeys(self) -> typing.List[typing.Tuple[int, str]]:
        return list(self.mCandidateStyleItems.keys())

    def candidateItems(self) -> typing.List[ProfileCandidateItem]:
        return list(self.mCandidateStyleItems.values())

    def candidateFeatureIds(self) -> typing.List[int]:
        return set([i[0] for i in self.candidateKeys()])

    def removeCandidates(self, candidateKeys: typing.List[typing.Tuple[int, str]]):

        to_remove = []
        for k in list(candidateKeys):
            if k in self.mCandidateStyleItems.keys():
                to_remove.append(self.mCandidateStyleItems.pop(k))

        for r in reversed(range(0, self.rowCount())):
            item = self.child(r, 1)
            if item in to_remove:
                self.takeRow(r)

        self.signals().requestPlotUpdate.emit()

    def clearCandidates(self):

        self.removeCandidates(self.mCandidateStyleItems.keys())

    def count(self) -> int:

        return len(self.mCandidateStyleItems)


class LayerBandVisualization(PropertyItemGroup):

    def __init__(self, *args, layer: QgsRasterLayer = None, **kwds):
        super().__init__(*args, **kwds)
        self.mZValue = 0
        self.setIcon(QIcon(':/images/themes/default/rendererCategorizedSymbol.svg'))
        self.setData('Renderer', Qt.DisplayRole)
        self.setData('Raster Layer Renderer', Qt.ToolTipRole)

        # self.mPropertyNames[LayerRendererVisualization.PIX_TYPE] = 'Renderer'
        # self.mPropertyTooltips[LayerRendererVisualization.PIX_TYPE] = 'raster layer renderer type'

        self.mLayer: QgsRasterLayer = None
        self.mUnitConverter: UnitConverterFunctionModel = UnitConverterFunctionModel()
        self.mIsVisible: bool = True

        self.mBarR: InfiniteLine = InfiniteLine(pos=1, angle=90, movable=True)
        self.mBarB: InfiniteLine = InfiniteLine(pos=2, angle=90, movable=True)
        self.mBarG: InfiniteLine = InfiniteLine(pos=3, angle=90, movable=True)
        self.mBarA: InfiniteLine = InfiniteLine(pos=3, angle=90, movable=True)

        self.mXUnit: str = BAND_NUMBER
        self.mBarR.sigPositionChangeFinished.connect(self.updateToRenderer)
        self.mBarG.sigPositionChangeFinished.connect(self.updateToRenderer)
        self.mBarB.sigPositionChangeFinished.connect(self.updateToRenderer)
        self.mBarA.sigPositionChangeFinished.connect(self.updateToRenderer)

        self.mItemRenderer = PropertyItem('Renderer')
        self.mItemBandR = PropertyItem('Red')
        self.mItemBandG = PropertyItem('Green')
        self.mItemBandB = PropertyItem('Blue')
        self.mItemBandA = PropertyItem('Alpha')

        for item in self.bandPlotItems():
            item.setVisible(False)

        if isinstance(layer, QgsRasterLayer):
            self.setLayer(layer)

        self.initBasicSettings()
        self.updateLayerName()

    def updateBarVisiblity(self):
        model = self.model()
        from ...speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotModel
        if isinstance(model, SpectralProfilePlotModel):
            plotItem = model.mPlotWidget.plotItem
            for bar in self.bandPlotItems():

                if True:
                    if bar.isVisible() and bar not in plotItem.items:
                        plotItem.addItem(bar)
                    elif not bar.isVisible() and bar in plotItem.items:
                        plotItem.removeItem(bar)
                else:
                    if bar not in plotItem.items:
                        plotItem.addItem(bar)
                    bar.setEnabled(bar.isVisible())

            s = ""

    def initWithProfilePlotModel(self, model):
        from ...speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotModel
        assert isinstance(model, SpectralProfilePlotModel)
        self.setXUnit(model.xUnit())
        # self.updateBarVisiblity()
        for bar in self.bandPlotItems():
            model.mPlotWidget.plotItem.addItem(bar)

    def clone(self) -> QStandardItem:
        item = LayerBandVisualization()
        item.setLayer(self.layer())
        item.setVisible(self.isVisible())
        return item

    def setXUnit(self, xUnit: str):
        self.mXUnit = xUnit
        self.updateFromRenderer()

    def layer(self) -> QgsRasterLayer:
        return self.mLayer

    def setLayer(self, layer: QgsRasterLayer):

        if layer == self.mLayer:
            return

        if isinstance(self.mLayer, QgsRasterLayer) and layer is None:
            self.onLayerRemoved()

        if isinstance(self.mLayer, QgsRasterLayer):
            self.disconnectLayer()

        assert isinstance(layer, QgsRasterLayer)
        self.mLayer = layer
        layer.rendererChanged.connect(self.updateFromRenderer)
        layer.willBeDeleted.connect(self.onLayerRemoved)
        layer.nameChanged.connect(self.updateLayerName)
        # layer.destroyed.connect(self.onLayerRemoved)

        self.updateFromRenderer()
        self.updateLayerName()

    def onLayerRemoved(self):
        if isinstance(self.mLayer, QgsRasterLayer):
            self.disconnectLayer()
            self.signals().requestRemoval.emit()

    def disconnectLayer(self):
        # if isinstance(self.mLayer, QgsRasterLayer):
        #    self.mLayer.rendererChanged.disconnect(self.updateFromRenderer)
        #    self.mLayer.willBeDeleted.disconnect(self.onLayerRemoved)
        #    # self.mLayer.destroyed.disconnect(self.onLayerRemoved)
        self.mLayer = None

    def updateToRenderer(self):
        if not (isinstance(self.mLayer, QgsRasterLayer) and self.mLayer.renderer(), QgsRasterRenderer):
            return
        renderer: QgsRasterRenderer = self.mLayer.renderer().clone()

        if self.mBarA.isVisible():
            bandA = self.xValueToBand(self.mBarA.pos().x())
            if bandA:
                renderer.setAlphaBand(bandA)

        bandR = self.xValueToBand(self.mBarR.pos().x())
        if isinstance(renderer, QgsMultiBandColorRenderer):
            bandG = self.xValueToBand(self.mBarG.pos().x())
            bandB = self.xValueToBand(self.mBarB.pos().x())
            if bandR:
                renderer.setRedBand(bandR)
            if bandG:
                renderer.setGreenBand(bandG)
            if bandB:
                renderer.setBlueBand(bandB)

        elif isinstance(renderer, (QgsHillshadeRenderer, QgsSingleBandPseudoColorRenderer)):
            if bandR:
                renderer.setBand(bandR)
        elif isinstance(renderer, QgsPalettedRasterRenderer):
            pass
        elif isinstance(renderer, QgsRasterContourRenderer):
            if bandR:
                renderer.setInputBand(bandR)
        elif isinstance(renderer, QgsSingleBandColorDataRenderer):
            pass
        elif isinstance(renderer, QgsSingleBandGrayRenderer):
            if bandR:
                renderer.setGrayBand(bandR)

        self.layer().setRenderer(renderer)
        self.layer().triggerRepaint()
        # convert to band unit

    def xValueToBand(self, pos: float) -> int:
        if not isinstance(self.mLayer, QgsRasterLayer):
            return None

        band = None
        if self.mXUnit == BAND_NUMBER:
            band = int(round(pos))
        elif self.mXUnit == BAND_INDEX:
            band = int(round(pos)) + 1
        else:
            wl, wlu = parseWavelength(self.mLayer)
            if wlu:
                func = self.mUnitConverter.convertFunction(self.mXUnit, wlu)
                new_wlu = func(pos)
                if new_wlu is not None:
                    band = np.argmin(np.abs(wl - new_wlu)) + 1
        if isinstance(band, int):
            band = max(band, 0)
            band = min(band, self.mLayer.bandCount())
        return band

    def bandToXValue(self, band: int) -> float:

        if not isinstance(self.mLayer, QgsRasterLayer):
            return None

        if self.mXUnit == BAND_NUMBER:
            return band
        elif self.mXUnit == BAND_INDEX:
            return band - 1
        else:
            wl, wlu = parseWavelength(self.mLayer)
            if wlu:
                func = self.mUnitConverter.convertFunction(wlu, self.mXUnit)
                return func(wl[band - 1])

        return None

    def setData(self, value: typing.Any, role: int = ...) -> None:
        super(LayerBandVisualization, self).setData(value, role)

    def plotDataItems(self) -> typing.List[PlotDataItem]:
        """
        Returns the activated plot data items
        Note that bandPlotItems() returns all plot items, even those that are not used and should be hidden.
        """
        plotItems = []

        activeItems = self.propertyItems()
        if self.mItemBandR in activeItems:
            plotItems.append(self.mBarR)
        if self.mItemBandG in activeItems:
            plotItems.append(self.mBarG)
        if self.mItemBandB in activeItems:
            plotItems.append(self.mBarR)
        if self.mItemBandA in activeItems:
            plotItems.append(self.mBarA)

        return plotItems

    def setBandPosition(self, band: int, bandBar: InfiniteLine, bandItem: PropertyItem) -> bool:
        bandBar.setToolTip(bandBar.name())
        bandItem.setData(band, Qt.DisplayRole)
        if isinstance(band, int) and band > 0:
            xValue = self.bandToXValue(band)
            if xValue:
                bandBar.setPos(xValue)
                return True
        return False

    def updateLayerName(self):
        if isinstance(self.layer(), QgsRasterLayer):
            self.setText(self.layer().name())
        else:
            self.setText('<layer not set>')

    def updateFromRenderer(self):

        for r in reversed(range(self.rowCount())):
            self.takeRow(r)

        is_checked = self.isVisible()
        if not (isinstance(self.mLayer, QgsRasterLayer)
                and isinstance(self.mLayer.renderer(), QgsRasterRenderer)):
            for b in self.bandPlotItems():
                b.setVisible(False)

            self.setValuesMissing(True)
            # self.updateBarVisiblity()
            return
        else:
            self.setValuesMissing(False)

        layerName = self.mLayer.name()
        renderer = self.mLayer.renderer()
        renderer: QgsRasterRenderer
        rendererName = renderer.type()

        bandR = bandG = bandB = bandA = None

        if renderer.alphaBand() > 0:
            bandA = renderer.alphaBand()

        is_rgb = False
        if isinstance(renderer, QgsMultiBandColorRenderer):
            # rendererName = 'Multi Band Color'
            bandR = renderer.redBand()
            bandG = renderer.greenBand()
            bandB = renderer.blueBand()
            is_rgb = True
        elif isinstance(renderer, (QgsSingleBandGrayRenderer,
                                   QgsPalettedRasterRenderer,
                                   QgsHillshadeRenderer,
                                   QgsRasterContourRenderer,
                                   QgsSingleBandColorDataRenderer,
                                   QgsSingleBandPseudoColorRenderer)
                        ):

            self.mBarR.setPen(color='grey')

            if isinstance(renderer, QgsHillshadeRenderer):
                bandR = renderer.band()
            elif isinstance(renderer, QgsPalettedRasterRenderer):
                bandR = renderer.band()
                # rendererName = 'Paletted Raster Renderer'
            elif isinstance(renderer, QgsRasterContourRenderer):
                bandR = renderer.inputBand()
                # rendererName = 'Raster Contour'
            elif isinstance(renderer, QgsSingleBandColorDataRenderer):
                bandR = None
                # rendererName = 'Single Band Color'
                # todo
            elif isinstance(renderer, QgsSingleBandGrayRenderer):
                bandR = renderer.grayBand()
                # rendererName = 'Single Band Gray'
        emptyPen = QPen()

        self.mItemRenderer.setText(rendererName)

        if len(renderer.usesBands()) >= 3:
            self.mBarR.setName(f'{layerName} red band {bandR}')
            self.mItemBandR.label().setText('Red')
            self.mBarG.setName(f'{layerName} green band {bandG}')
            self.mBarB.setName(f'{layerName} blue band {bandB}')
            self.mBarR.setPen(color='red')
            self.mBarG.setPen(color='green')
            self.mBarB.setPen(color='blue')

        else:
            self.mBarR.setName(f'{layerName} band {bandR}')
            self.mBarR.setPen(color='grey')
            self.mItemBandR.label().setText('Band')

        self.mBarA.setName(f'{layerName} alpha band {bandA}')

        self.mBarR.setVisible(is_checked and self.setBandPosition(bandR, self.mBarR, self.mItemBandR))
        self.mBarG.setVisible(is_checked and self.setBandPosition(bandG, self.mBarG, self.mItemBandG))
        self.mBarB.setVisible(is_checked and self.setBandPosition(bandB, self.mBarB, self.mItemBandB))
        self.mBarA.setVisible(is_checked and self.setBandPosition(bandA, self.mBarA, self.mItemBandA))

        self.appendRow(self.mItemRenderer.propertyRow())
        if bandR:
            self.appendRow(self.mItemBandR.propertyRow())
        if bandG:
            self.appendRow(self.mItemBandG.propertyRow())
        if bandB:
            self.appendRow(self.mItemBandB.propertyRow())
        if bandA:
            self.appendRow(self.mItemBandA.propertyRow())

        # self.updateBarVisiblity()

    def bandPositions(self) -> dict:
        pass

    def bandPlotItems(self) -> typing.List[InfiniteLine]:
        return [self.mBarR, self.mBarG, self.mBarB, self.mBarA]


class ProfileVisualization(PropertyItemGroup):
    MIME_TYPE = 'application/SpectralProfilePlotVisualization'

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.mZValue = 2
        self.setName('Visualization')
        self.setIcon(QIcon(':/qps/ui/icons/profile.svg'))
        self.mFirstColumnSpanned = False
        self.mSpeclib: QgsVectorLayer = None

        self.mPField = QgsPropertyItem('Field')
        self.mPField.setDefinition(QgsPropertyDefinition(
            'Field', 'Name of the field that contains the spectral profiles',
            QgsPropertyDefinition.StandardPropertyTemplate.String))
        self.mPField.setProperty(QgsProperty.fromField('profiles', True))

        self.mPStyle = PlotStyleItem('Style')
        self.mPLabel = QgsPropertyItem('Label')
        self.mPLabel.setDefinition(QgsPropertyDefinition(
            'Label', 'A label to describe the plotted profiles',
            QgsPropertyDefinition.StandardPropertyTemplate.String))
        self.mPLabel.setProperty(QgsProperty.fromExpression('$id'))

        self.mPFilter = QgsPropertyItem('Filter')
        self.mPFilter.setDefinition(QgsPropertyDefinition(
            'Filter', 'Filter for feature rows', QgsPropertyDefinition.StandardPropertyTemplate.String))
        self.mPFilter.setProperty(QgsProperty.fromExpression(''))

        self.mPColor = QgsPropertyItem('Color')
        self.mPColor.setDefinition(QgsPropertyDefinition(
            'Color', 'Color of spectral profile', QgsPropertyDefinition.StandardPropertyTemplate.ColorWithAlpha))
        self.mPColor.setProperty(QgsProperty.fromValue(QColor('white')))

        self.appendRow(self.mPField.propertyRow())
        self.appendRow(self.mPLabel.propertyRow())
        self.appendRow(self.mPFilter.propertyRow())
        self.appendRow(self.mPColor.propertyRow())
        self.appendRow(self.mPStyle.propertyRow())

        self.initBasicSettings()

    def initWithProfilePlotModel(self, model):
        self.setSpeclib(model.speclib())

    def propertyRow(self) -> typing.List[QStandardItem]:
        return [self]

    def writeXml(self, parentNode: QDomElement, doc: QDomDocument):
        # appends this visualization to a parent node

        parentNode.setAttribute('name', self.name())
        if isinstance(self.mPField.field(), QgsField):
            parentNode.setAttribute('field', self.mPField.field().name())
        parentNode.setAttribute('visible', '1' if self.isVisible() else '0')

        # add speclib node
        speclib = self.speclib()
        if isinstance(speclib, QgsVectorLayer):
            nodeSpeclib = doc.createElement('speclib')
            nodeSpeclib.setAttribute('id', self.speclib().id())
            parentNode.appendChild(nodeSpeclib)

        # add name expression node
        self.mPLabel.writeXml(parentNode, doc)
        self.mPColor.writeXml(parentNode, doc)
        self.mPFilter.writeXml(parentNode, doc)
        self.mPStyle.writeXml(parentNode, doc)

    def createExpressionContextScope(self) -> QgsExpressionContextScope:

        scope = QgsExpressionContextScope('profile_visualization')
        # todo: add scope variables
        scope.setVariable('vis_name', self.name(), isStatic=True)
        return scope

    def readXml(self, parentNode: QDomElement) -> typing.List['ProfileVisualization']:
        model = self.model()
        self.setText(parentNode.attribute('name'))
        self.setVisible(parentNode.attribute('visible').lower() in ['1', 'true', 'yes'])

        speclibNode = parentNode.firstChildElement('speclib')
        speclib: QgsVectorLayer = None
        if not speclibNode.isNull():
            # try to restore the speclib
            lyrId = speclibNode.attribute('id')
            from ...speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotModel
            if isinstance(model, SpectralProfilePlotModel):
                sl = model.project().mapLayer(lyrId)
                if isinstance(sl, QgsVectorLayer):
                    self.setSpeclib(sl)

            fieldName = parentNode.attribute('field')
            speclib = self.speclib()
            if isinstance(speclib, QgsVectorLayer) and fieldName in speclib.fields().names():
                self.setField(fieldName)
            else:
                self.setField(create_profile_field(fieldName))

            self.mPLabel.readXml(parentNode)
            self.mPFilter.readXml(parentNode)
            self.mPColor.readXml(parentNode)
            self.mPStyle.readXml(parentNode)

    def setColorProperty(self, property: QgsProperty):
        """
        Sets the color property
        :param property:
        :type property:
        :return:
        :rtype:
        """
        assert isinstance(property, QgsProperty)
        self.mPColor.setProperty(property)

    def colorProperty(self) -> QgsProperty:
        """
        Returns the color expression
        :return:
        :rtype:
        """
        return self.mPColor.property()

    def clone(self) -> 'QStandardItem':
        v = ProfileVisualization()
        return v

    def color(self, context: QgsExpressionContext = QgsExpressionContext()):
        return self.colorProperty().valueAsColor(context, self.plotStyle().lineColor())[0]

    def setColor(self, color: typing.Union[str, QColor]):
        c = QColor(color)
        self.colorProperty().setStaticValue(c)
        self.plotStyle().setLineColor(c)

    def name(self) -> str:
        """
        Returns the name of this visualization
        :return:
        """
        return self.text()

    def setName(self, name: str):
        self.setText(name)

    def setSpeclib(self, speclib: QgsVectorLayer):
        assert isinstance(speclib, QgsVectorLayer)
        self.mSpeclib = speclib
        self.update()

    def update(self):
        valuesMissing = False

        if not (isinstance(self.field(), QgsField)
                and isinstance(self.speclib(), QgsVectorLayer)
                and self.field().name() in self.speclib().fields().names()):
            valuesMissing = True
        self.setValuesMissing(valuesMissing)

        self.mPField.label().setIcon(QIcon(WARNING_ICON) if valuesMissing else QIcon())

    def speclib(self) -> QgsVectorLayer:
        return self.mSpeclib

    def isComplete(self) -> bool:
        speclib = self.speclib()
        field = self.field()
        return isinstance(speclib, QgsVectorLayer) and not sip.isdeleted(speclib) \
               and isinstance(field, QgsField) \
               and field.name() in speclib.fields().names()

    def setFilterExpression(self, expression):
        if isinstance(expression, QgsExpression):
            expression = expression.expression()
        assert isinstance(expression, str)
        self.mPFilter.property().setExpressionString(expression)
        self.mPFilter.update()
        self.update()

    def filterProperty(self) -> QgsProperty:
        """
        Returns the filter expression that describes included profiles
        :return: str
        """
        return self.mPFilter.property()

    def setLabelExpression(self, expression):
        if isinstance(expression, QgsExpression):
            expression = expression.expression()
        assert isinstance(expression, str)
        self.mPLabel.property().setExpressionString(expression)
        self.update()

    def labelProperty(self) -> QgsProperty:
        """
        Returns the expression that returns the name for a single profile
        :return: str
        """
        return self.mPLabel.property()

    def setField(self, field: typing.Union[QgsField, str]):

        if isinstance(field, str):
            speclib = self.speclib()
            assert isinstance(speclib, QgsVectorLayer), 'Speclib undefined'
            field = speclib.fields().at(speclib.fields().lookupField(field))
        assert isinstance(field, QgsField)
        self.mPField.setField(field)
        self.update()

    def field(self) -> QgsField:
        return self.mPField.field()

    def fieldName(self) -> str:
        if isinstance(self.field(), QgsField):
            return self.field().name()
        else:
            return None

    def fieldIdx(self) -> int:
        return self.speclib().fields().lookupField(self.field().name())

    def setPlotStyle(self, style: PlotStyle):
        self.mPStyle.setPlotStyle(style)
        self.update()

    def plotStyle(self) -> PlotStyle:
        return self.mPStyle.plotStyle()


PropertyItemGroup.registerXmlFactory(LayerBandVisualization())
PropertyItemGroup.registerXmlFactory(ProfileVisualization())
