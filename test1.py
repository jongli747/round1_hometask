import cv2 
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from pytesseract import Output
import re
import ftfy

refPt = []
cropping = False

def click_crop(event, x, y, flags, param):
    global refPt, cropping, num
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    if event == cv2.EVENT_LBUTTONUP:
        num += 1
        refPt.append((x, y))
        cropping = False        
        cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def get_ocr_output(image):
    raw_output = pytesseract.image_to_string(image, lang='eng')
    text = re.sub(r'[^\da-zA-Z0-9_() \n]+', '', raw_output)
    # print(text.splitlines())
    
    text = ftfy.fix_text(text)
    text = ftfy.fix_encoding(text)
    # print(text.splitlines())

    lines = text.split('\n')
    lines = more_clean(lines)
    # print(lines)
    print(get_information(lines))


def more_clean(lines):
    clear_lines = []
    for line in lines:
        s = line.strip()
        s = line.replace('\n', '')
        s = s.rstrip()
        s = s.lstrip()
        s = re.sub(r'\b[a-z]+\s*', '',s)
        clear_lines.append(s)
    clear_lines = list(filter(None,clear_lines))
    return clear_lines

def get_name(s):
    name_regex = re.compile(r'^[A-Z\s]+$')
    name = name_regex.search(s)
    if name != None:
        return name.group()

def get_dob(s):
    dob_regex = re.compile(r'\d\d\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}')
    dob = dob_regex.search(s)
    if dob != None:
        return dob.group()

def get_nid(s):
    nid_regex = re.compile(r'\d{3} \d{3} \d{4}|\d{6} \d{4}')
    nid = nid_regex.search(s)
    if nid != None:
        return nid.group()
    return 

def get_information(text):
    output_dict = {'Name': None, 'Date of Birth': None, 'NID No.': None}
    for t in range(len(text)):
        name = get_name(text[t])
        if output_dict['Name'] == None:
            output_dict['Name'] = name
        dob = get_dob(text[t])
        nid = get_nid(text[t])
        
        if dob != None:
            if int(dob[0]) > 2:
                temp = list(dob)
                temp[0] = '0'
                temp = ''.join(temp)
                dob = temp
            output_dict['Date of Birth'] = dob
        output_dict['NID No.'] = nid
    return output_dict


if __name__ == "__main__":
    num = 0

    windowName = 'Pre-processing Window'
    img = cv2.imread('./images/5.jpg', cv2.IMREAD_COLOR)
    img = cv2.resize(img, (1024,1024), interpolation=cv2.INTER_AREA)
    clone = img.copy()
    cv2.namedWindow(windowName)

    cv2.setMouseCallback(windowName, click_crop)

    num = 0
    if len(refPt) == 2:
        num += 1

    while True:
        cv2.imshow(windowName, img)
        key = cv2.waitKey(1)
        if key == ord("r"): 
            img = clone.copy()
        elif key == ord("s"):   
            roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            cv2.imwrite('roi{}.jpg'.format(num), roi)            
        elif key == ord("c"):  
            break    
    cv2.destroyAllWindows()

    roi = cv2.cvtColor(roi,cv2.COLOR_BGR2RGB)
    roi = get_grayscale(roi)
    # plt.imshow(roi)
    # plt.show()

    get_ocr_output(roi)