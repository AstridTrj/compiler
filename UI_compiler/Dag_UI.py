import sys

from compiler_principle import DAG_code_optimization
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QTextDocumentWriter
from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QApplication, QTextEdit, QTableWidget,
                             QAbstractItemView, QFileDialog, QTableWidgetItem, QHeaderView)


class DagUI(QFrame):

    def __init__(self):
        super(DagUI, self).__init__()
        self.dag = None
        self.filename = ""

        self.frame_grid = QGridLayout()  # 总布局

        self.left_widget = QWidget()  # 左部显示窗口和布局
        self.left_grid = QGridLayout()
        self.gra_label = QLabel("输入中间代码(一个基本快):")  # 文法输入标签
        self.grammar = QTextEdit()  # 四元式输入和显示框
        self.grammar.setFontFamily('STFangsong')
        self.grammar.setFontPointSize(12)
        self.open_file_btn = QPushButton(text="从文件导入文法")

        self.var_widget = QWidget()  # 指定活跃变量处的窗口和布局设置
        self.var_grid = QGridLayout()
        self.var_label = QLabel("指定活跃变量(空格间隔):")
        self.var_input = QLineEdit()  # 输入活跃变量
        self.start_without_var_btn = QPushButton(text="start without act-var")
        self.start_with_var_btn = QPushButton(text="start with act-var")

        self.right_widget = QWidget()  # 右部显示窗口和布局
        self.right_grid = QGridLayout()
        self.without_var_label = QLabel("不指定活跃变量的DAG图和优化后的四元式")
        self.without_var_label.setAlignment(Qt.AlignCenter)
        self.without_var_widget = QWidget()
        self.without_var_grid = QGridLayout()
        self.dag_without = QLabel("Position\nof\nDAG picture")  # 无活跃变量的dag图和优化后的四元式
        self.dag_without.setFrameShape(QFrame.Box)
        self.dag_without.setAlignment(Qt.AlignCenter)
        self.quaternary_without = QTextEdit()  # 四元式
        self.quaternary_without.setReadOnly(True)

        self.with_var_label = QLabel("指定活跃变量的DAG图和优化后的四元式")
        self.with_var_label.setAlignment(Qt.AlignCenter)
        self.with_widget = QWidget()
        self.with_grid = QGridLayout()
        self.dag_with = QLabel("Position\nof\nDAG picture")  # 指定活跃变量的dag图和优化后的四元式
        self.dag_with.setFrameShape(QFrame.Box)
        self.dag_with.setAlignment(Qt.AlignCenter)
        self.quaternary_with = QTextEdit()
        self.quaternary_with.setReadOnly(True)

        self.layout_setting()
        self.action_setting()

    def layout_setting(self):
        self.frame_grid.addWidget(self.left_widget, 0, 0)
        self.frame_grid.addWidget(self.right_widget, 0, 1)
        self.frame_grid.setColumnStretch(0, 1)
        self.frame_grid.setColumnStretch(1, 2)
        self.setLayout(self.frame_grid)

        self.left_grid.addWidget(self.gra_label, 0, 0)
        self.left_grid.addWidget(self.grammar, 1, 0)
        self.left_grid.addWidget(self.open_file_btn, 2, 0)
        self.left_grid.addWidget(self.start_without_var_btn, 3, 0)
        self.left_grid.addWidget(self.var_widget, 4, 0)
        self.left_grid.addWidget(self.start_with_var_btn, 5, 0)
        self.left_widget.setLayout(self.left_grid)

        self.var_grid.addWidget(self.var_label, 0, 0)  # 指定活跃变量窗口处布局
        self.var_grid.addWidget(self.var_input, 0, 1)
        self.var_widget.setLayout(self.var_grid)

        self.right_grid.addWidget(self.without_var_label, 0, 0)
        self.right_grid.addWidget(self.without_var_widget, 1, 0)
        self.right_grid.addWidget(self.with_var_label, 2, 0)
        self.right_grid.addWidget(self.with_widget, 3, 0)
        self.right_widget.setLayout(self.right_grid)

        self.without_var_grid.addWidget(self.dag_without, 0, 0)
        self.without_var_grid.addWidget(self.quaternary_without, 0, 1)
        self.without_var_grid.setColumnStretch(0, 1)
        self.without_var_grid.setColumnStretch(1, 1)
        self.without_var_widget.setLayout(self.without_var_grid)

        self.with_grid.addWidget(self.dag_with, 0, 0)
        self.with_grid.addWidget(self.quaternary_with, 0, 1)
        self.with_grid.setColumnStretch(0, 1)
        self.with_grid.setColumnStretch(1, 1)
        self.with_widget.setLayout(self.with_grid)

    def action_setting(self):
        self.open_file_btn.clicked.connect(self.read_quaternary)
        self.start_without_var_btn.clicked.connect(self.running_without_var)
        self.start_with_var_btn.clicked.connect(self.running_with_var)

    def read_quaternary(self):
        # 打开文法文件
        filename, _s = QFileDialog.getOpenFileName(self, "Open File", '', "All Files (*);;"
                                                                          "C++ Files (*.cpp *.h *.py);;"
                                                                          "Txt files (*.txt);;"
                                                                          "Python files (*.py);;"
                                                                          "HTML-Files (*.htm *.html)")
        if filename:  # 文件名有效时才进行打开
            self.filename = filename
            try:
                # 读取文件内容并设置显示到文法的显示窗口
                file = QFile(filename)
                if file.open(QFile.ReadOnly | QFile.Text):
                    text = file.readAll()
                    text = str(text, encoding='utf-8')
                    # 设置内容显示
                    self.grammar.setPlainText(text)
                    file.close()
                    return True
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'ERROR', 'Error, please open file again.')
        return False

    # 不指定活跃变量时的按钮响应事件处理
    def running_without_var(self):
        if self.grammar.document().isModified():
            self.write_to_file()
        if not self.filename:
            QMessageBox.information(self, 'ERROR', 'Error, please input quaternary.')
            return None
        try:
            quaternary, picture_path = DAG_code_optimization.start_no_active(self.filename)
            image = QImage(picture_path).scaled(300, 235, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.dag_without.setPixmap(QPixmap.fromImage(image))
            text = ""
            for i in quaternary:
                text = text + str(i) + "\n"
            self.quaternary_without.setPlainText(text)
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'ERROR', 'running error, do it again or select the other one file.')

    # 指定活跃变量时的按钮响应事件处理
    # 显示DAG图和优化后的四元式
    def running_with_var(self):
        if self.grammar.document().isModified():
            self.write_to_file()
        act_var = self.var_input.text()
        if not act_var:
            QMessageBox.information(self, 'ERROR', 'Please input active variable.')
            return None
        try:
            act_var = act_var.strip().split(" ")
            quaternary, picture_path = DAG_code_optimization.start_has_active(act_var)
            # 显示图片, 图片大小调试结果如下
            image = QImage(picture_path).scaled(300, 235, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.dag_with.setPixmap(QPixmap.fromImage(image))
            text = ""
            for i in quaternary:
                text = text + str(i) + "\n"
            self.quaternary_with.setPlainText(text)
        except Exception as e:
            QMessageBox.information(self, 'ERROR', str(e))

    def write_to_file(self):
        writer = QTextDocumentWriter(self.filename)
        writer.write(self.grammar.document())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("DAG-Optimize")
    frame = DagUI()
    frame.resize(1000, 600)
    frame.show()
    app.exec_()