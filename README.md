# Image Annotation Tool for Object Detection
Free tool used for annotating data for computer vision algorithms. 



## Preparation
* Put your data and label file to image folder.
* Edit image/classes.txt with your label.
* You need to convert your yolo format label with (yolo2M_conventor.py) script. Input format: **class_idx, top_left_x, top_left_y,bottom_right_x, bottom_right_y**
* If you want to use label assist put your .pt file to models folder. (Must be trained using the ultralytics package.)

## Usage

| Draw Box           | Open Folder    |
|----------------------|----------------------|
| ![GIF 1](/readme/box.gif) | ![GIF 2](/readme/opendic.gif) |
| des          | des         |

| Delete Label          | AI Tool           |
|----------------------|----------------------|
| ![GIF 1](/readme/delete.gif) | ![GIF 2](/readme/ai.gif) |
| des           | des         |





# References
[LabelMe](https://github.com/wkentaro/labelme)
[Dataset](https://www.kaggle.com/datasets/smaildurcan/turkish-license-plate-dataset)

# To-do
* Select model from hugging-face
* Export format
* Upload/Download dataset from cloud like hf/datasets
