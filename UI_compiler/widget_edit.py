from PyQt5.QtCore import (QTimer, Qt)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QTextEdit)

from TextEditRow import QCodeEditor
from compiler_principle.UI_compiler.edit_table import TextEdit


class TableEdit(QWidget):
    index = 1
    filename = ''

    def __init__(self):
        super(TableEdit, self).__init__()
        self.filename = 'Unnameed-{0}.txt'.format(TableEdit.index)
        TableEdit.index += 1
        self.initUI()

    def initUI(self):
        font = QFont()
        #
        # self.e_label = QLabel(self)
        # self.e_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        # self.e_label.setWordWrap(True)
        # self.e_label.setText("1\n")
        # self.LineCount = 1
        # self.LineNo = 1
        # self.startLine = 1

        font.setPointSize(12)
        # self.e_label.setFont(font)
        # self.e_label.setMargin(5)

        self.e_edit = QCodeEditor(self)
        self.e_edit.setFont(font)

        # self.e_edit = TextEdit(self)
        # self.e_edit.setFont(font)
        g_edit = QGridLayout()
        # g_edit.setColumnStretch(0, 2)
        # g_edit.setColumnStretch(1, 50)
        # g_edit.addWidget(self.e_label, 0, 0)
        g_edit.addWidget(self.e_edit, 0, 0)

        self.setLayout(g_edit)
        # 设置计时器定时更新文本框行数
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.updateLineNum)
        # self.timer.start(100)

    # def updateLineNum(self):
        # self.startLine = self.e_edit.scrollbar.value() // 24
        # h_c = int(self.e_edit.height() / 24.5)
        # str_l = ""
        # count = self.e_edit.document().blockCount()
        # if count < h_c:
        #     end = count
        # else:
        #     end = h_c
        # for i in range(1, end):
        #     str_l += "%3d\n" % (i + self.startLine)
        # str_l += "%3d\n" % (end + self.startLine)
        # self.e_label.setText(str_l)
