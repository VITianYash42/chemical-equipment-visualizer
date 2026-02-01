import sys
import requests
import matplotlib.pyplot as plt
# We use the Qt5Agg backend to embed Matplotlib charts inside a PyQt window
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt

class ChemicalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # API Endpoint (Centralized Logic)
        self.backend_url = "http://127.0.0.1:8000/api/upload/"

    def initUI(self):
        self.setWindowTitle('FOSSEE Chemical Visualizer (Desktop)')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Layouts
        main_layout = QVBoxLayout()

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
        self.btn_upload.clicked.connect(self.handle_upload_click)
        main_layout.addWidget(self.btn_upload, alignment=Qt.AlignCenter)

        # Stats Labels (Placeholder)
        self.stats_label = QLabel("Waiting for data...")
        self.stats_label.setStyleSheet("font-size: 14px; padding: 10px; background: white; border-radius: 5px;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.stats_label)

        # Chart Area (Matplotlib Canvas)
        self.figure = plt.figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

    def handle_upload_click(self):
        # Open Native File Dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)", options=options)
        
        if file_path:
            self.send_data_to_backend(file_path)

    def send_data_to_backend(self, file_path):
        """
        Sends the file to Django for processing.
        We do NOT calculate stats here to ensure consistency with the Web App.
        """
        self.stats_label.setText("Uploading and Analyzing...")
        
        try:
            # Open file in binary read mode ('rb')
            files = {'file': open(file_path, 'rb')}
            
            # Requesting the same API as the React Frontend
            response = requests.post(self.backend_url, files=files, auth=('admin', 'admin123'))
            
            if response.status_code == 201:
                data = response.json()
                self.update_dashboard(data)
            else:
                QMessageBox.critical(self, "API Error", f"Server returned error: {response.text}")
                self.stats_label.setText("Analysis Failed.")

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Error", "Could not reach Django Backend.\nIs the server running on port 8000?")
            self.stats_label.setText("Connection Error")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_dashboard(self, data):
        # 1. Update Text Stats
        report = data['stats']
        summary_text = (
            f"Total Equipment: {report['total_count']}  |  "
            f"Avg Flow: {report['avg_flowrate']}  |  "
            f"Avg Pressure: {report['avg_pressure']}"
        )
        self.stats_label.setText(summary_text)

        # 2. Update Matplotlib Chart
        chart_data = data['chart_data']
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Plotting
        ax.bar(chart_data['equipment_names'], chart_data['flowrate'], color='skyblue', label='Flowrate')
        ax.bar(chart_data['equipment_names'], chart_data['pressure'], color='salmon', label='Pressure', alpha=0.7)
        
        ax.set_title('Equipment Flowrate vs Pressure')
        ax.set_ylabel('Value')
        ax.legend()
        
        # Rotate x-axis labels to prevent overlap
        ax.tick_params(axis='x', rotation=45) 
        
        # Refresh the canvas
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChemicalApp()
    ex.show()
    sys.exit(app.exec_())