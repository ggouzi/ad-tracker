from PIL import Image
from urllib.request import Request, urlopen
from datetime import datetime
from random import shuffle
import traceback
import time


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


def resize(img, basewidth=800):
	if img is None:
		return None
	wpercent = (basewidth / float(img.size[0]))
	hsize = int((float(img.size[1]) * float(wpercent)))
	img = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
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
	orig_limit_h = limit_h

	for idx, im in enumerate(im_list):
		if idx < limit_h:
			h.append(im)
		else:
			t.append(h)
			h = [im]
			limit_h += orig_limit_h
	t.append(h)

	# Concat horizontally by line
	result = []
	for line in t:
		_im = None
		for im in line:
			_im = get_concat_h_blank(_im, resize(im), True)
		result.append(_im)

	# Concat vertically by concatenated-line & resize last line to fit previous lines width
	_im = None

	for im in result:
		_im = get_concat_v_blank(_im, resize(im), False)
	return _im


def nearest_square(limit):
	if limit <= 3:
		return 1
	if limit <= 4:
		return 2
	if limit == 5:
		return 5

	sq = int((limit ** 0.5))
	return sq


def generate_filename(suffix, extension):
	seed = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
	return f"medias/merged/{suffix}_{seed}.{extension}"


def getSublists(lst, n):
	subListLength = len(lst) // n
	for i in range(0, len(lst), subListLength):
		yield lst[i:i + subListLength]


def merge_image_list(rawList, number_images):
	list_images = []
	shuffle(rawList)

	for l in rawList:
		if l is not None:
			list_images.append(l)
	list_images.sort(key=lambda x: x.size[0])
	limit_h = nearest_square(len(list_images))
	print(limit_h)

	if number_images is None:
		number_images = 1

	filenames = []
	if len(list_images) > 0:
		lists_images = list(getSublists(list_images, number_images))
		for l in lists_images:
			filename = generate_filename(suffix="merged", extension="png")
			concat_multi(l, limit_h).save(filename)
			time.sleep(1)
			print(f"Merge images in {filename}")
			filenames.append(filename)
	return filenames
