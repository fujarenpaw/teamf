
# !/usr/bin/python3
# coding: utf-8

import cv2
import numpy as np
from PIL import Image
import sys
import pyocr
import pyocr.builders


def transform_by4(img, points):
    """ 4点を指定してトリミングする。 """

    points = sorted(points, key=lambda x:x[1])  # yが小さいもの順に並び替え。
    top = sorted(points[:2], key=lambda x:x[0])  # 前半二つは四角形の上。xで並び替えると左右も分かる。
    bottom = sorted(points[2:], key=lambda x:x[0], reverse=True)  # 後半二つは四角形の下。同じくxで並び替え。
    points = np.array(top + bottom, dtype='float32')  # 分離した二つを再結合。

    width = max(np.sqrt(((points[0][0]-points[2][0])**2)*2), np.sqrt(((points[1][0]-points[3][0])**2)*2))
    height = max(np.sqrt(((points[0][1]-points[2][1])**2)*2), np.sqrt(((points[1][1]-points[3][1])**2)*2))

    dst = np.array([
            np.array([0, 0]),
            np.array([width-1, 0]),
            np.array([width-1, height-1]),
            np.array([0, height-1]),
            ], np.float32)

    trans = cv2.getPerspectiveTransform(points, dst)  # 変換前の座標と変換後の座標の対応を渡すと、透視変換行列を作ってくれる。
    return cv2.warpPerspective(img, trans, (int(width), int(height)))  # 透視変換行列を使って切り抜く。


def OCR(imgPath):
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        return ""
        # sys.exit(1)
    # The tools are returned in the recommended order of usage
    tool = tools[0]

    lang = 'eng'
    txt = tool.image_to_string(
        # Image.open('bigTrimming.jpg'),
        Image.open(imgPath),
        lang=lang,
        builder=pyocr.builders.DigitBuilder()
    )
    return txt


"""
画像から社員証検出し、社員番号部分を抜き出す
コマンドラインから画像パスを引数として下記のように実行
python detection.py hogehoge.jpg
"""
if __name__ == '__main__':
    outputWrapPicture = "warped.jpg"
    outputTrimmingPicture = "numImg.jpg"
    rt = 0
    args = sys.argv
    if len(args) == 2:
        imgPath = args[1]
        # print(imgPath)
    else:
        sys.exit(0)

    orig = cv2.imread(imgPath)

    lines = orig.copy()

    # 輪郭を抽出する
    canny = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    canny = cv2.convertScaleAbs(orig)
    canny = cv2.GaussianBlur(canny, (5, 5), 0)
    canny = cv2.Canny(canny, 50, 100)
    # cv2.imshow('canny', canny)

    cnts = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]  # 抽出した輪郭に近似する直線（？）を探す。
    cnts.sort(key=cv2.contourArea, reverse=True)  # 面積が大きい順に並べ替える。

    warp = None
    for i, c in enumerate(cnts):
        arclen = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*arclen, True)

        level = 1 - float(i)/len(cnts)  # 面積順に色を付けたかったのでこんなことをしている。
        if len(approx) == 4:
            cv2.drawContours(lines, [approx], -1, (0, 0, 255*level), 2)
            if warp is None:
                warp = approx.copy()  # 一番面積の大きな四角形をwarpに保存。
        else:
            cv2.drawContours(lines, [approx], -1, (0, 255*level, 0), 2)

        for pos in approx:
            cv2.circle(lines, tuple(pos[0]), 4, (255*level, 0, 0))

    # 社員証抽出
    if warp is not None:
        warped = transform_by4(orig, warp[:,0,:])  # warpが存在した場合、そこだけくり抜いたものを作る。
        # cv2.imshow('warp', warped)
        cv2.imwrite(outputWrapPicture, warped)

        # 縦横比判定
        limMin = 0.52
        limMax = 0.88
        allowTH = 0.15

        height, width, channels = warped.shape[:3]
        if (limMin - allowTH) <= height / width <= (limMax + allowTH):
            # 座標で番号決め打ち
            getPosXMin = 0.600
            getPosXMax = 0.941
            getPosYMin = 0.340
            getPosYMax = 0.454
            numImg = warped[int(height * getPosYMin):int(height * getPosYMax), int(width * getPosXMin):int(width * getPosXMax)]

            cv2.imwrite(outputTrimmingPicture, numImg)
            num = OCR(outputTrimmingPicture)

            if num != "":
                rt = int(num)
            else:
                pass

    sys.exit(rt)
