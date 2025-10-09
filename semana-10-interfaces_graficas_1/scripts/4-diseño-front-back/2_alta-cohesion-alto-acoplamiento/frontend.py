import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QLineEdit)
from backend import procesar_input


class Ventana(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.inicializa_gui()

    def inicializa_gui(self) -> None:

        self.etiqueta = QLabel('Ingresa una lista de números '
                               'separados por comas:', self)
        self.etiqueta.move(20, 10)
        self.etiqueta.resize(self.etiqueta.sizeHint())

        self.input = QLineEdit('', self)
        self.input.setGeometry(20, 40, 360, 20)

        self.boton = QPushButton('Ordenar', self)
        self.boton.setGeometry(20, 70, 360, 30)
        self.boton.clicked.connect(self.boton_clickeado)

        self.resultado = QLabel('', self)
        self.resultado.move(20, 100)
        self.resultado.resize(self.resultado.sizeHint())

        self.setGeometry(700, 300, 400, 150)
        self.setWindowTitle('Ordenador de números')
        self.show()

    def boton_clickeado(self) -> None:
        texto_input = self.input.text()
        texto_resultado = procesar_input(texto_input)
        self.resultado.setText(texto_resultado)
        self.resultado.resize(self.resultado.sizeHint())
        self.resultado.repaint()


if __name__ == '__main__':
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication([])
    ventana = Ventana()
    sys.exit(app.exec())
