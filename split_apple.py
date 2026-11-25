import random
import shutil
from pathlib import Path

# =========================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# =========================

ROOT = Path(__file__).parent

SOURCE = ROOT / "raw_datasets" / "apple" / "dataset_apple" / "apple_dataset.zip"
DEST = ROOT / "dataset_test_apple"

SPLITS = ["train", "valid", "test"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Tỷ lệ chia
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
SEED = 42


# =========================
# 2. THU THẬP ẢNH VÀ NHÃN
# =========================

data = []

for split in SPLITS:
    image_dir = SOURCE / split / "images"
    label_dir = SOURCE / split / "labels"

    for image in image_dir.iterdir():
        if image.is_file() and image.suffix.lower() in IMAGE_EXTENSIONS:
            label = label_dir / f"{image.stem}.txt"

            if not label.exists():
                raise FileNotFoundError(
                    f"Không tìm thấy nhãn của ảnh: {image.name}"
                )

            data.append((image, label, split))

print(f"Tổng số ảnh thu thập: {len(data)}")


# =========================
# 3. TRỘN NGẪU NHIÊN
# =========================

random.seed(SEED)
random.shuffle(data)

total = len(data)

train_count = round(total * TRAIN_RATIO)
val_count = round(total * VAL_RATIO)
test_count = total - train_count - val_count

train_data = data[:train_count]
val_data = data[train_count:train_count + val_count]
test_data = data[train_count + val_count:]


# =========================
# 4. TẠO THƯ MỤC DATASET
# =========================

if DEST.exists():
    raise FileExistsError(
        f"Thư mục {DEST} đã tồn tại. "
        "Hãy đổi tên hoặc xóa thư mục chia thử trước khi chạy lại."
    )

for split in ["train", "val", "test"]:
    (DEST / "images" / split).mkdir(parents=True)
    (DEST / "labels" / split).mkdir(parents=True)


# =========================
# 5. COPY ẢNH VÀ NHÃN
# =========================

def copy_data(dataset, target_split):
    for image, label, original_split in dataset:

        # Đặt tên mới để tránh trùng tên ảnh từ các tập nguồn
        new_name = f"{original_split}_{image.name}"

        new_image = DEST / "images" / target_split / new_name
        new_label = DEST / "labels" / target_split / f"{Path(new_name).stem}.txt"

        shutil.copy2(image, new_image)
        shutil.copy2(label, new_label)


copy_data(train_data, "train")
copy_data(val_data, "val")
copy_data(test_data, "test")


# =========================
# 6. TẠO FILE DATA.YAML
# =========================

yaml_content = """train: images/train
val: images/val
test: images/test

nc: 1
names: ['apple']
"""

(DEST / "data.yaml").write_text(yaml_content, encoding="utf-8")


# =========================
# 7. IN KẾT QUẢ
# =========================

print("\n===== KẾT QUẢ CHIA DATASET APPLE =====")
print(f"Tổng số ảnh: {total}")
print(f"Train: {len(train_data)} ảnh ({len(train_data)/total*100:.2f}%)")
print(f"Validation: {len(val_data)} ảnh ({len(val_data)/total*100:.2f}%)")
print(f"Test: {len(test_data)} ảnh ({len(test_data)/total*100:.2f}%)")
print(f"\nDataset được tạo tại: {DEST}")
print("Đã tạo file data.yaml")
print("Hoàn thành!")