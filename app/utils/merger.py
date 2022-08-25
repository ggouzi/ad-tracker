#!/usr/bin/env python
from PIL import Image
from urllib.request import Request, urlopen
from datetime import datetime
import traceback


def get_image_from_url(url):
	try:
		req = Request(url)
		with urlopen(req) as u:
			img = Image.open(u)
			return img
	except Exception as e:
		print(str(e))
		print(traceback.format_exc())
		return None


def resize(img, basewidth=300):
	wpercent = (basewidth/float(img.size[0]))
	hsize = int((float(img.size[1])*float(wpercent)))
	img = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
	return img


def get_concat_h_blank(im1, im2, color=(0, 0, 0)):
	if im1 is None:
		return im2
	dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
	dst.paste(im1, (0, 0))
	dst.paste(im2, (im1.width, 0))
	return dst


def get_concat_v_blank(im1, im2, color=(0, 0, 0)):
	if im1 is None:
		return im2
	dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color)
	dst.paste(im1, (0, 0))
	dst.paste(im2, (0, im1.height))
	return dst


def concat_multi(im_list, limit_h):
	t, h = [], []
	for idx, im in enumerate(im_list):
		if idx < limit_h:
			h.append(resize(im))
		else:
			t.append(h)
			h = [im]
			limit_h += limit_h
	t.append(h)

	# Concat horizontally by line
	result = []
	for line in t:
		_im = None
		for im in line:
			_im = get_concat_h_blank(_im, resize(im), True)
		result.append(_im)

	# Concat vertically by concatenated-line & resize last line to fit previous lines width
	_im, width = None, None
	for idx, im in enumerate(result):
		current_width = im.size[0]
		if width is None:
			width = current_width
		if current_width != width:
			_im = get_concat_v_blank(_im, resize(im, width), False)
		else:
			_im = get_concat_v_blank(_im, im, False)
	return _im


def nearest_square(limit):
	if limit <= 2:
		return 1
	if limit <= 4:
		return 2
	if limit == 5:
		return 3
	available_limits = [2,3,4,5]
	sq = (limit ** 0.5)
	for i in available_limits:
		if sq % i == 0:
			return i

	min_i = 1

	for i in range(2, int(sq)+2 ):
		if (limit % i) >= min_i:
			min_i = i
	if min_i <= 2:
		return 3
	return min_i


def generate_filename(suffix, extension):
	seed = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
	return f"medias/output/{suffix}_{seed}.{extension}"


def merge_image_list(rawList):
	list_images = []

	for l in rawList:
		if l is not None:
			list_images.append(l)
	list_images.sort(key=lambda x: x.size[0])
	limit_h = nearest_square(len(list_images))

	filename = generate_filename(suffix="merged", extension="png")
	if len(list_images) > 0:
		concat_multi(list_images, limit_h).save(filename)
		print(f"Merge images in {filename}")
		return filename
	return None