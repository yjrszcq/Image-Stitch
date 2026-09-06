#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys
from pathlib import Path

from PIL import Image


SUPPORTED_INPUT_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}

SUPPORTED_OUTPUT_FORMATS = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def is_image_file(path):
    return Path(path).suffix.lower() in SUPPORTED_INPUT_EXTS


def normalize_output_extension(fmt):
    if fmt == "jpeg":
        return "jpg"
    if fmt == "tiff":
        return "tif"
    return fmt


def validate_manual_images(paths):
    if not paths:
        raise ValueError("没有指定任何输入图片。")

    for path in paths:
        if not os.path.isfile(path):
            raise ValueError(f"文件不存在：{path}")

        if not is_image_file(path):
            raise ValueError(f"不支持的图片格式：{path}")

    return [os.path.abspath(path) for path in paths]


def get_images_from_dir(folder, output_path=None):
    folder = os.path.abspath(folder)

    if not os.path.isdir(folder):
        raise ValueError(f"文件夹不存在：{folder}")

    image_files = []

    for name in os.listdir(folder):
        full_path = os.path.abspath(os.path.join(folder, name))

        if not os.path.isfile(full_path):
            continue

        if not is_image_file(full_path):
            continue

        if output_path is not None:
            if os.path.normcase(full_path) == os.path.normcase(
                os.path.abspath(output_path)
            ):
                continue

        image_files.append((name, full_path))

    if not image_files:
        raise ValueError(
            f"文件夹内没有找到支持的图片：{folder}"
        )

    numeric_files = []

    for name, full_path in image_files:
        stem = Path(name).stem

        if not re.fullmatch(r"\d+", stem):
            raise ValueError(
                f"图片文件名不符合要求：{name}\n"
                "\n"
                "使用 -d/--dir 时，文件夹内所有图片必须使用"
                "纯数字文件名，例如：\n"
                "  1.jpg\n"
                "  2.jpg\n"
                "  3.png"
            )

        numeric_files.append(
            (
                int(stem),
                name,
                full_path,
            )
        )

    numeric_files.sort(key=lambda item: item[0])

    numbers = [item[0] for item in numeric_files]

    if len(numbers) != len(set(numbers)):
        duplicates = sorted(
            number
            for number in set(numbers)
            if numbers.count(number) > 1
        )

        raise ValueError(
            "存在重复编号的图片："
            + ", ".join(map(str, duplicates))
            + "\n"
            "例如 1.jpg 和 1.png 不能同时存在。"
        )

    expected = list(
        range(
            numbers[0],
            numbers[0] + len(numbers),
        )
    )

    if numbers != expected:
        raise ValueError(
            "图片编号不连续。\n"
            f"实际编号：{numbers}\n"
            f"预期编号：{expected}"
        )

    return [item[2] for item in numeric_files]


def open_images(paths):
    images = []

    for path in paths:
        img = Image.open(path)
        img.load()

        images.append(
            {
                "path": path,
                "image": img.convert("RGBA"),
                "info": dict(img.info),
            }
        )

        img.close()

    return images


def stitch_horizontal(images):
    total_width = sum(
        item["image"].width
        for item in images
    )

    max_height = max(
        item["image"].height
        for item in images
    )

    result = Image.new(
        "RGBA",
        (total_width, max_height),
        (0, 0, 0, 0),
    )

    x = 0

    for item in images:
        img = item["image"]

        result.paste(
            img,
            (x, 0),
            img,
        )

        x += img.width

    return result


def stitch_vertical(images):
    max_width = max(
        item["image"].width
        for item in images
    )

    total_height = sum(
        item["image"].height
        for item in images
    )

    result = Image.new(
        "RGBA",
        (max_width, total_height),
        (0, 0, 0, 0),
    )

    y = 0

    for item in images:
        img = item["image"]

        result.paste(
            img,
            (0, y),
            img,
        )

        y += img.height

    return result


def flatten_transparency(image):
    background = Image.new(
        "RGB",
        image.size,
        (255, 255, 255),
    )

    background.paste(
        image,
        mask=image.getchannel("A"),
    )

    return background


def save_image(image, output_path, output_format, first_image_info=None):
    pil_format = SUPPORTED_OUTPUT_FORMATS[output_format]

    save_kwargs = {}

    if first_image_info:
        dpi = first_image_info.get("dpi")

        if dpi:
            save_kwargs["dpi"] = dpi

        icc_profile = first_image_info.get("icc_profile")

        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile

    if pil_format == "PNG":
        image.save(
            output_path,
            format="PNG",
            optimize=False,
            compress_level=6,
            **save_kwargs,
        )

    elif pil_format == "WEBP":
        image.save(
            output_path,
            format="WEBP",
            lossless=True,
            quality=100,
            method=6,
            **save_kwargs,
        )

    elif pil_format == "JPEG":
        rgb_image = flatten_transparency(image)

        image_kwargs = {
            key: value
            for key, value in save_kwargs.items()
            if key in {"dpi", "icc_profile"}
        }

        rgb_image.save(
            output_path,
            format="JPEG",
            quality=100,
            subsampling=0,
            optimize=False,
            **image_kwargs,
        )

    elif pil_format == "TIFF":
        image.save(
            output_path,
            format="TIFF",
            compression="raw",
            **save_kwargs,
        )

    elif pil_format == "BMP":
        rgb_image = flatten_transparency(image)

        rgb_image.save(
            output_path,
            format="BMP",
        )

    else:
        raise ValueError(
            f"不支持的输出格式：{output_format}"
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "图片拼接工具。"
            "默认横向拼接，默认输出 PNG，"
            "不缩放、不裁剪、不重采样。"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=[
            "h",
            "v",
            "horizontal",
            "vertical",
        ],
        default="h",
        help=(
            "拼接方向：\n"
            "  h / horizontal   横向拼接（默认）\n"
            "  v / vertical     纵向拼接"
        ),
    )

    input_group = parser.add_mutually_exclusive_group(
        required=True
    )

    input_group.add_argument(
        "-i",
        "--image",
        action="append",
        metavar="FILE",
        help=(
            "指定输入图片，可重复使用。\n"
            "图片严格按照 -i 出现的顺序拼接。\n"
            "\n"
            "例如：\n"
            "  -i 1.jpg -i 2.jpg -i 3.jpg"
        ),
    )

    input_group.add_argument(
        "-d",
        "--dir",
        nargs="?",
        const=".",
        metavar="DIR",
        help=(
            "拼接指定文件夹内的所有图片。\n"
            "只写 -d 不指定路径时，默认当前文件夹。\n"
            "\n"
            "文件名必须为连续纯数字，例如：\n"
            "  1.jpg\n"
            "  2.jpg\n"
            "  3.png"
        ),
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=list(
            SUPPORTED_OUTPUT_FORMATS.keys()
        ),
        default="png",
        help=(
            "输出格式。\n"
            "默认：png\n"
            "\n"
            "支持："
            + ", ".join(
                SUPPORTED_OUTPUT_FORMATS.keys()
            )
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        default=".",
        metavar="DIR",
        help=(
            "输出目录。\n"
            "默认：当前文件夹"
        ),
    )

    args = parser.parse_args()

    try:
        output_dir = os.path.abspath(
            args.output
        )

        os.makedirs(
            output_dir,
            exist_ok=True,
        )

        extension = normalize_output_extension(
            args.format
        )

        output_path = os.path.join(
            output_dir,
            f"stitched.{extension}",
        )

        if args.dir is not None:
            input_paths = get_images_from_dir(
                args.dir,
                output_path=output_path,
            )

        else:
            input_paths = validate_manual_images(
                args.image
            )

        if len(input_paths) < 2:
            raise ValueError(
                "至少需要两张图片才能进行拼接。"
            )

        normalized_output = os.path.normcase(
            os.path.abspath(output_path)
        )

        for input_path in input_paths:
            if (
                os.path.normcase(
                    os.path.abspath(input_path)
                )
                == normalized_output
            ):
                raise ValueError(
                    f"输出文件不能覆盖输入文件："
                    f"{input_path}"
                )

        images = open_images(
            input_paths
        )

        if args.mode in (
            "h",
            "horizontal",
        ):
            result = stitch_horizontal(
                images
            )

            mode_name = "横向"

        else:
            result = stitch_vertical(
                images
            )

            mode_name = "纵向"

        first_image_info = (
            images[0]["info"]
            if images
            else None
        )

        save_image(
            result,
            output_path,
            args.format,
            first_image_info,
        )

        print()
        print("拼接完成")
        print("=" * 50)

        print(
            f"拼接方向：{mode_name}"
        )

        print(
            f"图片数量：{len(input_paths)}"
        )

        print(
            f"输出尺寸："
            f"{result.width} × {result.height}"
        )

        print(
            f"输出格式："
            f"{args.format.upper()}"
        )

        print(
            f"输出文件：{output_path}"
        )

        print()
        print("输入顺序：")

        for index, path in enumerate(
            input_paths,
            start=1,
        ):
            print(
                f"  {index:>3}. {path}"
            )

        print()
        print(
            "未进行缩放、裁剪、重采样、"
            "锐化或降噪。"
        )

        if args.format in (
            "jpg",
            "jpeg",
        ):
            print(
                "注意：JPEG 本身是有损格式，"
                "已使用 quality=100、4:4:4 保存。"
            )

        elif args.format == "png":
            print(
                "PNG 为无损输出。"
            )

        elif args.format == "webp":
            print(
                "WebP 使用 lossless 模式无损输出。"
            )

    except KeyboardInterrupt:
        print(
            "\n操作已取消。",
            file=sys.stderr,
        )

        sys.exit(130)

    except Exception as exc:
        print(
            f"错误：{exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
