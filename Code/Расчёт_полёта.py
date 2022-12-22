import numpy as np
from scipy import integrate
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(851, 576)
        MainWindow.setStyleSheet("background-color: rgb(68, 68, 68);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 170, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: rgb(255, 255, 255);\n"
                                   "background-color: rgb(0, 0, 0);")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(30, 270, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(255, 255, 255);\n"
                                   "background-color: rgb(0, 0, 0);")
        self.label_3.setObjectName("label_3")
        self.apply_btn = QtWidgets.QPushButton(self.centralwidget)
        self.apply_btn.setGeometry(QtCore.QRect(30, 420, 141, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.apply_btn.setFont(font)
        self.apply_btn.setStyleSheet("background-color: rgb(93, 155, 255);")
        self.apply_btn.setObjectName("apply_btn")
        self.apply_btn.clicked.connect(self.calculate_graphic)
        self.variance = QtWidgets.QLineEdit(self.centralwidget)
        self.variance.setGeometry(QtCore.QRect(182, 180, 131, 22))
        self.variance.setObjectName("variance")
        self.weight = QtWidgets.QLineEdit(self.centralwidget)
        self.weight.setGeometry(QtCore.QRect(182, 280, 131, 22))
        self.weight.setObjectName("weight")
        self.widget = PlotWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(350, 90, 450, 340))
        self.widget.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.widget.setObjectName("widget")
        self.widget.setBackground('w')
        self.widget.setTitle("График полёта снаряда")
        self.widget.showGrid(x=True, y=True)
        styles = {'color':'r', 'font-size':'20px'}
        self.widget.setLabel('left', 'Высота (метр)', **styles)
        self.widget.setLabel('bottom', 'Расстояние от точки запуска (метр)', **styles)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.variance.setStyleSheet("color: rgb(255, 255, 255);")
        self.weight.setStyleSheet("color: rgb(255, 255, 255);")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        from PyQt5.QtWinExtras import QtWin
        app_id = "project.catapult.ui"
        QtWin.setCurrentProcessExplicitAppUserModelID(app_id)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Кинематика катапульты"))
        self.label_2.setText(_translate("MainWindow", "Отклонение:"))
        self.label_3.setText(_translate("MainWindow", "Вес снаряда:"))
        self.apply_btn.setText(_translate("MainWindow", "Apply"))

    def draw_trajectory(self, launch_height, speed):
        D = (speed * np.sin(np.pi / 6)) ** 2 + 2 * 9.8 * launch_height
        t = (speed * np.sin(np.pi / 6) + np.sqrt(D)) / 9.8
        dist = speed * t * np.cos(np.pi / 6)
        self.variance.setText(f'Дальность полёта: {dist}')

        x = []
        y = []
        i = 0.0
        while i < t:
            x.append(speed * np.cos(np.pi / 6) * i)
            y.append(launch_height + speed * i * np.sin(np.pi / 6) - 9.8 * (i ** 2) / 2)
            i += 0.001
        x.append(speed * np.cos(np.pi / 6) * t)
        y.append(launch_height + speed * t * np.sin(np.pi / 6) - 9.8 * (t ** 2) / 2)

        self.widget.clear()
        pen = pg.mkPen(color=(0, 255, 0), width=2, style=QtCore.Qt.SolidLine)
        self.widget.plot(x, y, pen=pen)

    def momentum(self, k, lever_mass, lever_len, projectile_mass, spring_point_lev, spring_point, spring_len, angle):
        base_angle = np.pi / 3

        l1 = spring_point - spring_point_lev * np.sin(angle)
        l2 = (spring_len - spring_point_lev * np.cos(base_angle)) + spring_point_lev * np.cos(angle)
        del_x = np.sqrt(l1 ** 2 + l2 ** 2) - spring_len # удлиннение пружины

        beta_angle = np.pi / 2 - angle - np.arctan(l1 / l2) # угол между пружиной и нормалью в точке крепления пружины к ложке
        momentum = k * del_x * spring_point_lev * np.cos(beta_angle) - 9.8 * np.sin(angle) * (projectile_mass * lever_len + lever_mass * lever_len / 2)
        return momentum

    def speed(self, k, lever_mass, lever_len, projectile_mass, spring_point_lev, spring_point, spring_len, angle):
        base_angle = np.pi / 3
        func = lambda ang: self.momentum(k, lever_mass, lever_len, projectile_mass, spring_point_lev, spring_point, spring_len, ang)
        work, _ = integrate.quad(func, angle, base_angle)
        return np.sqrt(work / (lever_mass / 6 + projectile_mass / 2))

    def calculate_graphic(self):
        # угол относительно плоскости земли, на котором рычаг находится в равонвесии
        base_angle = np.pi / 3

        try:
            input_angle = float(self.variance.text()) * np.pi / 180.0  # отклонение от положения равновесия
            if input_angle < 0 or input_angle > 60:
                raise Exception("Wrong angle value (must be between 0 and 60 degrees including)")
        except Exception:
            self.variance.setText("Input must be without letters")
            return

        try:
            input_projectile_mass = float(self.weight.text()) / 1000
        except Exception:
            self.weight.setText("Input must be without letters")
            return

        k = 435.213 * 2 # совместная жёсткость двух одинаковых пружин
        spring_point_lev = 0.06351  # место прикрепления пружины на рычаге
        spring_len = 0.069 # длина пружины (между центрами крепления - для удобства расчётов)
        lever_len = 0.09506  # длина рычага
        lever_mass = 0.036  # масса рычага
        spring_point = 0.055  # место прикрепления пружины на месте крепления оси для пружин
        delta_h = 0.015  # расстояние от оси вращения рычага до земли
        launch_height = delta_h + lever_len * np.sin(base_angle) # высота, с которой запускается снаряд

        speed = self.speed(k, lever_mass, lever_len, input_projectile_mass, spring_point_lev, spring_point, spring_len, base_angle - input_angle)
        self.draw_trajectory(launch_height, speed)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('catapult.png'))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
