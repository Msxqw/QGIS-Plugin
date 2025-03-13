import os
from .plugin_dialog import InvertDialog

from qgis.PyQt import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsFeature, QgsGeometry, QgsProject, QgsWkbTypes, QgsMapLayer

class InvertGeometry:

    def __init__(self, iface):

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.toolbar = self.iface.addToolBar(u"InvertGeometry")
        self.toolbar.setObjectName(u"InvertGeometry")
        self.first_start = True

    def initGui(self):

        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(QIcon(icon_path), u'Инвертирование геометрии', self.mainWindow())
        self.action.triggered.connect(self.run)
        self.toolbar.addAction(self.action)

    def unload(self):

        self.toolbar.removeAction(self.action)
        del self.toolbar

    def run(self):
        """Проверка на первый запуск"""

        if self.first_start == True:
            self.first_start = False
            self.dlg = InvertDialog()
            self.dlg.rejected.connect(self.reset_dialog)

        """Проверка на загрузку слоев в проекте"""

        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            self.iface.messageBar().pushSuccess("Info", "No vector layer found")
            return
        
        self.dlg.show()
        self.dlg.invertButton.clicked.connect(self.invert_geometry)
        self.dlg.useSelectedCheckBox.stateChanged.connect(lambda: self.upgate_labels(layer))

    def reset_dialog(self):
        """Сброс знаяений диалогового окна"""
        
        self.dlg.useSelectedCheckBox.setChanged(False)
        self.dlg.selectedLayerLabel.clear()
        self.dlg.featureCountLabel.clear()

    def update_labels(self, layer):
        """Обновление label-ов"""

        if layer and layer.type() == QgsMapLayer.VectorLayer:
            self.dlg.selectedLayerLabel.setText(f"{layer.name}")

            if self.dlg.useSelectedCheckBox.isChecked():
                feature_count = layer.selectedFeatureCount()
            else:
                feature_count = layer.featureCount()
            self.dlg.featureCountLabel.setText(f"{feature_count}")

    def invert_geometry(self):
        """Метод для инвертирования геометрии"""

        layer = self.iface.activelayer()
        use_selected = self.dlg.useSelectedCheckBox.isChecked()
        if use_selected:
            features = layer.selectedFeatures()
        else:
            features = layer.getFeatures()

        # Начало редактирования слоя
        layer.startEditing()

        geom_type = layer.wkbType()
        for feature in features:
            new_geom = None
            if QgsWkbTypes.isSingleType(geom_type):
                new_geom = self.invert_single_geometry(feature, geom_type)
            else:
                new_geom = self.invert_multi_geometry(feature, geom_type)

            if new_geom:
                layer.changeGeometry(feature.id(), new_geom)
            elif new_geom is None:
                self.iface.messageBar.pushSuccess("Info", "No new geometry was created")

            # Отладочное сообщение
            print(f"new_geom - {new_geom}")

        # Завершение редактирования
        layer.commitChanges()

    def invert_single_geometry(self, feature, geom_type):
        """Метод инвертирования одиночной геометрии"""

        geom = feature.geometry()
        if geom_type == QgsWkbTypes.LineString:
            line = geom.asPolyline()
            inverted_line = [point for point in reversed(line)]
            return QgsGeometry.fromPolylineXY(inverted_line)
        
        elif geom_type == QgsWkbTypes.Polygon:
            polygon = geom.asPolygon()
            inverted_polygon = [[point for point in reversed(ring)] for ring in polygon]
            return QgsGeometry.fromPolygonXY(inverted_polygon)
        
        return None
        
    def invert_multi_geometry(self, feature, geom_type):
        """Метод инвертирования мульти геометрии"""

        geom = feature.geometry()
        if geom_type == QgsWkbTypes.MultiLineString:
            multi_line = geom.asMultiPolyline()
            inverted_multi_line = [list(reversed(line)) for line in multi_line]
            return QgsGeometry.fromMultiPolylineXY(inverted_multi_line)
        
        elif geom_type == QgsWkbTypes.MultiPolygon:
            multi_polygon = geom.asMultiPolygon()
            inverted_multi_polygon = [[[point for point in reversed(ring)] for ring in polygon] for polygon in multi_polygon]
            return QgsGeometry.fromMultiPolygonXY(inverted_multi_polygon)

        return None
    