import os
import shutil

#virgüllü yoloyu tüm fodlerı uygun hale getirir ve yoloyu uygun hale getirir
def convert_coordinates(input_folder, output_folder):

        # Çıkış klasörünü oluşturun, eğer mevcut değilse
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            dosya_listesi = os.listdir(output_folder)
        

        # Giriş klasöründeki tüm txt dosyalarını işleyin
        for filename in os.listdir(input_folder):
            
            if filename.endswith(".txt") and filename != "classes.txt":
                input_file_path = os.path.join(input_folder, filename)
                output_file_path = os.path.join(output_folder, filename)
                

                with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
                    for line in input_file:
                        class_idx, center_x, center_y, width, height = map(float, line.strip().split(' '))

                        top_left_x = center_x - width / 2
                        top_left_y = center_y - height / 2
                        bottom_right_x = center_x + width / 2
                        bottom_right_y = center_y + height / 2

                        output_file.write(f"{class_idx},{top_left_x},{top_left_y},{bottom_right_x},{bottom_right_y}\n")
    
        


# Kullanım örneği
input_folder = "dataset"  # Giriş dosyasının adını değiştirin
output_folder = "dataset"  # Çıkış dosyasının adını değiştirin

convert_coordinates(input_folder, output_folder)



