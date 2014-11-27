# Copyright 2014 Utkarsh Jaiswal
# Adopted from the Python Tesseract project - https://code.google.com/p/python-tesseract/

import tesseract
import sys

api = tesseract.TessBaseAPI()

# Initialize Tesseract to recognize English characters
# The first argument must point to your tessdata/ folder that contains trained data
# and configs for the language you're using
api.Init(".", "eng", tesseract.OEM_DEFAULT)

# Set a character whitelist to improve accuracy
# The list used here restricts characters to ones found in guitar tabs
api.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGabcdefghp-\/|")

# Set a page segmentation mode to improve accuracy
# Further details can be found at - http://fossies.org/dox/tesseract-ocr-3.02.02/namespacetesseract.html#a338d4c8b5d497b5ec3e6e4269d8ac66a
api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)

mImgFile = sys.argv[1]
mBuffer = open(mImgFile, "rb").read()

result = tesseract.ProcessPagesBuffer(mBuffer, len(mBuffer), api)

print "OCRed tab -"
print result

api.End()
