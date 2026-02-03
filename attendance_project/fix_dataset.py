# fix_dataset.py
import os, shutil

DATA = "dataset"
if not os.path.exists(DATA):
    print("dataset/ folder not found. Create and add images first.")
    raise SystemExit

renamed = 0
moved = 0

# Rename folders that include extensions like "name.jpg" -> "name"
for name in sorted(os.listdir(DATA)):
    path = os.path.join(DATA, name)
    if os.path.isdir(path):
        lower = name.lower()
        if any(ext in lower for ext in (".jpg", ".jpeg", ".png")):
            newname = name
            for ext in (".jpg", ".jpeg", ".png"):
                newname = newname.replace(ext, "")
            newname = newname.strip().replace(" ", "_")
            newpath = os.path.join(DATA, newname)
            if not os.path.exists(newpath):
                os.rename(path, newpath)
                print(f"Renamed folder: {name} -> {newname}")
                renamed += 1
            else:
                # merge contents
                for f in os.listdir(path):
                    shutil.move(os.path.join(path, f), os.path.join(newpath, f))
                os.rmdir(path)
                print(f"Merged folder {name} -> {newname}")
                renamed += 1

# Move stray image files from dataset root into folder with same base name
for item in sorted(os.listdir(DATA)):
    p = os.path.join(DATA, item)
    if os.path.isfile(p) and item.lower().endswith((".jpg", ".jpeg", ".png")):
        base = os.path.splitext(item)[0].strip().replace(" ", "_")
        folder = os.path.join(DATA, base)
        os.makedirs(folder, exist_ok=True)
        target = os.path.join(folder, f"{base}_000{os.path.splitext(item)[1]}")
        i = 1
        while os.path.exists(target):
            target = os.path.join(folder, f"{base}_{i:03d}{os.path.splitext(item)[1]}")
            i += 1
        shutil.move(p, target)
        print(f"Moved file {item} -> {base}/{os.path.basename(target)}")
        moved += 1

print("Done. Folders renamed:", renamed, "Files moved:", moved)
print("Check dataset/ now: one folder per person, images inside.")
