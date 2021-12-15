
import glob
import shutil
import os
import random
random.seed(42)

files_to_process = glob.glob("processed/*")
random.shuffle(files_to_process)
i = 0
for paper_id_path in files_to_process:
    if os.path.exists(os.path.join(paper_id_path, "main_text.txt")):
        paper_id = paper_id_path.split("/")[-1]
        if i >= 50:
            split = "train"
        else:
            split = "test"

        shutil.copy(os.path.join(paper_id_path, "main_text.txt"), os.path.join("final", split, paper_id + ".main.txt"))
        shutil.copy(os.path.join(paper_id_path, "abstract.txt"), os.path.join("final", split, paper_id + ".abstract.txt"))
        i += 1

