# Image-Stitch

一个简单的命令行图片拼接工具，用于将多张图片按顺序进行横向或纵向拼接。

仓库名：

```text
Image-Stitch
```

脚本文件名：

```text
image-stitch.py
```

脚本：

```text
image-stitch.py
```

默认行为：

- 默认横向拼接
- 不缩放
- 不裁剪
- 不重采样
- 不锐化
- 不降噪
- 输出格式由 `-f` 和 `-o` 的文件后缀共同决定

## 安装

需要 Python 3.8+ 和 Pillow：

```bash
pip install Pillow
```

## 基本用法

```bash
python image-stitch.py [参数]
```

查看帮助：

```bash
python image-stitch.py -h
```

## 参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `-i FILE` / `--image FILE` | 指定输入图片，可重复使用 | 无 |
| `-d [DIR]` / `--dir [DIR]` | 拼接目录中的全部图片；只写 `-d` 时使用当前目录 | 无 |
| `-m MODE` / `--mode MODE` | `h`/`horizontal` 横向，`v`/`vertical` 纵向 | `h` |
| `-f FORMAT` / `--format FORMAT` | 显式指定输出格式 | 自动判断 |
| `-o [FILE]` / `--output [FILE]` | 输出文件路径，可省略值 | 自动 |

`-i` 和 `-d` 互斥，不能同时使用。

---

# 输出格式与 `-o` 规则

这是当前版本最重要的规则。

## 1. 不带 `-f`

### `-o` 不出现

```bash
python image-stitch.py -i 1.jpg -i 2.jpg
```

输出：

```text
./stitched.png
```

格式：

```text
PNG
```

### 只写 `-o`，不提供值

```bash
python image-stitch.py -i 1.jpg -i 2.jpg -o
```

输出：

```text
./stitched.png
```

格式：

```text
PNG
```

### `-o` 有值，但没有后缀

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -o ./result
```

输出：

```text
./result.png
```

格式：

```text
PNG
```

### `-o` 有值，并且有后缀

此时以后缀为准。

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -o ./result.webp
```

输出：

```text
./result.webp
```

格式：

```text
WebP
```

例如：

```bash
-o ./result.jpg
```

则输出 JPEG。

---

# 2. 带 `-f`

带 `-f` 后，输出格式始终以 `-f` 为准。

## `-o` 不出现

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -f jpg
```

输出：

```text
./stitched.jpg
```

格式：

```text
JPEG
```

## 只写 `-o`，不提供值

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -f webp \
  -o
```

输出：

```text
./stitched.webp
```

格式：

```text
WebP
```

## `-o` 有值，但没有后缀

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -f jpg \
  -o ./result
```

输出：

```text
./result.jpg
```

## `-o` 有值，并且已经带后缀

此时仍然以 `-f` 为准，并在 `-o` 原文件名后继续追加 `-f` 对应的后缀。

例如：

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -f jpg \
  -o ./a.png
```

最终输出：

```text
./a.png.jpg
```

实际格式：

```text
JPEG
```

另一个例子：

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg \
  -f webp \
  -o ./abc.jpg
```

输出：

```text
./abc.jpg.webp
```

实际格式：

```text
WebP
```

---

# 规则总表

| `-f` | `-o` | 结果 |
|---|---|---|
| 无 | 无 | `./stitched.png`，PNG |
| 无 | `-o` | `./stitched.png`，PNG |
| 无 | `-o a` | `a.png`，PNG |
| 无 | `-o a.jpg` | `a.jpg`，JPEG |
| 无 | `-o a.webp` | `a.webp`，WebP |
| `-f jpg` | 无 | `./stitched.jpg`，JPEG |
| `-f jpg` | `-o` | `./stitched.jpg`，JPEG |
| `-f jpg` | `-o a` | `a.jpg`，JPEG |
| `-f jpg` | `-o a.png` | `a.png.jpg`，JPEG |
| `-f webp` | `-o a.jpg` | `a.jpg.webp`，WebP |

---

# `-o` 路径

`-o` 支持：

- 相对路径
- 绝对路径

相对路径以执行命令时的当前工作目录为基准。

例如：

```bash
-o ./output/result
```

或：

```bash
-o ../result.png
```

或：

```bash
-o /home/user/Pictures/result.webp
```

如果输出文件的父目录不存在，脚本会自动创建。

---

# `-i`：手动指定图片

`-i` 可以重复使用，按参数出现顺序拼接。

```bash
python image-stitch.py \
  -i a.jpg \
  -i b.png \
  -i c.webp
```

顺序：

```text
a.jpg → b.png → c.webp
```

手动模式下不要求文件名是数字。

---

# `-d`：文件夹模式

指定目录：

```bash
python image-stitch.py -d ./images
```

只写：

```bash
python image-stitch.py -d
```

等价于：

```bash
python image-stitch.py -d .
```

即使用当前目录。

## 文件名要求

文件夹模式下，图片必须使用连续的纯数字文件名。

允许：

```text
1.jpg
2.jpg
3.png
4.webp
```

也允许：

```text
001.jpg
002.jpg
003.jpg
```

会按数字大小排序。

不允许：

```text
a.jpg
image1.jpg
1-test.jpg
```

编号必须连续：

```text
1.jpg
2.jpg
4.jpg
```

会报错，因为缺少 `3`。

同一个编号不能重复：

```text
1.jpg
1.png
2.jpg
```

也会报错。

---

# 横向与纵向

## 横向

默认：

```bash
python image-stitch.py \
  -i 1.jpg \
  -i 2.jpg
```

也可以显式指定：

```bash
-m h
```

或：

```bash
--mode horizontal
```

输出宽度为所有图片宽度之和，输出高度为最大图片高度。

如果高度不同：

- 顶部对齐
- 其余区域透明

## 纵向

```bash
-m v
```

或：

```bash
--mode vertical
```

输出高度为所有图片高度之和，输出宽度为最大图片宽度。

如果宽度不同：

- 左侧对齐
- 其余区域透明

JPEG / BMP 不支持透明，因此透明区域会使用白色背景。

---

# 输出格式

支持：

```text
png
jpg
jpeg
webp
bmp
tif
tiff
```

## PNG

无损。

## WebP

使用 Lossless 模式，无损。

## JPEG

JPEG 本身为有损格式。

脚本使用：

- `quality=100`
- 4:4:4 色度采样

尽量降低额外质量损失。

## TIFF

使用无压缩 TIFF。

---

# 注意事项

1. 至少需要两张图片。
2. `-i` 与 `-d` 不能同时使用。
3. `-d` 不指定路径时默认当前目录。
4. `-m` 不指定时默认横向。
5. 不同尺寸图片不会自动缩放。
6. PNG 和 WebP Lossless 为无损输出。
7. JPEG 本身为有损格式。
8. 带 `-f` 时，`-f` 对输出格式拥有最高优先级。
9. 带 `-f` 且 `-o` 已有后缀时，不替换原后缀，而是在末尾追加 `-f` 对应后缀。
