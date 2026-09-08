import rasterio
import matplotlib.pyplot as plt
import numpy as np

file1 = "data/delhi/2021/delhi_2021_rgb.tif"
file2 = "data/delhi/2022/delhi_2022_rgb.tif"

src1 = rasterio.open(file1)
src2 = rasterio.open(file2)

img1 = src1.read().astype(float)
img2 = src2.read().astype(float)

img1 = img1 / 255
img2 = img2 / 255

# Difference between 2021 and 2022
diff = np.abs(img1 - img2)

change = diff.mean(axis=0)

# Change threshold
mask = change > 0.15

mask = mask.astype(np.uint8)

# Save change mask
profile = src1.profile
profile.update(
    dtype=rasterio.uint8,
    count=1
)

with rasterio.open(
    "output/change_mask_2021_2022.tif",
    "w",
    **profile
) as dst:

    dst.write(mask, 1)

print("2021-2022 change mask saved!")

plt.figure(figsize=(6, 6))

plt.imshow(mask, cmap="gray")

plt.title("Delhi 2021 - 2022 Change Mask")

plt.axis("off")

plt.show()

src1.close()
src2.close()