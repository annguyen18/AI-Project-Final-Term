from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from converted import Ui_MainWindow
import sys
import csv
import os
import cv2
import shutil
from time import sleep
from datetime import datetime
from attendancesystem import *


class window(QtWidgets.QMainWindow):
    def __init__(self):
        super(window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadData()
        self.ui.addButton.clicked.connect(self.saveData)

        # dropdown items
        self.ui.dropdownList.addItem("cnn")
        self.ui.dropdownList.addItem("hog")
        self.ui.dropdownList.setCurrentIndex(1)

        # encode button
        self.ui.encodeButton.clicked.connect(self.encodeDataset)

        self.ui.checkIn.clicked.connect(self.checkIn)
        self.ui.deleteButton.clicked.connect(self.delStudent)
        self.ui.reload.clicked.connect(self.loadData)

        # attendance table
        self.ui.attendanceTable.setColumnCount(3)
        self.ui.attendanceTable.setColumnWidth(0, 250)
        self.ui.attendanceTable.setColumnWidth(1, 120)
        self.ui.attendanceTable.setHorizontalHeaderLabels(
            ("Họ và tên", "Mã Sinh viên", "Thời gian điểm danh"))
        self.ui.attendanceTable.setColumnCount(3)

    def delStudent(self):
        selectedRow = self.ui.tableWidget.currentItem()
        print(selectedRow.text())
        deleteRow(selectedRow.text())
        print("deleted")

    def encodeDataset(self):
        id = self.ui.idTextbox.text()
        detectionMethod = self.ui.dropdownList.currentText().lower()
        # id is folder name
        encode_faces.encodeFaces(id, detectionMethod)
        # recognize_faces_image.recognizeFace()
        msg = QMessageBox()
        msg.setWindowTitle("Thông Báo")
        msg.setText("Đã hoàn thành encode.")

    def checkIn(self):
        detectionMethod = self.ui.dropdownList.currentText().lower()

        currentTime = datetime.now().strftime("%H-%M-%S")
        recogImage = "photo_" + str(currentTime)
        openCamera(recogImage)
        sleep(0.01)
        # try:
        currentStudentIdList = recognize_faces_image.recognizeFace(
            recogImage, detectionMethod)
        currentStudents = []  # 2d list

        for student in currentStudentIdList:
            result = searchFor(student)     # this returns a list
            result.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            currentStudents.append(result)
            if (not result[0].isalpha()):
                saveToFile(result, "checkins.csv")
        rowCount = self.ui.attendanceTable.rowCount()
        # self.ui.attendanceTable.insertRow(rowCount)

        students = loadFromFile("checkins.csv")

        self.ui.attendanceTable.setRowCount(len(students))

        row_index = 0
        for student in students:
            self.ui.attendanceTable.setItem(
                row_index, 0, QTableWidgetItem(student[0]))
            self.ui.attendanceTable.setItem(
                row_index, 1, QTableWidgetItem(student[1]))
            self.ui.attendanceTable.setItem(
                row_index, 2, QTableWidgetItem(student[2]))
            row_index += 1

        # except:
            #print("Không thể tìm thấy sinh viên!")

    def saveData(self):
        name = self.ui.nameTextbox.text()
        id = self.ui.idTextbox.text()

        student = []
        if name and id is not None:
            rowCount = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowCount)
            self.ui.tableWidget.setItem(rowCount, 0, QTableWidgetItem(name))
            self.ui.tableWidget.setItem(rowCount, 1, QTableWidgetItem(id))
            student.append(name)
            student.append(id)

            saveToFile(student, "students.csv")
            self.ui.nameTextbox.clear()
            self.ui.idTextbox.clear()

        # build dataset
        build_dataset.build(id)

    def loadData(self):

        students = loadFromFile("students.csv")

        self.ui.tableWidget.setRowCount(len(students))
        self.ui.tableWidget.setColumnCount(2)

        self.ui.tableWidget.setHorizontalHeaderLabels(
            ('Họ và Tên', 'Mã Sinh viên'))

        self.ui.tableWidget.setColumnWidth(0, 250)
        # self.ui.tableWidget.setColumnWidth(1, 80)

        row_index = 0
        for student in students:
            self.ui.tableWidget.setItem(
                row_index, 0, QTableWidgetItem(student[0]))
            self.ui.tableWidget.setItem(
                row_index, 1, QTableWidgetItem(student[1]))
            row_index += 1


def deleteRow(id):
    rows = []
    with open("students.csv", "r", encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if (row[1] == id):
                continue
            rows.append(row)

    rootdir = "attendancesystem\\dataset"
    for folder in os.listdir(rootdir):
        if (folder == id):
            shutil.rmtree(rootdir + "\\" + folder)

    # for folder in folders
    with open("students.csv", "w", encoding='utf-8', newline='') as f:
        reader = csv.writer(f)
        reader.writerows(rows)


def saveToFile(obj, fileName):
    with open(fileName, "a", encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # writer.writerows(students)
        writer.writerow(obj)


def loadFromFile(fileName):
    rows = []

    with open(fileName, "r", encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            # print(row)
            rows.append(row)

    return rows


def searchFor(id):
    studentInfo = []
    with open("students.csv", "r", encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            if (row[1] == id):
                studentInfo = row
    return studentInfo


def launchApp():
    app = QtWidgets.QApplication(sys.argv)
    win = window()
    win.show()
    sys.exit(app.exec_())


def openCamera(imageFileName):

    cam = cv2.VideoCapture(0)

    while (True):
        # Capture frame-by-frame
        ret, frame = cam.read()
        # Display the resulting frame
        cv2.imshow('Attendance', frame)
        # Waits for a user input to quit the application
        key = cv2.waitKey(1) & 0xFF
        # press space to take a photo
        if key == ord(' '):
            cv2.imwrite(("checkins" + "\\" + imageFileName + ".jpg"), frame)
            break
    # When everything done, release the capture
    cam.release()
    cv2.destroyAllWindows()


launchApp()
