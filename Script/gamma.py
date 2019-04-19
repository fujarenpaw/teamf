#!/usr/bin/python
# -*- Coding: utf-8 -*-

from PIL import Image,ImageDraw
import numpy as np
import sys


"""
入力した画像にgamma補正をかけて出力する。下記のように実行
python gammma.py hogehoge.jpg(画像パス) 230(level)
"""
if __name__ == '__main__':
    args = sys.argv
    maxAugmenter = 3
    minAugmenter = 0.2
    if len(args) == 3:
        imgPath = args[1]
        level = int(args[2])
    else:
        sys.exit()

    # 補正力を決める
    if level != 0:
        aug = level / 300
        if aug > maxAugmenter:
            aug = maxAugmenter
        if aug < minAugmenter:
            aug = minAugmenter
    else:
        aug = minAugmenter

    if aug >= 1:
        color = (255, 255, 255)
    else:
        color = (0, 0, 0)

    # 画像読み込み
    im = np.array(Image.open(imgPath), 'f')
    imAugmenter = 255.0 * (im / 255.0) ** aug
    # 画像中にレベル記載
    pil_img = Image.fromarray(np.uint8(imAugmenter))
    draw = ImageDraw.Draw(pil_img)
    draw.text((10, 10), "level:" + str(level), color)

    pil_img.save('gamma.jpg')

