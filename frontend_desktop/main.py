import sys
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt

class ChemicalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.backend_url = "http://127.0.0.1:8000/api/upload/"

    def initUI(self):
        self.setWindowTitle('FOSSEE Chemical Visualizer (Desktop)')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Title
        self.title_label = QLabel("Chemical Equipment Dashboard")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        main_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Upload Button
        self.btn_upload = QPushButton('Upload CSV & Analyze')
        self.btn_upload.setStyleSheet("""
            QPushButton {
                background-color: #007bff; color: white; padding: 10px 20px;
                font-size: 14px; border-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        self.btn_upload.clicked.connect(self.upload_file)
        main_layout.addWidget(self.btn_upload, alignment=Qt.AlignCenter)

        # Stats Labels
        self.stats_label = QLabel("Waiting for data...")
        self.stats_label.setStyleSheet("font-size: 14px; padding: 10px; background: white; border-radius: 5px;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.stats_label)

        # Chart Area (Matplotlib)
        self.figure = plt.figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

    def upload_file(self):
        # 1. Open File Dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)", options=options)
        
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        self.stats_label.setText("Uploading and Analyzing...")
        
        # 2. Send to Django Backend
        try:
            files = {'file': open(file_path, 'rb')}
            response = requests.post(self.backend_url, files=files, auth=('admin', 'admin123'))
            
            if response.status_code == 201:
                data = response.json()
                self.update_ui(data)
            else:
                QMessageBox.critical(self, "Error", f"Upload Failed: {response.text}")
                self.stats_label.setText("Error during analysis.")

        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to Backend.\nEnsure Django is running.\nError: {e}")
            self.stats_label.setText("Connection Error")

    def update_ui(self, data):
        # 3. Update Stats Text
        stats = data['stats']
        summary_text = (
            f"Total Equipment: {stats['total_count']}  |  "
            f"Avg Flow: {stats['avg_flowrate']}  |  "
            f"Avg Pressure: {stats['avg_pressure']}"
        )
        self.stats_label.setText(summary_text)

        # 4. Update Chart
        chart_data = data['chart_data']
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create Bar Chart
        ax.bar(chart_data['equipment_names'], chart_data['flowrate'], color='skyblue', label='Flowrate')
        ax.bar(chart_data['equipment_names'], chart_data['pressure'], color='salmon', label='Pressure', alpha=0.7)
        
        ax.set_title('Equipment Flowrate vs Pressure')
        ax.set_ylabel('Value')
        ax.legend()
        ax.tick_params(axis='x', rotation=45) # Rotate labels so they don't overlap
        
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChemicalApp()
    ex.show()
    sys.exit(app.exec_())