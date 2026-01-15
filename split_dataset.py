import os
import random
import shutil

SOURCE_DIR = r"C:\Users\athar\Downloads\Plant_leaf_diseases_dataset_without_augmentation\Plant_leave_diseases_dataset_without_augmentation"
TARGET_DIR = r"C:\Users\athar\Downloads\plant_disease_prediction\dataset"

TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1

random.seed(42)

# Create base folders
for split in ["train", "val", "test"]:
    os.makedirs(os.path.join(TARGET_DIR, split), exist_ok=True)

# Loop over each class folder
for class_name in os.listdir(SOURCE_DIR):
    class_path = os.path.join(SOURCE_DIR, class_name)

    if not os.path.isdir(class_path):
        continue

    images = [f for f in os.listdir(class_path)
              if os.path.isfile(os.path.join(class_path, f))]

    random.shuffle(images)

    total = len(images)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:]
    }

    for split, files in splits.items():
        split_class_dir = os.path.join(TARGET_DIR, split, class_name)
        os.makedirs(split_class_dir, exist_ok=True)

        for file in files:
            src_file = os.path.join(class_path, file)
            dst_file = os.path.join(split_class_dir, file)
            shutil.copy2(src_file, dst_file)

    print(f"✅ Done: {class_name}")

print("\n🎉 Dataset successfully split into train / val / test!")
