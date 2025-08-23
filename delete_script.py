import os
import shutil

files_to_delete = [
    "butler/弃用",
    "butler/弃用1",
    "package/弃用",
    "plugin/弃用",
    "弃用"
]

for item in files_to_delete:
    try:
        if os.path.isfile(item):
            os.remove(item)
            print(f"Deleted file: {item}")
        elif os.path.isdir(item):
            shutil.rmtree(item)
            print(f"Deleted directory: {item}")
        else:
            # It might be a file without extension, or the tool ls shows dirs without trailing slash
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"Deleted directory: {item}")
                else:
                    os.remove(item)
                    print(f"Deleted file: {item}")
            else:
                print(f"Item not found or already deleted: {item}")
    except Exception as e:
        print(f"Error deleting {item}: {e}")
