# import 套件
import csv
import boto3
import cv2
import time
import io
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

'''
------------------------------------------------------------------------
Part 1: 攝影機記錄使用者
------------------------------------------------------------------------
'''
# cap = cv2.VideoCapture(0)  # 啟用(零號)相機
# # 參數 cv2.CAP_DSHOW 是微軟特有的，用來防止釋放攝影鏡頭時的[ WARN:0] terminating async callback警告
# milli = int(round(time.time() * 1000))
#
# while (True):  # while 迴圈 在這裡一直都是 true 不會跳離開，會永遠亮著開啟
#
#     milli = 2 * 1000  # 2*1000 毫秒(秒)
#     cv2.waitKey(milli)  # waitkey 等他 2 秒 讓鏡頭先暖機 2 秒
#
#     time.sleep(3)  ##延遲執行的秒數: (設定3秒)
#
#     ret, frame = cap.read()  # 拍一張照片，在這個無窮迴圈中，每次呼叫 cap.read() 就會讀取一張影像，其第一個傳回值 ret 代表成功與否 (True 代表成功，False 代表失敗)，而第二個傳回值 frame 就是攝影機的單張照片。
#     cv2.imshow('frame', frame)  # 跑出視窗讓我知道攝影鏡頭有開啟
#     cv2.imwrite('guest.jpg', frame)  # 照到的影像要存成什麼檔名
#     break  # 用來終止 while 迴圈     # if cv2.waitKey(1) & 0xFF == ord('q'): #若按下 q 則離開迴圈
#
# cap.release()  # 關閉相機
# cv2.destroyAllWindows()  # 關閉視窗
'''
------------------------------------------------------------------
Part 2: AWS帳號－－讀取金鑰 csv 檔案 (executable)
------------------------------------------------------------------
'''

# 讀取iam生成之 access_key  secret_access_key
with open('C:/Users/yuniy/Desktop/New pioneers in the industry/Python-Programming Language/Python code and GUI course/accessKeys.csv','r') as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[0]
        secret_access_key = line[1]
print(line)
type(line)

# rekognition
client = boto3.client('rekognition',
                      aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key,
                      region_name='us-west-2')

'''
-------------------------------------------------------------------------------------------
Part 3: 指定必須穿戴的 PPE 類型回傳 SummarizationAttributes ，顯示可疑人物人數。                      
-------------------------------------------------------------------------------------------
'''


def detect_Suspicious_person(photo):  # 定義涵式
    # 要讀取之檔案

    photo = 'Gun_1.jpg'
    with open(photo, 'rb') as imgfile:  # 開啟先前利用攝影鏡頭照到的照片來做分析
        imgbytes = imgfile.read()  # 指定 Bytes 屬性，以傳遞 base64 編碼的影像位元組(以二進制的形式來讀取圖片)

    response = client.detect_protective_equipment(Image={'Bytes': imgbytes},
                                                  SummarizationAttributes={'MinConfidence': 50,
                                                                           'RequiredEquipmentTypes': ['HEAD_COVER',
                                                                                                      'FACE_COVER',
                                                                                                      'HAND_COVER']})
    # SummarizationAttributes:全部屬性(type)      MinConfidence:最小信賴區間
    # RequiredEquipmentTypes : 指定人員要穿戴的 PPE 類型到 summaryAttributes， RequiredEquipmentTypes 的值為 list:[ FACE_COVER | HAND_COVER | HEAD_COVER]

    suspicious_person = response["Summary"][
        "PersonsWithRequiredEquipment"]  # 三個部位都有遮掩的人被判定為可疑人物，回傳符合指定的 Attributes 的人員 ID

    person_count = len(response['Persons'])
    num_of_suspicious_person = len(suspicious_person)  # 計算符合指定 Attributes 的人數

    print('Detected PPE for people in image ' + photo)  # 印分析的照片檔名出來
    if num_of_suspicious_person >= 1:
        print()
        print(f"suspicious_person ID: {suspicious_person}")

    suspiciousperson = '可疑人物人數:', num_of_suspicious_person

    ppeitemlabel = []
    count = 0
    for person in response['Persons']:
        for body_part in person['BodyParts']:
            ppe_items = body_part['EquipmentDetections']
            for ppe_item in ppe_items:
                ppeitemlabel.append(ppe_item)

        count += 1
        if count != 3: continue

    for ppelabl in ppeitemlabel:
        PPEinfo = str(ppelabl["Type"]) + '\n\tCovers body part: ' + str(
            ppelabl["CoversBodyPart"]["Value"]) + '\n\tConfidence: ' + '\n\t' + str(
            ppelabl["CoversBodyPart"]["Confidence"])

    return person_count, num_of_suspicious_person, suspiciousperson, PPEinfo


# 回傳 person_count 給 main() 涵式計算總人數;回傳 num_of_suspicious_person 給 main() 函式計算可疑人物總人數; 回傳 suspiciousperson、PPEinfo 值 作為  GUI 參數


'''
-------------------------------------------------------------------------------------------
Part 4: 顯示圖片並框出可疑人物與 PPE 位置   (executable)                           
-------------------------------------------------------------------------------------------
'''


# Draw frames and show       根據信賴區間框出 PPE 位置
def detect_ppe(photo, confidence):
    fill_green = '#00d400'  # 完全有戴 框框呈綠色
    fill_red = '#ff0000'  # 完全沒戴 框框呈紅色
    fill_yellow = '#ffff00'  # 信賴區間判讀不夠呈黃色
    line_width = 3  # 框線粗度

    # open image and get image data from stream.
    image = Image.open(open(photo, 'rb'))
    stream = io.BytesIO()  # 利用 io 套件 以bytes 形式讀取
    image.save(stream, format=image.format)
    image_binary = stream.getvalue()
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    response = client.detect_protective_equipment(Image={'Bytes': image_binary},
                                                  SummarizationAttributes={'MinConfidence': 50,
                                                                           'RequiredEquipmentTypes': ['HEAD_COVER',
                                                                                                      'FACE_COVER',
                                                                                                      'HAND_COVER']})

    suspicious_person = response["Summary"][
        "PersonsWithRequiredEquipment"]  # 三個部位都有遮掩的人被判定為可疑人物，回傳符合指定的 Attributes 的人員 ID

    num_of_suspicious_person = len(suspicious_person)  # 計算符合指定 Attributes 的人數
    found_suspicious_person = False
    if num_of_suspicious_person >= 1:
        found_suspicious_person = True

    if found_suspicious_person == True:
        for person_id in suspicious_person:
            suspicious_person = response["Persons"][person_id]
            box = suspicious_person["BoundingBox"]
            left = imgWidth * box["Left"]
            top = imgHeight * box["Top"]
            width = imgWidth * box["Width"]
            height = imgHeight * box["Height"]
            points = (
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top)
            )
            draw.line(points, fill=fill_red, width=line_width)
            for body_part in suspicious_person['BodyParts']:
                ppe_items = body_part['EquipmentDetections']
                for ppe_item in ppe_items:
                    print('\t\t' + ppe_item['Type'] + '\n\t\t\tConfidence: ' + str(ppe_item['Confidence']))
                    print('\t\t\tCovers body part: ' + str(
                        ppe_item['CoversBodyPart']['Value']) + '\n\t\t\tConfidence: ' + str(
                        ppe_item['CoversBodyPart']['Confidence']))

                    if ppe_item['Type'] == 'FACE_COVER' or "HEAD_COVER" or "HAND_COVER":
                        # draw bounding box around PPE
                        box = ppe_item['BoundingBox']
                        left = imgWidth * box['Left']
                        top = imgHeight * box['Top']
                        width = imgWidth * box['Width']
                        height = imgHeight * box['Height']
                        points = (
                            (left, top),
                            (left + width, top),
                            (left + width, top + height),
                            (left, top + height),
                            (left, top)
                        )
                        draw.line(points, fill=fill_red, width=line_width)

                        # image.show()
    image = image.convert("RGB")
    image.save("Gun_1 analysis.jpg")


'''
-------------------------------------------------------------------------------------------
Part 5: Detect Label 偵測影像是否有刀子、槍等武器
-------------------------------------------------------------------------------------------
'''


def detect_labels(photo):
    photo = 'Gun_1.jpg'
    with open(photo, 'rb') as imgfile:  # 開啟先前利用攝影鏡頭照到的照片來做分析
        imgbytes = imgfile.read()  # 指定 Bytes 屬性，以傳遞 base64 編碼的影像位元組(以二進制的形式來讀取圖片)

    response = client.detect_labels(Image={'Bytes': imgbytes}, MaxLabels=2580)

    found_robber = False
    print('Detected labels for ' + photo)
    print()
    detectedlabel = []  #存放照片中偵測到的所有標籤
    for label in response['Labels']:
        detectedlabel.append(label['Name'])
    
        print("Label: " + label['Name'])
        print("Confidence: " + str(label['Confidence']))
        
        print("Instances:")  
        for instance in label['Instances']:
            print("  Bounding box")
            print("    Top: " + str(instance['BoundingBox']['Top']))
            print("    Left: " + str(instance['BoundingBox']['Left']))
            print("    Width: " + str(instance['BoundingBox']['Width']))
            print("    Height: " + str(instance['BoundingBox']['Height']))
            print("  Confidence: " + str(instance['Confidence']))
            print()

        
        if label["Name"] == "Gun" or "Knife" or "Axe" or "Sword":
            found_robber = True           
            
               
        weaponinfo ='發現搶匪攜帶武器!!!\n武器標籤:'
        labelinfo = '\n\n系統偵測到的標籤:' + '\n'
        count = 0
        for weapon in detectedlabel:
            if weapon == "Gun": weaponinfo += " Gun"
            if weapon == "Knife": weaponinfo += " Knife"
            if weapon == "Axe": weaponinfo += " Axe"
            if weapon == "Sword": weaponinfo += " Sword"
            labelinfo += f"{weapon}"
            count += 1
            if count != len(detectedlabel):
                labelinfo += ", "
            

     # 偵測到的 ParentLabel 類別標籤  
        for parent in label['Parents']:
            print("Parents Label: " + parent['Name'])
            if parent["Name"] == "Weapon":
                found_robber = True

        print("----------------")
        print()

    return len(response['Labels']), found_robber, weaponinfo, labelinfo


'''
-------------------------------------------------------------------------------------------
Part 6: Detect Moderating content 偵測影像中不適當內容、冒犯性內容-暴力
-------------------------------------------------------------------------------------------
'''


def moderating_content(photo):
    photo = 'Gun_1.jpg'
    with open(photo, 'rb') as imgfile:  # 開啟照片來做分析
        imgbytes = imgfile.read()  # 指定 Bytes 屬性，以傳遞 base64 編碼的影像位元組(以二進制的形式來讀取圖片)

    response = client.detect_moderation_labels(Image={'Bytes': imgbytes})  # 呼叫偵測照片的API

    found_robber = False
    print('Detected labels for ' + photo)
    ModerationLabelvalue = []
    for label in response['ModerationLabels']:
        print(label['Name'] + ' : ' + str(label['Confidence']))   #分析影像中不當內容的類別標籤
        print(label['ParentName'])
        
        if label['ParentName'] == "Violence":
            found_robber = True
        elif label['Name'] == "Violence" or "Graphic Violence Or Gore" or "Physical Violence" or "Weapon Violence":
            found_robber = True
            
        ModerationLabelvalue.append(label['Name'], )  #將偵測到的次標籤加到串列中

 # 內容管制的偵測資訊(為了顯示文字在警告視窗的資訊欄，影像中出現的冒犯性內容標籤)
    moderatinginfo = "系統判斷影像出現冒犯性內容:" + '\n'
    count = 0
    for moderationlabel in ModerationLabelvalue:
        count += 1
        moderatinginfo += moderationlabel
        if count != len(ModerationLabelvalue):
            moderatinginfo += ", "

    return len(response['ModerationLabels']), found_robber, moderatinginfo


'''
-------------------------------------------------------------------------------------------
Part 6: 警示音
-------------------------------------------------------------------------------------------
'''


# pip install playsound
def alert():
    from playsound import playsound
    playsound('Alert.wav', block=True)


# import os   確認檔案路徑
# os.path.dirname(os.path.abspath('Alert.wav'))


'''
-------------------------------------------------------------------------------------------
Part 7: 可疑人物警告視窗
-------------------------------------------------------------------------------------------
'''
#建立主視窗(GUI 主框架)

def GUI_suspicious(suspiciousperson, PPEinfo):
    window = tk.Tk()  # 定義一個主視窗(GUI 主框架) 名叫 window
    window.title('< 9 安全防護系統 >                       !!! 警告視窗 !!!')  # 設定框架標題
    window.configure(background='white')  # 更改背景顏色


#建立 Frame (把元件變成群組的容器)，區隔主視窗空間的區塊
    frame_size = 100
    img_size = frame_size * 9
    frame1 = tk.Frame(window, width=img_size, height=img_size, bg='white')
    frame2 = tk.Frame(window, width=frame_size, height=frame_size, bg='white')


    window.update()  # 更新每次縮放視窗的長寬
    win_size = min(window.winfo_width(), window.winfo_height())
    print(win_size)


    align_mode = 'news'  # align_mode 對齊方式，而給予字串 ‘nswe’ 是置中的意思 ( n 上 s 下 w左 e 右)：
    pad = 5  # 上下左右各添加多少 ( pixel )
    # sticky 是對齊方式，這邊用 align_mode 來統一所有的對齊方式，而給予字串 ‘nswe’ 是置中的意思 ( n 上 s 下 w左 e 右)：

    frame1.grid(column=0, row=0, padx=pad, pady=pad, rowspan=2, sticky=align_mode)
    frame2.grid(column=1, row=0, padx=pad, pady=pad, sticky=align_mode)


    #函式(define_layout)用來定義縮放時區塊的比例，引入 obj 為 UI widget、cols 該 widget 中有幾欄、row 該 widget 中有幾列
    def define_layout(obj, cols=1, rows=1):  # obj = UI widget

        def method(trg, col, row):  # trg = frame

            for c in range(cols):
                trg.columnconfigure(c, weight=1)
            for r in range(rows):
                trg.rowconfigure(r, weight=1)

        if type(obj) == list:
            [method(trg, cols, rows) for trg in obj]
        else:
            trg = obj
            method(trg, cols, rows)

    img = Image.open(
        'Gun_1 analysis.jpg')
    imgTK = ImageTk.PhotoImage(img.resize((img_size, img_size)))

    image_main = tk.Label(frame1, image=imgTK)
    image_main['height'] = img_size
    image_main['width'] = img_size
    image_main.grid(column=0, row=0, sticky=align_mode)


    label_title1 = tk.Label(frame2, text='警告!!! 出現可疑人物', bg='red', fg='white', font=('標楷體', 24))
    label2 = tk.Label(frame2, text="資訊欄 :", bg='white', fg='black', font=('標楷體', 18), anchor='w')
    label3 = tk.Label(frame2, text=suspiciousperson, bg='white', fg='orange', font=('標楷體', 18), wraplength=500,
                      justify='left', anchor='w')
    label4 = tk.Label(frame2, text=PPEinfo, bg='white', fg='orange', font=('Times New Romance', 18), wraplength=500,
                      justify='left', anchor='w')


    label_title1.grid(column=0, row=0, sticky=align_mode)
    label2.grid(column=0, row=1, sticky='nw')
    label3.grid(column=0, row=2, sticky='nw')
    label4.grid(column=0, row=3, sticky='nw')


    define_layout(window, cols=2, rows=1)
    define_layout(frame1)
    define_layout(frame2, rows=4)

    alert()
    window.mainloop()


'''
-------------------------------------------------------------------------------------------
Part 8: 搶匪警告視窗
-------------------------------------------------------------------------------------------
'''


def GUI_Robber(weaponinfo,labelinfo,  moderatinginfo):
    window = tk.Tk()
    window.title('< 9 安全防護系統 >                     !!!  警告視窗  !!!')
    window.configure(background='white')
    align_mode = 'news'  # align_mode 來統一所有的對齊方式，而給予字串 ‘nswe’ 是置中的意思 ( n 上 s 下 w左 e 右)：
    pad = 5  # 上下左右各添加多少 ( pixel )

    frame_size = 100
    img_size = frame_size * 9
    frame1 = tk.Frame(window, width=img_size, height=img_size, bg='white')
    frame2 = tk.Frame(window, width=frame_size, height=frame_size, bg='white')

    window.update()
    win_size = min(window.winfo_width(), window.winfo_height())
    print(win_size)

    
    frame1.grid(column=0, row=0, padx=pad, pady=pad, rowspan=2, sticky=align_mode)
    frame2.grid(column=1, row=0, padx=pad, pady=pad, sticky=align_mode)
    
 
    def define_layout(obj, cols=1, rows=1):

        def method(trg, col, row): 

            for c in range(cols):
                trg.columnconfigure(c, weight=1)
            for r in range(rows):
                trg.rowconfigure(r, weight=1)

        if type(obj) == list:
            [method(trg, cols, rows) for trg in obj]
        else:
            trg = obj
            method(trg, cols, rows)

    img = Image.open(
        'Gun_1 analysis.jpg')
    imgTK = ImageTk.PhotoImage(img.resize((img_size, img_size)))

    image_main = tk.Label(frame1, image=imgTK)
    image_main['height'] = img_size
    image_main['width'] = img_size

    image_main.grid(column=0, row=0, sticky=align_mode)

    label_title1 = tk.Label(frame2, text='警告!!! 出現搶匪', bg='red', fg='white', font=('標楷體', 24))

    label2 = tk.Label(frame2, text= "資訊欄 :", bg='white', fg='black', font=('標楷體', 18), anchor='w')
    label3 = tk.Label(frame2, text= weaponinfo + labelinfo, bg='white', fg='orange', font=('標楷體', 18), wraplength=500,
                      justify='left', anchor='w')

    label4 = tk.Label(frame2, text= moderatinginfo, bg='white', fg='orange', font=('標楷體', 18), wraplength=500,
                      justify='left', anchor='w')
    # wraplength：指定多少單位後開始換行，justify:指定多行的對齊方式，ahchor：指定文字(text)在 Label 中的顯示位置

    label_title1.grid(column=0, row=0, sticky=align_mode)
    label2.grid(column=0, row=1, sticky='nw')
    label3.grid(column=0, row=2, sticky='nw')
    label4.grid(column=0, row=3, sticky='nw')

    define_layout(window, cols=2, rows=1)
    define_layout(frame1)
    define_layout(frame2, rows=4)

    alert()
    window.mainloop()


'''
-------------------------------------------------------------------------------------------
Part Main
-------------------------------------------------------------------------------------------
'''


def main():
    photo = 'Gun_1.jpg'
    person_count, num_of_suspicious_person, suspiciousperson, PPEinfo = detect_Suspicious_person(photo)
    print("Persons detected: " + str(person_count))
    print("Suspicious person detected: ", num_of_suspicious_person)
    confidence = 50
    detect_ppe(photo, confidence)
    label_count, found_robber, weaponinfo, labelinfo = detect_labels(photo)
    print("Labels detected: " + str(label_count))
    print("Labels detected: " + str(label_count))
    moderationlabel_count, found_robber, moderatinginfo = moderating_content(photo)
    print("ModeratingLabels detected: " + str(moderationlabel_count))
    
    if found_robber == True:
        GUI_Robber(weaponinfo, labelinfo, moderatinginfo)
    elif num_of_suspicious_person >= 1:
        GUI_suspicious(suspiciousperson, PPEinfo)


if __name__ == "__main__":
    main()







'''
播放音效參考資料
https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
https://www.geeksforgeeks.org/play-sound-in-python/

'''
