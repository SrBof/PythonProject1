import sys

import PyQt5
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QGridLayout
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtCore import pyqtSignal, Qt


class Tablero(QWidget):
    senal_procesar = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.inicializa_gui()
        self.setMouseTracking(True)
        self.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        x = event.x()
        y = event.y()
        print(f"El mouse se mueve... está en {x},{y}")

    def mousePressEvent(self, event: QMouseEvent):
        x = event.x()
        y = event.y()

    def inicializa_gui(self) -> None:
        self.setGeometry(400, 100, 2000, 1500)
        self.setWindowTitle("Ajedrez")
        grid = QGridLayout()

        piezas = {
            0: ["torre_negra", "caballo_negro", "alfil_negro", "reina_negra", "rey_negro", "alfil_negro",
                "caballo_negro", "torre_negra"],
            1: ["peon_negro"] * 8,
            6: ["peon_blanco"] * 8,
            7: ["torre_blanca", "caballo_blanco", "alfil_blanco", "reina_blanca", "rey_blanco", "alfil_blanco",
                "caballo_blanco", "torre_blanca"]
        }

        for fila in range(8):
            for columna in range(8):
                label = QLabel("", self)
                # ------------------------------Tablero de colores-------
                if (fila + columna) % 2 == 0:
                    label.setStyleSheet("background-color: lightgrey;")
                else:
                    label.setStyleSheet("background-color: green;")
                # ---------------------------------------------------------

                # -------------------------------Posición de las piezas------------
                if fila in piezas:
                    pieza = piezas[fila][columna]
                    archivo = f"piezas/{pieza}.png"
                    pixmap = QPixmap(archivo)
                    label.setPixmap(pixmap)
                    label.setAlignment(Qt.AlignCenter)
                    label.setScaledContents(True)
                # ------------------------------------------------------------------

                # Se agrega al grid
                self.labels[fila][columna] = label
                grid.addWidget(label, fila, columna)

        self.setLayout(grid)
        print(grid.getItemPosition(5))
        print(grid.itemAtPosition(4, 4))
        print(self.labels)


class Pieza(ABC):
    def __init__(self):
        self.puntaje = 1

    @abstractmethod
    def mover(self):
        pass

    @abstractmethod
    def comer(self):
        pass


class Peon(Pieza):
    def mover(self):
        pass

    def comer(self):
        pass


if __name__ == "__main__":
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)


    sys.__excepthook__ = hook

    app = QApplication([])
    ventana = Tablero()
    ventana.show()
    sys.exit(app.exec())
