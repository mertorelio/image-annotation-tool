import os
def process_txt_file(file_path):
    new_lines = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            parts = line.split()  # Satırı boşluklara göre böl
            new_line = ",".join(parts)  # Bölünen kısımları virgülle birleştir
            new_lines.append(new_line)

    with open(file_path, "w") as file:
        for new_line in new_lines:
            file.write(new_line + "\n")  # Yeni satırları dosyaya yaz


def process_txt_files_in_folder(folder_path):
    txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]

    for txt_file in txt_files:
        txt_file_path = os.path.join(folder_path, txt_file)
        process_txt_file(txt_file_path)

# Kullanım örneği
folder_path = "image"
process_txt_files_in_folder(folder_path)
