import json
import sys
import time

import yt_dlp
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QSizeGrip,
)
from PyQt5.uic import loadUi


class Outube(QMainWindow):
    def __init__(self):
        super(Outube, self).__init__()
        loadUi(f"design/designoutube.ui", self)
        self.download_folder = None  # Variable para almacenar la carpeta de descarga
        self.init_ui()

    def init_ui(self):
        self.bt_minimize.setIcon(QIcon("img/minus.svg"))
        self.bt_maximize.setIcon(QIcon("img/chevron-down.svg"))
        self.bt_normal.setIcon(QIcon("img/chevron-up.svg"))
        self.bt_close.setIcon(QIcon("img/x.svg"))
        self.bt_minimize.clicked.connect(self.showMinimized)
        self.bt_normal.clicked.connect(self.control_bt_normal)
        self.bt_maximize.clicked.connect(self.control_bt_maximize)
        self.bt_close.clicked.connect(self.close)
        self.bt_normal.hide()

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        icon_user = QIcon("img/user.svg")
        self.urltxt.addAction(icon_user, QLineEdit.LeadingPosition)
        self.btn_downloads.clicked.connect(self.descargar_mp3)
        self.gripSize = 10
        self.grip = QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)
        self.frame_superior.mouseMoveEvent = self.mover_ventana
        self.bt_minimize.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.bt_normal.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.bt_maximize.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.bt_close.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_select_folder.clicked.connect(self.select_download_folder)

    def json_job(self):
        try:
            # Abre el archivo JSON
            with open("json/type_file.json", "r", encoding="utf-8") as archivo_json:
                self.datos = json.load(
                    archivo_json
                )  # Guardar los datos JSON en self.datos
                names = self.datos.get("formats", [])

                if not names:
                    raise ValueError("No se encontraron datos en 'name'")

                # Agregar los nombres de las regiones al QComboBox
                for types in names:
                    self.comboboxtype.addItem(types["extension"])

                # Conectar la señal de cambio de región
                # self.industry_combobox.currentIndexChanged.connect(self.cargar_datos_json_commune)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Archivo JSON no encontrado.")
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self, "Error de JSON", f"Error al decodificar el archivo JSON: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Se produjo un error: {str(e)}")

    def select_download_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Descarga"
        )
        if folder:
            self.download_folder = folder
            self.download_status.setText(
                f"Carpeta seleccionada: {self.download_folder}"
            )

    def descargar_mp3(self):
        url = self.urltxt.text()
        if not self.download_folder:
            self.download_status.setText(
                "Por favor, selecciona una carpeta de descarga primero."
            )
            return

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{self.download_folder}/%(title)s.%(ext)s",  # Ruta de descarga usando la carpeta seleccionada
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            start_time = time.time()  # Marca el inicio de la descarga
            self.download_status.setText("Descarga en progreso...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                mp3_filename = (
                    ydl.prepare_filename(info_dict).rsplit(".", 1)[0] + ".mp3"
                )
                self.download_status.setText(
                    f"El archivo MP3 se ha descargado: {mp3_filename}"
                )
            end_time = time.time()  # Marca el final de la descarga
            download_time = end_time - start_time  # Calcula el tiempo total de descarga
            self.download_time.setText(
                f"Tiempo de descarga: {download_time:.2f} segundos"
            )
        except Exception as e:
            self.download_status.setText(f"Error al descargar el archivo: {e}")

    def reload_ui(self):
        self.close()  # Cierra la ventana actual
        self.__init__()  # Re-inicia la vista con el nuevo tema
        self.show()  # Vuelve a mostrar la ventana

    def control_bt_normal(self):
        self.showNormal()
        self.bt_normal.hide()
        self.bt_maximize.show()

    def control_bt_maximize(self):
        self.showMaximized()
        self.bt_maximize.hide()
        self.bt_normal.show()

    def mousePressEvent(self, event):
        self.click_posicion = event.globalPos()

    def mover_ventana(self, event):
        if not self.isMaximized():
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_posicion)
                self.click_posicion = event.globalPos()
                event.accept()
        if event.globalPos().y() <= 5 or event.globalPos().x() <= 5:
            self.showMaximized()
            self.bt_maximize.hide()
            self.bt_normal.show()
        else:
            self.showNormal()
            self.bt_normal.hide()
            self.bt_maximize.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Outube()
    window.show()
    sys.exit(app.exec_())
