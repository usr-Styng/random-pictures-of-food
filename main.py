import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QDesktopWidget, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QUrl, QPropertyAnimation
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import requests

class RandomImageLoader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Man I sure am hungry")
        self.layout = QVBoxLayout()
        self.label = QLabel("Loading...")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.opacity = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity)
        self.fade = QPropertyAnimation(self.opacity, b"opacity")
        self.fade.setDuration(350)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.image_downloaded)

        self.refresh_button = QPushButton("New Image")
        self.refresh_button.clicked.connect(self.refresh)
        self.layout.addWidget(self.refresh_button)

        self.fit_screen()
        self.center()

    def fit_screen(self):
        g = QDesktopWidget().availableGeometry()
        margin = 150
        self.screen_width = g.width() - margin
        self.screen_height = g.height() - margin
        self.setMaximumSize(self.screen_width, self.screen_height)

    def center(self):
        qr = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(center_point)
        self.move(qr.topLeft())

    def load_image_from_url(self, url):
        self.manager.get(QNetworkRequest(QUrl(url)))

    def image_downloaded(self, reply):
        if reply.error():
            self.label.setText(f"Error downloading image: {reply.errorString()}")
            return

        data = reply.readAll()
        pixmap = QPixmap()
        if not pixmap.loadFromData(data):
            self.label.setText("Could not load image data.")
            return

        w = pixmap.width()
        h = pixmap.height()
        if w > self.screen_width or h > self.screen_height:
            f = min(self.screen_width / w, self.screen_height / h)
            pixmap = pixmap.scaled(int(w * f), int(h * f))

        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        self.center()

        self.opacity.setOpacity(0.0)
        self.fade.stop()
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.start()

    def refresh(self):
        try:
            url = requests.get("https://foodish-api.com/api/").json()["image"]
            self.label.setText("Loading...")
            self.opacity.setOpacity(1.0)
            self.load_image_from_url(url)
        except Exception as e:
            self.label.setText(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication([])
    w = RandomImageLoader()
    url = requests.get("https://foodish-api.com/api/").json()["image"]
    w.load_image_from_url(url)
    w.show()
    sys.exit(app.exec_())