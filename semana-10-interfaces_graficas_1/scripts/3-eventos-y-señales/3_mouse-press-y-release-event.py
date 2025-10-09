import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QMouseEvent, QPixmap
import os



class MiVentana(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.contador = 0
        self.setGeometry(100, 100, 1200, 1200)
        #bloque 1
        self.label_bloque_1 = QLabel("Bloque 1", self)
        self.label_bloque_1.setGeometry(0, 0, 400, 400)
        click_dentro_de_label_1 = False

        # bloque 2
        self.label_bloque_2 = QLabel("Bloque 2", self)
        self.label_bloque_2.setGeometry(400, 0, 400, 400)
        click_dentro_de_label_2 = False

        # bloque 3
        self.label_bloque_3 = QLabel("Bloque 3", self)
        self.label_bloque_3.setGeometry(800, 0, 400, 400)
        click_dentro_de_label_3 = False

        #bloque 4
        self.label_bloque_4 = QLabel("Bloque 4", self)
        self.label_bloque_4.setGeometry(0, 400, 400, 400)
        click_dentro_de_label_4 = False

        # bloque 5
        self.label_bloque_5 = QLabel("Bloque 5", self)
        self.label_bloque_5.setGeometry(400, 400, 400, 400)
        click_dentro_de_label_5 = False

        # bloque 6
        self.label_bloque_6 = QLabel("Bloque 6", self)
        self.label_bloque_6.setGeometry(800, 400, 400, 400)
        click_dentro_de_label_6 = False

        # bloque 7
        self.label_bloque_7 = QLabel("Bloque 7", self)
        self.label_bloque_7.setGeometry(0, 800, 400, 400)
        click_dentro_de_label_7 = False

        # bloque 8
        self.label_bloque_8 = QLabel("Bloque 8", self)
        self.label_bloque_8.setGeometry(400, 800, 400, 400)
        click_dentro_de_label_8 = False

        # bloque 9
        self.label_bloque_9 = QLabel("Bloque 9", self)
        self.label_bloque_9.setGeometry(800, 800, 400, 400)
        click_dentro_de_label_9 = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.contador = self.contador + 1
        if self.contador % 2 != 0:
            color = "background-color: red;"
        else:
            color = "background-color: blue;"

        print(self.contador, "contador")
        # Cargamos la imagen como pixeles.

        x = event.x()
        y = event.y()
        print(f"El mouse fue presionado en {x},{y}")
        self.click_dentro_del_label_1 = self.label_bloque_1.underMouse()
        self.click_dentro_del_label_2 = self.label_bloque_2.underMouse()
        self.click_dentro_del_label_3 = self.label_bloque_3.underMouse()
        self.click_dentro_del_label_4 = self.label_bloque_4.underMouse()
        self.click_dentro_del_label_5 = self.label_bloque_5.underMouse()
        self.click_dentro_del_label_6 = self.label_bloque_6.underMouse()
        self.click_dentro_del_label_7 = self.label_bloque_7.underMouse()
        self.click_dentro_del_label_8 = self.label_bloque_8.underMouse()
        self.click_dentro_del_label_9 = self.label_bloque_9.underMouse()
        if self.click_dentro_del_label_1:
            print("\tFue presionado dentro del QLabel1")
            self.label_bloque_1.setScaledContents(True)
            self.label_bloque_1.setStyleSheet(color)
        elif self.click_dentro_del_label_2:
            print("\tFue presionado dentro del QLabel2")
            self.label_bloque_2.setStyleSheet(color)
            self.label_bloque_2.setScaledContents(True)
        elif self.click_dentro_del_label_3:
            print("\tFue presionado dentro del QLabel3")
            self.label_bloque_3.setStyleSheet(color)
            self.label_bloque_3.setScaledContents(True)
        elif self.click_dentro_del_label_4:
            print("\tFue presionado dentro del QLabel4")
            self.label_bloque_4.setStyleSheet(color)
            self.label_bloque_4.setScaledContents(True)
        elif self.click_dentro_del_label_5:
            print("\tFue presionado dentro del QLabel5")
            self.label_bloque_5.setStyleSheet(color)
            self.label_bloque_5.setScaledContents(True)
        elif self.click_dentro_del_label_6:
            print("\tFue presionado dentro del QLabel6")
            self.label_bloque_6.setStyleSheet(color)
            self.label_bloque_6.setScaledContents(True)
        elif self.click_dentro_del_label_7:
            print("\tFue presionado dentro del QLabel7")
            self.label_bloque_7.setStyleSheet(color)
            self.label_bloque_7.setScaledContents(True)
        elif self.click_dentro_del_label_8:
            print("\tFue presionado dentro del QLabel8")
            self.label_bloque_8.setStyleSheet(color)
            self.label_bloque_8.setScaledContents(True)
        elif self.click_dentro_del_label_9:
            print("\tFue presionado dentro del QLabel9")
            self.label_bloque_9.setStyleSheet(color)
            self.label_bloque_9.setScaledContents(True)
        self.show()
        if self.contador == 10:
            print("Perdiste feo ctm")
            sys.exit(app.exec())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        x = event.x()
        y = event.y()
        print(f"El mouse fue liberado en {x},{y}")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        x = event.x()
        y = event.y()
        print(f"El mouse se mueve... está en {x},{y}")


if __name__ == "__main__":
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)


    sys.__excepthook__ = hook

    app = QApplication([])
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())
