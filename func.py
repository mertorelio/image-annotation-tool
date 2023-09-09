import os
import sys
import random
import PIL
import PIL.Image
from PIL import ImageQt
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QColorDialog, QSpinBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
import sys
from PIL import Image
import PIL.ImageQt

from ultralytics import YOLO
from PIL import Image
import glob
import os

class Resizer:
    def __init__(self, target_height, target_width):
        self._target_height = target_height
        self._target_width = target_width

    def _resize_factor(self, image):
        height_ratio = image.size[1] / self._target_height
        width_ratio = image.size[0] / self._target_width
        return max(height_ratio, width_ratio)

    def scaled_image_dims(self, image):
        r_factor = self._resize_factor(image)
        return round(image.size[1] / r_factor), round(image.size[0] / r_factor)

    def resize(self, image: PIL.Image.Image):
        scaled_h, scaled_w = self.scaled_image_dims(image)
        image = image.resize(size=(scaled_w, scaled_h))
        return image


def cursor_func1(self):
        if self._cursor_selected == True:
            self._cursor_selected = False
            self.info_label.setText("")
            
        elif self._cursor_selected == False:
            self._cursor_selected = True


def show_selected1(self):
        #loop for update image
        self.timer.start(500)
        if self._label_selected == True:
            self._label_selected = False
            print(self._label_selected)
            self.update_image()
        elif self._label_selected == False:
            self._label_selected = True
            print(self._label_selected)
            self.update_image()
            

def delete_selected_labels1(self):
        selected_items = self._coordinates_list.selectedItems()
        
        
        #item_text = self._coordinates_list.item(i).text().split(",")
        for item in selected_items:
            self._coordinates_list.takeItem(self._coordinates_list.row(item))
            
        self.update_image()
        self._is_saved = False


def prev_label1(self):
        image_path = os.path.join(self._current_directory, self._image_filenames[self._current_image_index])
        image = PIL.Image.open(image_path)
        resizer = Resizer(self._target_height, self._target_width)
        image = resizer.resize(image)
        self._img = PIL.ImageQt.ImageQt(image)
        self._m_pixmap = QtGui.QPixmap.fromImage(self._img)
        self._image_item = QtWidgets.QGraphicsPixmapItem(self._m_pixmap)
        self._scene.setSceneRect(0, 0, self._m_pixmap.width(), self._m_pixmap.height())
        self._graphics_view.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    # Clear the current list of coordinates
        self._coordinates_list.clear()

    # Check if the corresponding .txt file exists
        txt_file_path = os.path.join(self._current_directory, os.path.splitext(self._image_filenames[self._current_image_index-1])[0] + ".txt")
        if os.path.exists(txt_file_path):
            with open(txt_file_path, "r") as txt_file:
                for line in txt_file:
                    line_elements = line.strip().split(",")
                    if len(line_elements) == 3:  # Keypoint
                        class_idx, normalized_x, normalized_y = map(float, line_elements)
                        x = int(normalized_x * self._m_pixmap.width())
                        y = int(normalized_y * self._m_pixmap.height())
                        item_text = f"{int(class_idx)}, {x}, {y}"
                        item = QtWidgets.QListWidgetItem(item_text)
                        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                        self._coordinates_list.addItem(item)
                    elif len(line_elements) == 5:  # Bounding box
                        class_idx, top_left_x, top_left_y,bottom_right_x, bottom_right_y = map(float, line_elements)

                        item_text = f"{int(class_idx)}, {top_left_x}, {top_left_y}, {bottom_right_x}, {bottom_right_y}"
                        item = QtWidgets.QListWidgetItem(item_text)
                        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                        self._coordinates_list.addItem(item)
                        
        
        self.update_image()
        self.update()
        self._is_saved = True

    
def pred_save1(self):

        img = self._image_list.selectedItems()
        for item in img:
                selected_item_text = item.text()
        print(selected_item_text)
        img = str(selected_item_text)
        print(img)
        results = self._model(f"{self._current_directory}/{img}")  # results list
        
        text_name = str(img)
        text_name = text_name[:-4]
        with open(f"image/{text_name}.txt", 'w') as file:
            for r in results:
                clss = r.boxes.cls.tolist()
                xy = r.boxes.xywhn.tolist()
                for i in range(len(clss)):
                    
                    top_left_x = xy[i][0] - xy[i][2] / 2
                    top_left_y = xy[i][1] - xy[i][3] / 2
                    bottom_right_x = xy[i][0] + xy[i][2] / 2
                    bottom_right_y = xy[i][1] + xy[i][3] / 2
                    file.write(f"{(clss[i])} , {top_left_x} , {top_left_y } , {bottom_right_x } , {bottom_right_y} " + '\n')
    
def next_image1(self):
        if self._current_image_index is None or self._image_filenames is None:
            return
        if self._current_image_index == len(self._image_filenames) - 1:
            return
        if not self._is_saved:
            if self._ask_for_saving() == QtWidgets.QMessageBox.Yes:
                self.save()
            self._is_saved = True
        self._coordinates_list.clear()
        self._current_image_index += 1
        self._current_image_item = self._image_list.item(self._current_image_index)
        self._current_image_item.setSelected(True)
        self.load_image()

def open_dir1(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        directory = QFileDialog.getExistingDirectory(self, "Select a directory", options=options)
        if directory:
            self._coordinates_list.clear()
            with open(os.path.join(directory, "classes.txt"), "r") as file:
                self._class_names = file.readlines()
            self._current_directory = directory
            self._image_filenames = [
                name for name in os.listdir(directory)
                if any(name.endswith(ext) for ext in [".jpg", ".png", ".gif", ".jpeg"])
            ]
            self._current_image_index = 0
            for i in range(len(self._class_names)):
                color = "#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
                self._class_colors.append(color)
            self._image_list.clear()
            for name in self._image_filenames:
                self._image_list.addItem(name)
            self._current_image_item = self._image_list.item(0)
            self._current_image_item.setSelected(True)
            self._toplam_satir_sayisi = 0
            self._index1 = 0
            self._index2 = 0
            self._index3 = 0
            self._index4 = 0
            self._index5 = 0
            
            klasor_yolu = self._current_directory

            for filename in os.listdir(klasor_yolu):
                if filename.endswith(".txt"):
                    dosya_yolu = os.path.join(klasor_yolu, filename)
            
                    with open(dosya_yolu, 'r') as dosya:
                        #satir_sayisi = len(dosya.readlines())
                        #self._toplam_satir_sayisi += satir_sayisi
                        satirlar = dosya.readlines()
                        
                        for satir in satirlar:
                            
                            if len(satir) > 0:
                                ilk_karakter = satir[0]
                                
                                if str(ilk_karakter) == '1':
                                    self._index1 += 1
                                elif str(ilk_karakter) == '2':
                                    self._index2 += 1

                                elif str(ilk_karakter)== '3':
                                    self._index3 += 1
                                elif str(ilk_karakter)== '4':
                                    self._index4 += 1
                                elif str(ilk_karakter) == '5':
                                    self._index5 += 1
                   
            self.load_image()
        self._toplam_satir_sayisi = self._index1 + self._index2 + self._index3 + self._index4 + self._index5 
        print(self._index1)
        print(self._index2)
        print(self._index3)
        print(self._toplam_satir_sayisi)

def prev_image1(self):
        if self._current_image_index is None or self._image_filenames is None:
            return
        if self._current_image_index == 0:
            return
        if not self._is_saved:
            if self._ask_for_saving() == QtWidgets.QMessageBox.Yes:
                self.save()
            self._is_saved = True
        self._coordinates_list.clear()
        self._current_image_index -= 1
        self._current_image_item = self._image_list.item(self._current_image_index)
        self._current_image_item.setSelected(True)
        self.load_image()

def save1(self):
        current_image_name = self._image_filenames[self._current_image_index]
        default_file_name = os.path.splitext(current_image_name)[0] + ".txt"
        default_name = os.path.join(self._current_directory, default_file_name)
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", default_name, "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as file:
                for i in range(self._coordinates_list.count()):
                    item_text = self._coordinates_list.item(i).text().split(",")
                    class_idx = item_text[0]
                    if len(item_text) == 3:  # Keypoint
                        normalized_x, normalized_y = item_text[1], item_text[2]
                        file.write(f"{class_idx}, {normalized_x}, {normalized_y}\n")
                    elif len(item_text) == 5:  # Bounding box
                        normalized_top_left_x, normalized_top_left_y = item_text[1], item_text[2]
                        normalized_bottom_right_x, normalized_bottom_right_y = item_text[3], item_text[4]
                        file.write(
                            f"{class_idx}, {normalized_top_left_x}, {normalized_top_left_y}, {normalized_bottom_right_x}, {normalized_bottom_right_y}\n")
                self._is_saved = True