from PIL import Image

from conf.conf import logo_png_path, logo_icon_path

size = (256, 256)
im = Image.open(logo_png_path).resize(size)
im.save(logo_icon_path)
