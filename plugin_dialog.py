import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'dialog.ui'))

class InvertDialog(QDialog):

    def __init__(self, parent=None):
        super(InvertDialog, self).__init__(parent)
        self.setupUi(self)
