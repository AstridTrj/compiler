import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from compiler_principle import re_to_mdfa

from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QApplication)


class ReExpUI(QFrame):

    def __init__(self):
        super(ReExpUI, self).__init__()
        self.re_exp = ''  # 输入的正则式
        # 设置输入窗口，图片显示窗口，定义页面布局
        self.input_widget = QWidget(self)
        self.image_widget = QWidget(self)
        self.frame_grid = QGridLayout()
        # 在图片显示窗口中定义各图像的标签
        self.nfa_label = QLabel(self.image_widget)
        self.dfa_label = QLabel(self.image_widget)
        self.mdfa_label = QLabel(self.image_widget)
        self.image_gird = QGridLayout()
        # 设置输入口,按钮
        self.input_text = QLineEdit(self.input_widget)
        self.start_button = QPushButton(self.input_widget, text='start')
        self.input_grid = QGridLayout()
        # 所有页面布局设置
        self.layout_re_exp()
        # 设置按钮点击响应事件
        self.start_button.clicked.connect(self.btn_action)

    def layout_re_exp(self):
        # 主窗口布局
        self.frame_grid.addWidget(self.image_widget, 0, 0)
        self.frame_grid.addWidget(self.input_widget, 1, 0)
        # 设置指定行的拉伸因子
        self.frame_grid.setRowStretch(0, 4)
        self.frame_grid.setRowStretch(1, 1)

        # 为主窗口添加网格布局
        self.setLayout(self.frame_grid)

        # 图片显示区域的窗口布局
        font = QFont("STFangsong")
        font.setPointSizeF(12)
        font.setBold(True)
        label1 = QLabel("N\nF\nA")
        label1.setFont(font)
        self.image_gird.addWidget(label1, 0, 0)
        self.image_gird.addWidget(self.nfa_label, 0, 1)
        label2 = QLabel("D\nF\nA")
        label2.setFont(font)
        self.image_gird.addWidget(label2, 1, 0)
        self.image_gird.addWidget(self.dfa_label, 1, 1)
        label3 = QLabel("M\nD\nF\nA")
        label3.setFont(font)
        self.image_gird.addWidget(label3, 2, 0)
        self.image_gird.addWidget(self.mdfa_label, 2, 1)
        self.image_gird.setRowStretch(0, 1)
        self.image_gird.setRowStretch(1, 1)
        self.image_gird.setRowStretch(2, 1)
        self.image_widget.setLayout(self.image_gird)
        # 输入区域布局
        self.input_grid.addWidget(QLabel("输入正则式: "), 0, 0)
        self.input_grid.addWidget(self.input_text, 0, 1)
        self.input_grid.addWidget(self.start_button, 0, 2)
        self.input_widget.setLayout(self.input_grid)

    def btn_action(self):
        try:
            self.re_exp = re_to_mdfa.RetoMFA(text=self.input_text.text())
            self.re_exp.run()
            # Qt.KeepAspectRatio图像被缩放到一个尽可能大的矩形内尺寸，保持高宽比 IgnoreAspectRatio
            # SmoothTransformation 图片缩放无锯齿处理
            image = QImage("img/NFA.png").scaled(650, 170, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.nfa_label.setPixmap(QPixmap.fromImage(image))
            image = QImage("img/DFA.png").scaled(650, 170, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.dfa_label.setPixmap(QPixmap.fromImage(image))
            image = QImage("img/MDFA.png").scaled(650, 170, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.mdfa_label.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'ERROR', 'Error, please run again.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Re2NFA2DFA2MDFA")
    frame = ReExpUI()
    frame.resize(700, 600)
    frame.show()
    app.exec_()