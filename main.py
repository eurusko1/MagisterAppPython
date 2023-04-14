import sys
import tkinter as tk
from collections import defaultdict
from datetime import datetime, timedelta
import cv2
import matplotlib.pyplot as plt
import pymysql
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, \
    QMainWindow, QGridLayout, QMessageBox, QGroupBox, QFormLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def get_coordinates_from_database(host, user, password, database, table_name):
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=database)

    coordinates = []
    try:
        with connection.cursor() as cursor:
            query = f"SELECT x, y FROM {table_name};"
            cursor.execute(query)
            data = cursor.fetchall()
            coordinates = [(row[0], row[1]) for row in data]
    finally:
        connection.close()

    return coordinates


def plot_coordinates(coordinates, intersections, title):
    fig, ax = plt.subplots()
    x_values, y_values = zip(*coordinates)
    ax.plot(x_values, y_values)

    for i in range(len(coordinates) - 1):
        color_intensity = intersections[(coordinates[i], coordinates[i + 1])]
        ax.plot([coordinates[i][0], coordinates[i + 1][0]],
                [coordinates[i][1], coordinates[i + 1][1]],
                linewidth=1,
                color=plt.cm.viridis(0.5 * color_intensity))

    ax.plot(coordinates[0][0], coordinates[0][1], marker='o', color='green', markersize=8)
    ax.plot(coordinates[-1][0], coordinates[-1][1], marker='o', color='red', markersize=8)
    ax.set_title(title)

    return fig


class AppAbrakeszites(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()
        self.host_input = QLineEdit("MYSQL5045.site4now.net")
        self.user_input = QLineEdit("a970cb_test")
        self.password_input = QLineEdit("test123456")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.database_input = QLineEdit("db_a970cb_test")
        self.table_input = QLineEdit("")
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel("Felhasználó:"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Jelszó:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Adatbázis:"))
        layout.addWidget(self.database_input)
        layout.addWidget(QLabel("Tábla neve:"))
        layout.addWidget(self.table_input)
        self.title_input = QLineEdit("")
        layout.addWidget(QLabel("Ábra címe:"))
        layout.addWidget(self.title_input)
        self.output_button = QPushButton("Válasz kimenetet")
        self.output_button.clicked.connect(self.select_output)
        layout.addWidget(self.output_button)
        self.output_path_label = QLabel("Nincs kimenet válaztva")
        layout.addWidget(self.output_path_label)
        self.run_button = QPushButton("Futtasd")
        self.run_button.clicked.connect(self.run)
        layout.addWidget(self.run_button)
        self.figure = None
        self.canvas = None
        self.setLayout(layout)
        self.setWindowTitle("Ábra készítő")
        self.show()

    def select_output(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getSaveFileName(self, "Kimenet választó ", "", "Image Files "
                                                                             "(*.png);;All Files (*)",
                                              options=options)
        if file:
            self.output_path_label.setText(file)

    def run(self):
        host = self.host_input.text()
        user = self.user_input.text()
        password = self.password_input.text()
        database = self.database_input.text()
        table_name = self.table_input.text()

        coordinates = get_coordinates_from_database(host, user, password, database, table_name)
        intersections = defaultdict(int)
        for i in range(len(coordinates) - 1):
            for j in range(i + 1, len(coordinates) - 1):
                if (coordinates[i] == coordinates[j] and
                        coordinates[i + 1] == coordinates[j + 1]):
                    intersections[(coordinates[i], coordinates[i + 1])] += 1

        title = self.title_input.text()
        fig = plot_coordinates(coordinates, intersections, title)

        if self.canvas is not None:
            self.layout().removeWidget(self.canvas)
            self.canvas.deleteLater()

        self.figure = fig
        self.canvas = FigureCanvas(self.figure)
        self.layout().addWidget(self.canvas)

        output_path = self.output_path_label.text()
        if output_path != "Nincs kimenet választva":
            self.figure.savefig(output_path, bbox_inches='tight')


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Objektumkövető alkalmazás")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_layout = QGridLayout(central_widget)

        self.video_label = QLabel("Videó elérése:")
        grid_layout.addWidget(self.video_label, 0, 0)

        self.video_entry = QLineEdit()
        grid_layout.addWidget(self.video_entry, 0, 1)

        self.video_browse_button = QPushButton("Tallózás")
        self.video_browse_button.clicked.connect(self.browse_video)
        grid_layout.addWidget(self.video_browse_button, 0, 2)

        self.table_label = QLabel("Új tábla neve:")
        grid_layout.addWidget(self.table_label, 1, 0)

        self.table_entry = QLineEdit()
        grid_layout.addWidget(self.table_entry, 1, 1)

        self.host_label = QLabel("Host:")
        grid_layout.addWidget(self.host_label, 2, 0)

        self.host_entry = QLineEdit("MYSQL5045.site4now.net")
        grid_layout.addWidget(self.host_entry, 2, 1)

        self.user_label = QLabel("Felhasználó:")
        grid_layout.addWidget(self.user_label, 3, 0)

        self.user_entry = QLineEdit("a970cb_test")
        grid_layout.addWidget(self.user_entry, 3, 1)

        self.password_label = QLabel("Jelszó:")
        grid_layout.addWidget(self.password_label, 4, 0)

        self.password_entry = QLineEdit("test123456")
        self.password_entry.setEchoMode(QLineEdit.Password)
        grid_layout.addWidget(self.password_entry, 4, 1)

        self.database_label = QLabel("Adatbázis:")
        grid_layout.addWidget(self.database_label, 5, 0)

        self.database_entry = QLineEdit("db_a970cb_test")
        grid_layout.addWidget(self.database_entry, 5, 1)

        self.start_button = QPushButton("Kisérlet indítás")
        self.start_button.clicked.connect(self.start_experiment)
        grid_layout.addWidget(self.start_button, 6, 0, 1, 3)

    def browse_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "",
                                                    "Video files (*.mp4 *.avi *.mkv);;All files (*)")
        self.video_entry.setText(video_path)

    def get_connection(self, host, user, password, database):
        connection = pymysql.connect(host=host,
                                     user=user,
                                     password=password,
                                     db=database)
        return connection

    def start_experiment(self):
        video_name = self.video_entry.text()
        table_name = self.table_entry.text()
        host = self.host_entry.text()
        user = self.user_entry.text()
        password = self.password_entry.text()
        database = self.database_entry.text()

        if not video_name or not table_name or not host or not user or not password or not database:
            QMessageBox.critical(self, "Hiba", "Kérlek töltsd ki az összes mezőt.")
            return

        connection = self.get_connection(host, user, password, database)

        mycursor = connection.cursor()
        mycursor.execute("SHOW TABLES LIKE %s", (table_name,))
        result = mycursor.fetchone()

        if not result:
            mycursor.execute(
                "CREATE TABLE {} (id INT AUTO_INCREMENT PRIMARY KEY, x INT, y INT, w INT, h INT,"
                " elapsed_time TIME,CellaNevek VARCHAR(255))".format(
                    table_name))

        cap = cv2.VideoCapture(video_name)

        start_time = datetime.now()
        elapsed_time = timedelta()

        ret, frame = cap.read()
        bbox = cv2.selectROI(frame, False)

        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, bbox)

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            success, bbox = tracker.update(frame)
            x, y, w, h = [int(i) for i in bbox]
            elapsed_time = datetime.now() - start_time

            sql = "INSERT INTO {} (x, y, w, h, elapsed_time) VALUES (%s, %s, %s, %s, %s)".format(table_name)
            val = (x, y, w, h, str(elapsed_time))
            mycursor.execute(sql, val)
            connection.commit()

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            timer_text = str(elapsed_time - timedelta(microseconds=elapsed_time.microseconds)).zfill(8)
            cv2.putText(frame, timer_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.imshow('Objektumkövető', frame)

            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Cella Információ Kimentése")
        layout = QVBoxLayout()
        self.db_settings_group = QGroupBox("Adatbázis beállítások")
        self.db_settings_layout = QFormLayout()
        self.host_edit = QLineEdit("MYSQL5045.site4now.net")
        self.user_edit = QLineEdit("a970cb_test")
        self.password_edit = QLineEdit("test123456")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.database_edit = QLineEdit("db_a970cb_test")
        self.db_settings_layout.addRow("Host:", self.host_edit)
        self.db_settings_layout.addRow("Felhasználó:", self.user_edit)
        self.db_settings_layout.addRow("Jelszó:", self.password_edit)
        self.db_settings_layout.addRow("Adatbázis:", self.database_edit)
        self.db_settings_group.setLayout(self.db_settings_layout)
        self.select_video_btn = QPushButton("Videó kiválasztása")
        self.select_video_btn.clicked.connect(self.select_video)
        self.video_path_label = QLabel("")
        self.table_name_edit = QLineEdit()
        layout.addWidget(QLabel("Tábla neve:"))
        layout.addWidget(self.table_name_edit)
        self.select_output_btn = QPushButton("Mentés helyének kiválasztása")
        self.select_output_btn.clicked.connect(self.select_output)
        self.output_path_label = QLabel("")
        self.start_btn = QPushButton("Indítás")
        self.start_btn.clicked.connect(self.process_cells)
        layout.addWidget(self.db_settings_group)
        layout.addWidget(self.select_video_btn)
        layout.addWidget(self.video_path_label)
        layout.addWidget(QLabel("Tábla kiválasztása:"))
        layout.addWidget(self.select_output_btn)
        layout.addWidget(self.output_path_label)
        layout.addWidget(self.start_btn)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_video(self):
        options = QFileDialog.Options()
        video_path, _ = QFileDialog.getOpenFileName(self, "Videó kiválasztása", "",
                                                    "Videó fájlok (*.mp4 *.avi *.mkv);;Minden fájl (*)", options=options)
        if video_path:
            self.video_path_label.setText(video_path)
    def select_output(self):
        options = QFileDialog.Options()
        output_path, _ = QFileDialog.getSaveFileName(self, "Mentés helyének kiválasztása", "",
                                                     "Képfájlok (*.png);;Minden fájl (*)", options=options)
        if output_path:
            self.output_path_label.setText(output_path)
    def get_connection(self, host, user, password, database):
        connection = pymysql.connect(host=host,
                                     user=user,
                                     password=password,
                                     db=database)
        return connection
    def process_cells(self):
        if not self.video_path_label.text() or not self.output_path_label.text():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Kérlek, válaszd ki a videó fájlt és a mentési helyet.")
            msg.setWindowTitle("Hiányzó adatok")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
        host = self.host_edit.text()
        user = self.user_edit.text()
        password = self.password_edit.text()
        database = self.database_edit.text()
        def get_connection(self, host, user, password, database):
            connection = pymysql.connect(host=host,
                                         user=user,
                                         password=password,
                                         db=database)
            return connection
        db_connection = self.get_connection(host, user, password, database)
        cursor = db_connection.cursor()
        cursor.execute("SELECT id,name, x, y FROM cells")
        cells = cursor.fetchall()
        table_name = self.table_name_edit.text()
        cursor.execute(f"SELECT CellaNevek FROM {table_name}")
        visited_cells = {cell[0] for cell in cursor.fetchall()}
        video_path = self.video_path_label.text()
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Nincs meg a videófájl vagy nemvolt megnyitva.")
            return
        ret, frame = cap.read()
        if not ret:
            print("Error: Nemtudom olvasni a framet a videóból.")
            return
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for cell in cells:
            id,name, x, y = cell
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        cropped_frame = frame[min_y:max_y + 100, min_x:max_x + 100]
        for cell in cells:
            id, name, x, y = cell
            x -= min_x
            y -= min_y
            if name in visited_cells:
                cv2.rectangle(cropped_frame, (x, y), (x + 100, y + 100), (0, 255, 0), -1)
                cv2.rectangle(cropped_frame, (x, y), (x + 100, y + 100), (0, 255, 0), 2)
            else:
                cv2.rectangle(cropped_frame, (x, y), (x + 100, y + 100), (0, 0, 100), 2)
            cv2.putText(cropped_frame, name, (x + 5, y + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 211), 2)
            cv2.putText(cropped_frame, f"({x}, {y})", (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            cv2.putText(cropped_frame, f"ID: {id}", (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        output_path = self.output_path_label.text()
        if output_path:
            cv2.imwrite(output_path, cropped_frame)
            cap.release()
        cursor.close()
        db_connection.close()

class MainApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("300x200")  # Fix méret
        self.master.resizable(False, False)  # Ablak átméretezésének letiltása

        self.grid()
        self.create_widgets()

        self.open_windows = []

    def create_widgets(self):

        self.object_tracking_button = tk.Button(self, text="Object Tracking", command=self.open_object_tracking)
        self.object_tracking_button.grid(row=0, column=0, padx=10, pady=20)

        self.abra_keszites_button = tk.Button(self, text="Ábra Készítés", command=self.open_abra_keszites)
        self.abra_keszites_button.grid(row=0, column=1, padx=10, pady=20)

        self.racs_abra_keszites = tk.Button(self, text="Rács ábra készítés", command=self.open_racs_abra_keszites)
        self.racs_abra_keszites.grid(row=2, column=0, padx=10, pady=20)

        self.quit_button = tk.Button(self, text="Kilépés", command=self.quit_all_windows)
        self.quit_button.grid(row=1, column=0, columnspan=2, padx=10, pady=20)

    def open_object_tracking(self):
        app = QApplication(sys.argv)
        ex = App()
        ex.show()
        app.exec_()
    def open_abra_keszites(self):
        app = QApplication(sys.argv)
        ex = AppAbrakeszites()
        ex.show()
        app.exec_()
    def open_racs_abra_keszites(self):
        app = QApplication([])
        main_window = MainWindow()
        main_window.show()
        app.exec_()

        app.aboutToQuit.connect(self.quit_all_windows)
    def quit_all_windows(self):
        for window in self.open_windows:
            window.close()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
