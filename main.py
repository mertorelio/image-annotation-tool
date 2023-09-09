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
from func import cursor_func1, delete_selected_labels1, next_image1, open_dir1, open_dir1, pred_save1, prev_image1, prev_label1, save1, show_selected1


colour = "#FFFFFF"

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


class ImageAnnotator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Image Annotator")
        self._target_height, self._target_width = 1920, 1080
        self._is_saved = True
        self._mode = "bounding_boxes"
        self._class_colors = []
        self._current_image_index = None
        self._image_filenames = None
        self._dragged_keypoint_index = None
        self._bounding_box_start = None
        self._bounding_box_end = None
        self._dragged_box_index = None
        self._dragged_box_corner = None
        self._dragging_corner = False
        self._cursor_selected = False
        self._label_selected = False
        self._model = YOLO('yolov8n.pt')  # load an official model
        self._model = YOLO('models/plate.pt')  # load a custom trained
       
    def initUI(self):
        # Create a QGraphicsView to display the image
        self._graphics_view = QtWidgets.QGraphicsView(self)
        self._graphics_view.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setCentralWidget(self._graphics_view)
        self._scene = QtWidgets.QGraphicsScene(self)
        self._graphics_view.setScene(self._scene)
        self._m_pixmap = QtGui.QPixmap()
        self._image_item = QtWidgets.QGraphicsPixmapItem(self._m_pixmap)
        self._scene.addItem(self._image_item)
        self._graphics_view.setStyleSheet(f"background-color: {colour};")

        # Create a QDockWidget to hold the keypoints list
        self._coordinates_dock = QtWidgets.QDockWidget("Points and boxes", self)
        self._coordinates_dock.setFixedWidth(200)
        self._coordinates_dock.setStyleSheet(f"background-color: {colour};")
        self.addDockWidget(Qt.RightDockWidgetArea, self._coordinates_dock)

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.info_label = QtWidgets.QLabel("Burada bir şeyler oluyor...")
        self.statusBar.addWidget(self.info_label)
        # Bilgi çubuğunu sağ üst köşeye hizala
        self.statusBar.setMaximumHeight(30)  # Maksimum yükseklik ayarlayabilirsiniz

        # Create a QListWidget to display the key points
        self._coordinates_list = QtWidgets.QListWidget()
        self._coordinates_list.itemChanged.connect(self.update_image)
        self._coordinates_dock.setWidget(self._coordinates_list)

        # Create a QDockWidget to hold the image list
        self._image_list_dock = QtWidgets.QDockWidget("Image list", self)
        self._image_list_dock.setFixedWidth(200)
        self.addDockWidget(Qt.RightDockWidgetArea, self._image_list_dock)
        self._image_list_dock.setStyleSheet(f"background-color: {colour};")

        # Create a QListWidget to display the image names
        self._image_list = QtWidgets.QListWidget()
        self._image_list_dock.setWidget(self._image_list)
     
        # Create the left toolbar
        self.create_left_toolbar()
        
        # Connect events to the appropriate functions for adding and moving key points
        self._graphics_view.mousePressEvent = self.mouse_press
        self._graphics_view.mouseMoveEvent = self.mouse_move
        self._graphics_view.mouseReleaseEvent = self.mouse_release
        self._image_list.itemClicked.connect(self.go_to_image)

        self.show()

    def create_left_toolbar(self):
        self._left_toolbar = QtWidgets.QToolBar("Left Toolbar")
        self._left_toolbar.setIconSize(QtCore.QSize(48, 48))
        self._left_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonFollowStyle )
        
        self._left_toolbar.setFloatable(False)
        self._left_toolbar.setMovable(False)
        self._left_toolbar.setStyleSheet(f"background-color: {colour};")
     
        self.addToolBar(Qt.LeftToolBarArea, self._left_toolbar)
        
        # Create the "Open dir" action
        self._openDirAction = QAction(QtGui.QIcon(os.path.join("resources", "file.png")), "Open dir", self)
        self._openDirAction.triggered.connect(self.open_dir)
        self._left_toolbar.addAction(self._openDirAction)

        # Create the "Save" action
        self._saveAction = QAction(QtGui.QIcon(os.path.join("resources",  "save-file.png")), "Save", self)
        self._saveAction.triggered.connect(self.save)
        self._left_toolbar.addAction(self._saveAction)
               
              
        self._cursor_selection = QAction(QtGui.QIcon(os.path.join("resources", "bounding-box.png")), "Cursor Selection", self)
        self._cursor_selection.triggered.connect(self.cursor_func)
        self._left_toolbar.addAction(self._cursor_selection)

        self._predictAction = QAction(QtGui.QIcon(os.path.join("resources", "cpu.png")), "AI Prediction", self)
        self._predictAction.triggered.connect(self.pred_save)
        self._left_toolbar.addAction(self._predictAction)

        self._cursor_selection1 = QAction(QtGui.QIcon(os.path.join("resources", "bring-to-front.png")), "Copy from previous", self)
        self._cursor_selection1.triggered.connect(self.prev_label)
        self._left_toolbar.addAction(self._cursor_selection1)
        
        self._deleteAction = QAction(QtGui.QIcon(os.path.join("resources", "delete.png")), "Delete Selected", self)
        self._deleteAction.triggered.connect(self.delete_selected_labels)
        self._left_toolbar.addAction(self._deleteAction)

        self._showAction = QAction(QtGui.QIcon(os.path.join("resources", "hide.png")), "Show Selected", self)
        self._showAction.triggered.connect(self.show_selected)
        self._left_toolbar.addAction(self._showAction)
        
        self._prevAction = QAction(QtGui.QIcon(os.path.join("resources", "left.png")), "Previos Image", self)
        self._prevAction.triggered.connect(self.prev_image)
        self._left_toolbar.addAction(self._prevAction)
        self._prevAction.setShortcut(QtCore.Qt.Key_Left)

        self._nextAction = QAction(QtGui.QIcon(os.path.join("resources", "right.png")), "Next Image", self)
        self._nextAction.triggered.connect(self.next_image)
        self._left_toolbar.addAction(self._nextAction)
        self._nextAction.setShortcut(QtCore.Qt.Key_Right)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_image)

         # Create the "Save" action
        self._saveAction = QAction(QtGui.QIcon(os.path.join("resources",  "push.png")), "Push", self)
        self._saveAction.triggered.connect(self.save)
        self._left_toolbar.addAction(self._saveAction)

        # Create the "Save" action
        self._saveAction = QAction(QtGui.QIcon(os.path.join("resources",  "pull.png")), "Pull", self)
        self._saveAction.triggered.connect(self.save)
        self._left_toolbar.addAction(self._saveAction)

                # Create the "Change color" action
        self._changeColorAction = QAction(QtGui.QIcon(os.path.join("resources",  "color-wheel.png")),
                                          "Change point color", self)
        self._changeColorAction.triggered.connect(self._select_point_color)
        self._changeColorAction.setProperty("background-color", QtCore.Qt.red)
        self._left_toolbar.addAction(self._changeColorAction)
        
        

        # Create the "Change point size" action
        self._point_size_spinbox = QSpinBox()
        self._point_size_spinbox.setRange(1, 100)
        self._point_size_spinbox.setValue(3)
        
    
    def cursor_func(self):
        cursor_func1(self)
        
    def show_selected(self):
        show_selected1(self)
        
    def delete_selected_labels(self):
        delete_selected_labels1(self)

    def prev_label(self):
        prev_label1(self)
        
    def pred_save(self):
        pred_save1(self)
    
    def next_image(self):
        next_image1(self)

    def open_dir(self):
        open_dir1(self)

    def prev_image(self):
        prev_image1(self)
    
    def save(self):
        save1(self)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            if self._current_image_index is None or self._image_filenames is None:
                return
            if self._current_image_index == len(self._image_filenames) - 1:
                return
            if not self._is_saved: #edit for faster ui
                if self._ask_for_saving() == QtWidgets.QMessageBox.Yes:
                    self.save()
                self._is_saved = True
            self._coordinates_list.clear()
            self._current_image_index += 1
            self._current_image_item = self._image_list.item(self._current_image_index)
            self._current_image_item.setSelected(True)
            self.load_image()

        if event.key() == Qt.Key_Left:  
            if self._current_image_index is None or self._image_filenames is None:
                return
            if self._current_image_index == 0:
                return
            if not self._is_saved: #edit for faster ui
                if self._ask_for_saving() == QtWidgets.QMessageBox.Yes:
                    self.save()
                self._is_saved = True
            self._coordinates_list.clear()
            self._current_image_index -= 1
            self._current_image_item = self._image_list.item(self._current_image_index)
            self._current_image_item.setSelected(True)
            self.load_image()

    def switch_mode(self):
        self._mode = "keypoints" if self._mode == "bounding_boxes" else "bounding_boxes"
        self._switchModeAction.setText(f"Mode (Current: {self._mode})")
                
    def go_to_image(self, item):
        if not self._is_saved:
            if self._ask_for_saving() == QtWidgets.QMessageBox.Yes:
                self.save()
            self._is_saved = True
        self._current_image_index = self._image_list.row(item)
        self._coordinates_list.clear()
        self._current_image_item = item
        self.load_image()
  
   
    
    def _select_point_color(self):
        class_name, ok = QtWidgets.QInputDialog.getItem(self, "Select class dialog",
                                                        "List of classes", self._class_names, 0, False)
        if ok:
            class_idx = self._class_names.index(class_name)
            color = QColorDialog.getColor(QtGui.QColor(self._class_colors[class_idx]), self, "Select point color")
            if color.isValid():
                self._class_colors[class_idx] = color.name()
                for i in range(self._coordinates_list.count()):
                    item = self._coordinates_list.item(i)
                    item_text = item.text().split(",")
                    item_class_idx = int(item_text[0])
                    if item_class_idx == class_idx:
                            normalized_top_left_x, normalized_top_left_y = item_text[1], item_text[2]
                            normalized_bottom_right_x, normalized_bottom_right_y = item_text[3], item_text[4]
                            item.setText(
                                f"{item_class_idx}, "
                                f"{normalized_top_left_x}, "
                                f"{normalized_top_left_y}, "
                                f"{normalized_bottom_right_x}, "
                                f"{normalized_bottom_right_y}"
                            )

                self.update_image()

    def mouse_press(self, event):
        
        if self._cursor_selected == False:
            return
        
        if event.button() != Qt.LeftButton:
            return

        x = int(self._graphics_view.mapToScene(event.pos()).x())
        y = int(self._graphics_view.mapToScene(event.pos()).y())
        normalized_x, normalized_y = x / self._m_pixmap.width(), y / self._m_pixmap.height()

        
        # If click is outside the image, just return and ignore the event
        if x < 0 or x >= self._m_pixmap.width() or y < 0 or y >= self._m_pixmap.height():
            return

        if self._mode == "keypoints":
            # Check if the user clicked on an existing keypoint
            for i in range(self._coordinates_list.count()):
                item = self._coordinates_list.item(i)
                if len(item.text().split(",")) != 3:  # Bounding box
                    continue
                class_idx, item_normalized_x, item_normalized_y = item.text().split(",")
                item_x, item_y = int(float(item_normalized_x) * self._m_pixmap.width()), int(
                    float(item_normalized_y) * self._m_pixmap.height())
                if abs(item_x - x) < 5 and abs(item_y - y) < 5:  # adjust the threshold (5) as needed
                    self._dragged_keypoint_index = i
                    return

            class_name, ok = QtWidgets.QInputDialog.getItem(self, "Select class dialog",
                                                            "List of classes", self._class_names, 0, False)
            if not ok:
                return
            class_idx = self._class_names.index(class_name)
            item = QtWidgets.QListWidgetItem(f"{class_idx}, {normalized_x:.4f}, {normalized_y:.4f}")
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            self._coordinates_list.addItem(item)
            self.update_image()
            self.update()

        elif self._mode == "bounding_boxes":
            # Check if the user clicked on a corner of an existing bounding box
            for i in range(self._coordinates_list.count()):
                item = self._coordinates_list.item(i)
                if len(item.text().split(",")) != 5:  # Keypoint
                    continue
                class_idx, normalized_top_left_x, normalized_top_left_y,  normalized_bottom_right_x, normalized_bottom_right_y = item.text().split(",")
                top_left_x, top_left_y = int(float(normalized_top_left_x) * self._m_pixmap.width()), int(float(normalized_top_left_y) * self._m_pixmap.height())
                bottom_right_x, bottom_right_y = int(float(normalized_bottom_right_x) * self._m_pixmap.width()), int( float(normalized_bottom_right_y) * self._m_pixmap.height())

                top_right_x, top_right_y = bottom_right_x, top_left_y
                bottom_left_x, bottom_left_y = top_left_x, bottom_right_y

                corners = [
                    ("top_left", top_left_x, top_left_y),
                    ("bottom_right", bottom_right_x, bottom_right_y),
                    ("top_right", top_right_x, top_right_y),
                    ("bottom_left", bottom_left_x, bottom_left_y),
                ]

                for corner, corner_x, corner_y in corners:
                    if abs(corner_x - x) < 5 and abs(corner_y - y) < 5:
                        self._dragged_box_index = i
                        self._dragged_box_corner = corner
                        return

            # Set the start position of the bounding box
            self._bounding_box_start = self._graphics_view.mapToScene(event.pos()).toPoint()

    def mouse_move(self, event):
       
        x, y = int(self._graphics_view.mapToScene(event.pos()).x()), int(
            self._graphics_view.mapToScene(event.pos()).y())
        normalized_x, normalized_y = x / self._m_pixmap.width(), y / self._m_pixmap.height()

        if self._mode == "keypoints":
            if self._dragged_keypoint_index is not None:
                item = self._coordinates_list.item(self._dragged_keypoint_index)
                class_idx = item.text().split(",")[0]
                item.setText(f"{class_idx}, {normalized_x:.4f}, {normalized_y:.4f}")
                self.update_image()
        elif self._mode == "bounding_boxes":
            if self._dragged_box_index is not None:
                self._dragging_corner = True
                item = self._coordinates_list.item(self._dragged_box_index)
                class_idx, top_left_x, top_left_y, bottom_right_x, bottom_right_y = [elem.strip() for elem in item.text().split(",")]
                if self._dragged_box_corner == "top_left":
                    item.setText(f"{class_idx}, {normalized_x:.4f}, {normalized_y:.4f}, {bottom_right_x}, {bottom_right_y}")
                elif self._dragged_box_corner == "bottom_right":
                    item.setText(f"{class_idx}, {top_left_x}, {top_left_y}, {normalized_x:.4f}, {normalized_y:.4f}")
                elif self._dragged_box_corner == "top_right":
                    item.setText(f"{class_idx}, {top_left_x}, {normalized_y:.4f}, {normalized_x:.4f}, {bottom_right_y}")
                elif self._dragged_box_corner == "bottom_left":
                    item.setText(f"{class_idx}, {normalized_x:.4f}, {top_left_y}, {bottom_right_x}, {normalized_y:.4f}")
                self.update_image()
            else:
                if event.buttons() & QtCore.Qt.LeftButton:
                    # Update the end position of the bounding box
                    self._bounding_box_end = self._graphics_view.mapToScene(event.pos()).toPoint()
                    # Redraw the image
                    self.update_image()

    def mouse_release(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self._mode == "keypoints":
            if self._dragged_keypoint_index is None:
                return
            x, y = int(self._graphics_view.mapToScene(event.pos()).x()), int(self._graphics_view.mapToScene(event.pos()).y())
            # Check if the keypoint is outside the image
            if x < 0 or x >= self._m_pixmap.width() or y < 0 or y >= self._m_pixmap.height():
                # Remove the keypoint from the QListWidget
                item_to_delete = self._coordinates_list.takeItem(self._dragged_keypoint_index)
                del item_to_delete
                self.update_image()
            self._dragged_keypoint_index = None

        elif self._mode == "bounding_boxes":
            if self._dragged_box_index is not None:  # Dragging behaviour
                item = self._coordinates_list.item(self._dragged_box_index)
                class_idx, normalized_top_left_x, normalized_top_left_y, normalized_bottom_right_x, normalized_bottom_right_y = item.text().split(",")
                top_left_x, top_left_y = int(float(normalized_top_left_x) * self._m_pixmap.width()), int(
                    float(normalized_top_left_y) * self._m_pixmap.height())
                bottom_right_x, bottom_right_y = int(float(normalized_bottom_right_x) * self._m_pixmap.width()), int(
                    float(normalized_bottom_right_y) * self._m_pixmap.height())
                if top_left_x >= bottom_right_x or top_left_y >= bottom_right_y or \
                        top_left_x < 0 or top_left_y < 0 or bottom_right_x >= self._m_pixmap.width() or bottom_right_y >= self._m_pixmap.height():
                    # Remove the bounding box from the QListWidget
                    item_to_delete = self._coordinates_list.takeItem(self._dragged_box_index)
                    del item_to_delete
                    self.update_image()
                self._dragged_box_index = None
                self._dragged_box_corner = None
            elif not self._bounding_box_start or not self._bounding_box_end:  # There is no dragging or drawing
                return

            # The user ends drawing a new bounding box
            if self._dragging_corner == True:
                self._bounding_box_start = None
                self._bounding_box_end = None
                self._dragging_corner = False
                self.update_image()
                return

            # Get the class_name input from the user
            class_name, ok = QtWidgets.QInputDialog.getItem(self, "Select class dialog",
                                                            "List of classes", self._class_names, 0, False)
            if not ok:
                self._bounding_box_start = None
                self._bounding_box_end = None
                self.update_image()
                self._is_saved = True
                return

            class_idx = self._class_names.index(class_name)

            # Calculate the normalized bounding box coordinates
            top_left = self._bounding_box_start
            bottom_right = self._bounding_box_end
            normalized_top_left = QtCore.QPointF(top_left.x() / self._m_pixmap.width(),
                                                 top_left.y() / self._m_pixmap.height())
            normalized_bottom_right = QtCore.QPointF(bottom_right.x() / self._m_pixmap.width(),
                                                     bottom_right.y() / self._m_pixmap.height())

            # Add the bounding box information to the QListWidget
            item = QtWidgets.QListWidgetItem(
                f"{class_idx}, "
                f"{normalized_top_left.x():.4f}, "
                f"{normalized_top_left.y():.4f}, "
                f"{normalized_bottom_right.x():.4f}, "
                f"{normalized_bottom_right.y():.4f}"
            )
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            self._coordinates_list.addItem(item)
            self._bounding_box_start = None
            self._bounding_box_end = None
            self.update_image()

    def update_image(self):

        if self._label_selected!= True:
            # Clear the old image item from the scene
            self._scene.removeItem(self._image_item)
            self._scene.clear()

            # Create a new pixmap with the updated key points or bounding boxes
            pixmap = self._m_pixmap.copy()
            qp = QtGui.QPainter(pixmap)
            point_size = self._point_size_spinbox.value()
        # Draw
            for i in range(self._coordinates_list.count()):
                item_text = self._coordinates_list.item(i).text().split(",")
                class_idx = int(item_text[0])
                color = self._class_colors[class_idx]
                color = QtGui.QColor(color.strip())

                if len(item_text) == 5:  # Bounding box
                    qp.setPen(QtGui.QPen(color, 2, QtCore.Qt.SolidLine))
                    normalized_top_left = QtCore.QPointF(float(item_text[1]), float(item_text[2]))
                    normalized_bottom_right = QtCore.QPointF(float(item_text[3]), float(item_text[4]))
                    top_left = QtCore.QPoint(int(normalized_top_left.x() * pixmap.width()),
                                         int(normalized_top_left.y() * pixmap.height()))
                    bottom_right = QtCore.QPoint(int(normalized_bottom_right.x() * pixmap.width()),
                                             int(normalized_bottom_right.y() * pixmap.height()))
                    qp.drawRect(QtCore.QRect(top_left, bottom_right).normalized())

                # Add special points on the corners of bounding box
                    qp.setPen(QtGui.QPen(QtCore.Qt.green, 10))  # you can adjust the pen size as per your requirement
                    qp.drawPoint(top_left)  # top-left corner
                    qp.drawPoint(bottom_right.x(), top_left.y())  # top-right corner
                    qp.drawPoint(bottom_right)  # bottom-right corner
                    qp.drawPoint(top_left.x(), bottom_right.y())  # bottom-left corner
                
                    temp_font = QtGui.QFont("Helvetica", 14, QtGui.QFont.Bold)
                    qp.setFont(temp_font)
                    qp.setPen(QtGui.QPen(color, 10))

                    background_brush = QtGui.QBrush(QtGui.QColor(0, 0, 255, 100))  # Mavi renkli yarı saydam bir arkaplan
                    qp.setBackground(background_brush)
                
                    qp.drawText(top_left.x(), top_left.y() - 10, f"{self._class_names[class_idx]}") 
                
        else:
            # Clear the old image item from the scene
            self._scene.removeItem(self._image_item)
            self._scene.clear()

        # Create a new pixmap with the updated key points or bounding boxes
            pixmap = self._m_pixmap.copy()
            qp = QtGui.QPainter(pixmap)
            point_size = self._point_size_spinbox.value()
            
            selected_items = self._coordinates_list.selectedItems()
        
        
        #item_text = self._coordinates_list.item(i).text().split(",")
            for item in selected_items:
                selected_item_text = item.text()
                item_text = selected_item_text.split(",")
                class_idx = int(item_text[0])
                color = QtGui.QColor("#45FFCA")
            

                if len(item_text) == 5:  # Bounding box
                    qp.setPen(QtGui.QPen(color, 2, QtCore.Qt.SolidLine))
                    normalized_top_left = QtCore.QPointF(float(item_text[1]), float(item_text[2]))
                    normalized_bottom_right = QtCore.QPointF(float(item_text[3]), float(item_text[4]))
                    top_left = QtCore.QPoint(int(normalized_top_left.x() * pixmap.width()),
                                         int(normalized_top_left.y() * pixmap.height()))
                    bottom_right = QtCore.QPoint(int(normalized_bottom_right.x() * pixmap.width()),
                                             int(normalized_bottom_right.y() * pixmap.height()))
                    qp.drawRect(QtCore.QRect(top_left, bottom_right).normalized())

                # Add special points on the corners of bounding box
                    qp.setPen(QtGui.QPen(QtCore.Qt.green, 10))  # you can adjust the pen size as per your requirement
                    qp.drawPoint(top_left)  # top-left corner
                    qp.drawPoint(bottom_right.x(), top_left.y())  # top-right corner
                    qp.drawPoint(bottom_right)  # bottom-right corner
                    qp.drawPoint(top_left.x(), bottom_right.y())  # bottom-left corner
                
                    temp_font = QtGui.QFont("Helvetica", 14, QtGui.QFont.Bold)
                    qp.setFont(temp_font)
                    qp.setPen(QtGui.QPen(color, 10))

                    background_brush = QtGui.QBrush(QtGui.QColor(0, 0, 255, 100))  # Mavi renkli yarı saydam bir arkaplan
                    qp.setBackground(background_brush)
                
                    qp.drawText(top_left.x(), top_left.y() - 10, f"{self._class_names[class_idx]}") 

        # Draw the bounding box being created
        if self._mode == "bounding_boxes" and self._bounding_box_start and self._bounding_box_end:
            qp.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.green), 1, QtCore.Qt.SolidLine))
            bounding_box_rect = QtCore.QRect(self._bounding_box_start, self._bounding_box_end)
            qp.drawRect(bounding_box_rect.normalized())
        qp.end()

                
        # Create a new image item with the updated pixmap and add it to the scene
        self._image_item = QtWidgets.QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._image_item)
        self._scene.update()

        # There are changes waiting
        self._is_saved = False

    def load_image(self):
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
        txt_file_path = os.path.join(self._current_directory, os.path.splitext(self._image_filenames[self._current_image_index])[0] + ".txt")
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
    def select_anno(self,event):
        x, y = int(self._graphics_view.mapToScene(event.pos()).x()), int(self._graphics_view.mapToScene(event.pos()).y())
        normalized_x, normalized_y = x / self._m_pixmap.width(), y / self._m_pixmap.height()
    def zoom(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Set anchors
        self._graphics_view.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        # Get the current scale factor
        current_scale = self._graphics_view.transform().m11()

        # Calculate the new scale factor based on the mouse wheel delta
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        new_scale = current_scale * zoom_factor

        # Limit the scale factor to a reasonable range between "min_scale" and "max_scale"
        new_scale = max(min(new_scale, 10.0), 0.1)

        # Set the new scale factor
        self._graphics_view.setTransform(QtGui.QTransform.fromScale(new_scale, new_scale))

    def wheelEvent(self, event):
        self.zoom(event)

    def _ask_for_saving(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("Do you want to save the changes?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = msg.exec_()
        return retval


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ImageAnnotator()
    sys.exit(app.exec_())