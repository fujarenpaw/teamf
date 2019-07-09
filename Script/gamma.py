#!/usr/bin/python
# -*- Coding: utf-8 -*-

from PIL import Image,ImageDraw
import numpy as np
import sys


"""
入力した画像にgamma補正をかけて出力する。下記のように実行
python gammma.py hogehoge.jpg(画像パス) 230(level)
300を倍率1(無補正として)0に近いと白く、正の値が大きいと黒くなる

"""
if __name__ == '__main__':
    args = sys.argv
    maxAugmenter = 10
    minAugmenter = 0.2
    if len(args) == 4:
        imgPath = args[1]
        level = int(args[2])
        outputPath = args[3]
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

    pil_img.save(outputPath)

