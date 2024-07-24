"""! @brief Renamer to modify the name of form 1040, apply watermarks on all pages , change EIN of the Owner 'brian' and the address
 @file renamer_v11.py
 @section libs Librairies/Modules
  - fitz (lien)
  - tkinter (lien)
  - tkinter (lien)
  - tkinter (lien)
  - tkinter.messagebox (lien)
  - os (lien)
  - base64 (lien)
  - io (lien)
  - PIL (lien)
  - fitz (lien)
  - Watermark (lien)
 @section authors Auteur(s)
  - Créé par [Name] [Last Name] le 7/5/2024 .
"""
from fitz import * 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import os
import base64
from io import BytesIO
from PIL import Image, ImageTk
import fitz
from Watermark import base64_bytes_watermark
import time
from TNRB import base64_bytes_Times_New_Roman_Bold
from AB import base64_bytes_arial_black
#GUI Params
root = tk.Tk()
root.title('Form 1040 Renamer v1')
root.resizable(False, False)
root.geometry('700x400')

# style choose
style = ttk.Style()
style.configure("Large.TCheckbutton", font=("Arial", 13))


# fonts 
new_fonts={"Arial-Black":base64_bytes_arial_black,"TimesNewRoman,Bold":base64_bytes_Times_New_Roman_Bold}

EIN=None
#Backend params
Form_8879_PE="8879-PE"
Form_1065="1065"
form_k1="Schedule K-1 \n(Form 1065)"


image = Image.open(BytesIO(base64.b64decode(base64_bytes_watermark)))
image = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=image,pady=50)
image_label.pack()

#Function to modify a specific text field in a pdf page
def search_and_replace(page,to_search_and_replace,one_time):
    try:
        for b in page.get_text("dict",sort=True)["blocks"]:
            for l in b["lines"]:
                for s in l['spans']:
                    xl=Rect(s['bbox']).tl.x
                    yl=Rect(s['bbox']).tl.y
                    xr=Rect(s['bbox']).br.x
                    yr=Rect(s['bbox']).br.y     
                    font_size=yr-yl  
                    text_font=l['spans'][0]['size']
                    font_name_extracted=l['spans'][0]['font']



                    for to_search in list(to_search_and_replace.keys()):


    
                        if(to_search in s['text']):

                            
                            text_lenght = fitz.get_text_length(to_search_and_replace[to_search], fontname="Courier", fontsize=int(text_font))

                            rect_x2 = xl + text_lenght + 2  # needs margin
                            rect_y2 = yl + font_size + 2  # needs margin
                            Bbox_text=Rect(xl,yl,rect_x2,rect_y2)
                            if(font_name_extracted in new_fonts):
                                page.insert_font(fontname=font_name_extracted,fontbuffer=BytesIO(base64.b64decode(new_fonts[font_name_extracted])))
                                page.insert_text((0,0),  # anywhere, but outside all redaction rectangles
                                    "something",  # some non-empty string
                                    fontname=font_name_extracted,  # new, unused reference name
                                    render_mode=3,  # makes the text invisible
                                )
                                page.apply_redactions()
                            annot=page.add_redact_annot(Bbox_text, to_search_and_replace[to_search], fontname=font_name_extracted, fill=False,fontsize=font_size,align=TEXT_ALIGN_LEFT)  # more parameters
                            # page.insert_text((75.98400115966797, 651.4600219726562), to_search_and_replace[to_search], fontsize=18, fontname=font_name_extracted)

                            if(one_time):
                                return
    except:
        pass

def run(doc,EIN,file_path,file_name):
    
    i=0
    
    EIN_masked=None
    try:
        for page in doc:
            for l in page.get_text_blocks(sort=True):
                if str(l[0])[:4]==str(57.4): #00001525878906
                    EIN_masked=l[4][:-1]
                    break
            if(EIN_masked):
                break
        
        for page in doc:
            selector=page.get_text_blocks()[0][4]

            search_and_replace(page,{"Brian A. Lang":"US-Expat.tax"},False)

            if "1040" in selector:
                search_and_replace(page,{"1125 Maxwell Lane, #1124 Hoboken NJ 07030":"1125 Maxwell Lane, #1124 Hoboken NJ 07030"},False)
                page.apply_redactions(images=PDF_REDACT_IMAGE_NONE )
                break

            if(Form_8879_PE in selector):
                pass
                
            elif(Form_1065 in selector):
                pass

            i+=1
            page.apply_redactions(images=PDF_REDACT_IMAGE_NONE )
            
    except Exception as e:
        print(str(e))
        pass            
    
    doc.saveIncr()


def select_file():
    global EIN
    filetypes = (
        ('pdf files', '*.pdf'),
        ('All files', '*.*')
    )
    current_path=os.getcwd()
    
    filenames = fd.askopenfilenames(
        title='Open a file',
        initialdir=current_path,
        filetypes=filetypes)
    
    if(len(filenames)!=0):
        
        for file in filenames:
            doc = open(file)
            file_name=file.split('/')[-1].split('_')[0]

            file=file[:len(file)-file[::-1].find('/')]
            run(doc,EIN,file,file_name)

        
        showinfo(
            title='Selected File',
            message="Success"
        )

    else:
        showinfo(
            title='Error',
            message="Select a file or multiple files please"
        )


open_button = ttk.Button(
    root,
    text='Open a File',
    command=select_file
).place(x=310, y=360)

# run the application
root.mainloop()


