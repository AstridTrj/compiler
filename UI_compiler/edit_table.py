from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.setLineWrapMode(0)
        self.scrollbar = self.verticalScrollBar()
        self.scrollbar.setSingleStep(20)
        self.scrollbar.setValue(0)

