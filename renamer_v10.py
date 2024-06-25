from fitz import * 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import os
import base64
from io import BytesIO
from PIL import Image, ImageTk
from icon_renamer import base64_bytes_image
import fitz
from Watermark import base64_bytes_watermark


#GUI Params
root = tk.Tk()
root.title('Renamer v10')
root.resizable(False, False)
root.geometry('700x350')

# style choose
style = ttk.Style()
style.configure("Large.TCheckbutton", font=("Arial", 13))
watermark_bool=tk.BooleanVar()

#function to check the revere_name var
def watermark_set():
    if(watermark_bool.get()):
        tk.messagebox.showinfo(title='Info',
            message="Watermark added")
    else:
        tk.messagebox.showinfo(title='Info',
            message="No Watermark added")  

ttk.Checkbutton(root, style="Large.TCheckbutton",
                text='Add Watermark',
                command=watermark_set,
                variable=watermark_bool,
                onvalue=True,
                offvalue=False).place(x=300, y=260)


EIN=None
#Backend params
Form_8879_PE="8879-PE"
Form_1065="1065"
form_k1="Schedule K-1 \n(Form 1065)"


image = Image.open(BytesIO(base64.b64decode(base64_bytes_image)))
image = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=image,pady=50)
image_label.pack()

#Function to modify a specific text field in a pdf page
def search_and_replace(page,to_search_and_replace,one_time):

    for b in page.get_text("dict",sort=True)["blocks"]:
        for l in b["lines"]:
            for s in l['spans']:
                xl=Rect(s['bbox']).tl.x
                yl=Rect(s['bbox']).tl.y
                xr=Rect(s['bbox']).br.x
                yr=Rect(s['bbox']).br.y     
                font_size=yr-yl  
                for to_search in list(to_search_and_replace.keys()):
                    #print(s['text'])
                    if(to_search in s['text']):
                        text_lenght = fitz.get_text_length(to_search_and_replace[to_search], fontname="Courier", fontsize=10)
                        rect_x2 = xl + text_lenght + 2  # needs margin
                        rect_y2 = yl + font_size + 2  # needs margin
                        Bbox_text=Rect(xl,yl,rect_x2,rect_y2)
                        annot=page.add_redact_annot(Bbox_text, to_search_and_replace[to_search], fontname="Courier", fill=False,fontsize=font_size,align=TEXT_ALIGN_LEFT)  # more parameters
                        if(one_time):
                            return


def run(doc,EIN,file_path,file_name):
    
    i=0
    
    EIN_masked=None
    for page in doc:
        for l in page.get_text_blocks(sort=True):
            if str(l[0])[:4]==str(57.4): #00001525878906
                EIN_masked=l[4][:-1]
                break
        if(EIN_masked):
            break
    
    for page in doc:

        selector=page.get_text_blocks()[0][4]
        if(Form_8879_PE in selector):
            search_and_replace(page,{"Brian A. Lang":"UpstreamConsulting.tax"},False)
            if(not(EIN==None)):
                search_and_replace(page,{"**-***":EIN},False)
            
        elif(Form_1065 in selector):
            
            for l in page.get_text_blocks(sort=True):
                if(str(l[0])[:6]=="198.76"):

                    if("U.S. Return of Partnership Income" in l[4]):

                        if(not(EIN==None)):
                            search_and_replace(page,{EIN_masked:EIN},True)
                        page.apply_redactions(images=PDF_REDACT_IMAGE_NONE)

                        search_and_replace(page,{"**-***8651":"92-2981121"},False) 

                        search_and_replace(page,{"Brian A. Lang":"UpstreamConsulting.tax","1125 Maxwell Lane, #1124 Hoboken,NJ 07030":"6586 Atlantic Ave Num 2066, Delray Beach, FL 33446"},False)
                        search_and_replace(page,{"1125 Maxwell Lane, #1124 Hoboken,NJ 07030":"6586 Atlantic Ave Num 2066, Delray Beach, FL 33446"},False)
                        search_and_replace(page,{"46-5698651":"92-2981121"},False) 
                        search_and_replace(page,{"(646)580-2430":"(646)580-2430"},False)  

        i+=1
        page.apply_redactions(images=PDF_REDACT_IMAGE_NONE)
            

        
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
        
        for file in filenames:
            doc2=open(file)
            # mark watermark on all pages
            for page in doc2:
                if(watermark_bool.get()):
                    page.insert_image(page.bound(),stream=BytesIO(base64.b64decode(base64_bytes_watermark)), overlay=False)   

                page.apply_redactions(images=PDF_REDACT_IMAGE_NONE)
            doc2.saveIncr()
        
        showinfo(
            title='Selected File',
            message="Modified the file successfuly"
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
).place(x=330, y=300)

# run the application
root.mainloop()


