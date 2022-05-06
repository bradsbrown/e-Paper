#!/usr/bin/python
# -*- coding:utf-8 -*-
import enum
import os
import pathlib
import sys
import typing

python_root = pathlib.Path(__file__).parents[1]
picdir = python_root / "pic"
libdir = python_root / "lib"
if os.path.exists(libdir):
    sys.path.append(str(libdir))

import logging
import time

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13bc

logging.basicConfig(level=logging.DEBUG)


def setup_epd():
    epd = epd2in13bc.EPD()
    epd.init()
    return epd


Epd = setup_epd()


class Images(enum.Enum):
    Black = Image.new("1", (Epd.height, Epd.width), 255)
    Red = Image.new("1", (Epd.height, Epd.width), 255)


class Markers(enum.Enum):
    Black = ImageDraw.Draw(Images.Black.value)
    Red = ImageDraw.Draw(Images.Red.value)


def get_font(size=20):
    return ImageFont.truetype(os.path.join(picdir, "Font.ttc"), size)


def draw_text(
    text: str, coords: typing.Tuple[int, int], font_size: int, marker: Markers, fill=0
):
    marker.value.text(coords, text, font=get_font(font_size), fill=fill)


def write_buffers(buffers=None):
    Epd.display(Epd.getbuffer(Images.Black.value), Epd.getbuffer(Images.Red.value))


def demo():
    logging.info("epd2in13bc Demo")

    clear()
    time.sleep(1)

    # Drawing on the image
    logging.info("Drawing")
    font20 = get_font(20)
    font18 = get_font(18)

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    drawblack = Markers.Black.value
    drawry = Markers.Red.value
    drawblack.text((10, 0), "hello world", font=font20, fill=0)
    drawblack.text((10, 20), "2.13inch e-Paper bc", font=font20, fill=0)
    drawblack.text((120, 0), "微雪电子", font=font20, fill=0)
    drawblack.line((20, 50, 70, 100), fill=0)
    drawblack.line((70, 50, 20, 100), fill=0)
    drawblack.rectangle((20, 50, 70, 100), outline=0)
    drawry.line((165, 50, 165, 100), fill=0)
    drawry.line((140, 75, 190, 75), fill=0)
    drawry.arc((140, 50, 190, 100), 0, 360, fill=0)
    drawry.rectangle((80, 50, 130, 100), fill=0)
    drawry.chord((85, 55, 125, 95), 0, 360, fill=1)
    Epd.display(Epd.getbuffer(Images.Black.value), Epd.getbuffer(Images.Black.value))
    time.sleep(2)

    # Drawing on the Vertical image
    logging.info("2.Drawing on the Vertical image...")
    LBlackimage = Image.new("1", (Epd.width, Epd.height), 255)  # 126*298
    LRYimage = Image.new("1", (Epd.width, Epd.height), 255)  # 126*298
    drawblack = ImageDraw.Draw(LBlackimage)
    drawry = ImageDraw.Draw(LRYimage)

    drawblack.text((2, 0), "hello world", font=font18, fill=0)
    drawblack.text((2, 20), "2.13 epd b", font=font18, fill=0)
    drawblack.text((20, 50), "微雪电子", font=font18, fill=0)
    drawblack.line((10, 90, 60, 140), fill=0)
    drawblack.line((60, 90, 10, 140), fill=0)
    drawblack.rectangle((10, 90, 60, 140), outline=0)
    drawry.rectangle((10, 150, 60, 200), fill=0)
    drawry.arc((15, 95, 55, 135), 0, 360, fill=0)
    drawry.chord((15, 155, 55, 195), 0, 360, fill=1)
    Epd.display(Epd.getbuffer(LBlackimage), Epd.getbuffer(LRYimage))
    time.sleep(2)

    logging.info("3.read bmp file")
    HBlackimage = Image.open(os.path.join(picdir, "2in13bc-b.bmp"))
    HRYimage = Image.open(os.path.join(picdir, "2in13bc-ry.bmp"))
    Epd.display(Epd.getbuffer(HBlackimage), Epd.getbuffer(HRYimage))
    time.sleep(2)

    logging.info("4.read bmp file on window")
    blackimage1 = Image.new("1", (Epd.height, Epd.width), 255)  # 298*126
    redimage1 = Image.new("1", (Epd.height, Epd.width), 255)  # 298*126
    newimage = Image.open(os.path.join(picdir, "100x100.bmp"))
    blackimage1.paste(newimage, (10, 10))
    Epd.display(Epd.getbuffer(blackimage1), Epd.getbuffer(redimage1))

    logging.info("Clear...")
    Epd.init()
    Epd.Clear()

    logging.info("Goto Sleep...")
    Epd.sleep()


def clear():
    Epd.Clear()


def name_badge():
    clear()
    Markers.Red.value.rectangle((0, 0, Epd.height, Epd.width), fill=0)
    draw_text("Brad Brown", (15, 0), 30, Markers.Black, fill=1)
    draw_text("W5BUB", (10, 40), 40, Markers.Red, fill=1)
    write_buffers()
    Epd.sleep()


def name_badge_img():
    clear()
    black_img = Image.open(picdir / "badge_b.bmp")
    red_img = Image.open(picdir / "badge_ry.bmp")
    Epd.display(Epd.getbuffer(black_img), Epd.getbuffer(red_img))
    Epd.sleep()


FUNC_DICT = {
    "name_badge": name_badge,
    "badge_img": name_badge_img,
    "clear": clear,
    "demo": demo,
}


if __name__ == "__main__":
    func = name_badge
    if len(sys.argv) > 1:
        func = FUNC_DICT.get(sys.argv[1], func)

    try:
        func()
    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c")
        epd2in13bc.epdconfig.module_exit()
    finally:
        exit()
