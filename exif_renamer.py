import os
from datetime import datetime, timedelta
import sys
from PIL import Image

def rename_files(directory_path, time_shift_dict):
    files = os.listdir(directory_path)

    for file_name in files:
        _, file_extension = os.path.splitext(file_name)
        if not file_extension.lower().lstrip('.') in ['jpg', 'jpeg', 'png', 'bmp']:
            continue
        
        file_path = os.path.join(directory_path, file_name)

        image = Image.open(file_path)

        exif_data = image._getexif()
        time_shift = None
        if exif_data is not None and 40094 in exif_data:
            base_name = exif_data[40094]
        else:
            if "DSC" in file_name:
                base_name = "DSC" + file_name.rsplit("DSC", 1)[1]
                time_shift = time_shift_dict.get("DSC", 0)
            elif "_MG" in file_name:
                base_name = "_MG" + file_name.rsplit("_MG", 1)[1]
                time_shift = time_shift_dict.get("_MG", 0)
            else:
                base_name = file_name

        if exif_data is not None and 36867 in exif_data:
            capture_time = datetime.strptime(exif_data[36867], "%Y:%m:%d %H:%M:%S")
        else:
            capture_time = datetime.fromtimestamp(os.path.getctime(file_path))
        capture_time += timedelta(seconds=time_shift)

        new_file_name = capture_time.strftime("%Y%m%d_%H%M_") + base_name

        new_file_path = os.path.join(directory_path, new_file_name)

        image.close()
        image = None

        if os.path.exists(new_file_path) and file_path != new_file_path:
            os.remove(new_file_path)
        os.rename(file_path, new_file_path)


if __name__ == "__main__":
    print(sys.argv)

    if len(sys.argv) < 2:
        # directory_path = ""
        sys.exit()
    else:
        directory_path = sys.argv[1]

    if len(sys.argv) >= 2:
        time_shift_arg = sys.argv[2]
    else:
        time_shift_arg = "" # "DSC|125|_MG|247"
    
    time_shift_dict = {}

    shift_list = [x for x in time_shift_arg.split("|") if x]
    for i in range(0, len(shift_list), 2):
        key = shift_list[i]
        value = int(shift_list[i+1])
        time_shift_dict[key] = value

    rename_files(directory_path, time_shift_dict)
