'''Functions'''

import cv2

def bgr2bw (img,LTL=120,UTL=255):
    '''Take an image and convert it to grayscale.
    Then, convert it to pure black and white ( binary channel )using a given threshold.
    Convert it again to BGR to display it with BGR channels.'''
    gray_img= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bw_img= cv2.threshold(gray_img , LTL, UTL, cv2.THRESH_BINARY)
    RE_BGR = cv2.cvtColor(bw_img, cv2.COLOR_GRAY2BGR)
    return bw_img , RE_BGR

def crop(img,x_start ,y_start ,w_new=.2,h_new=.2):
    
    height, width = img.shape[:2]
    
    x,w=int(x_start *width),int(w_new *width)
    y,h=int(y_start *height),int(h_new *height)

    return img [y:y+h, x:x+w]