from fitz import * 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo, askyesnocancel
import os
from io import BytesIO
import base64
from PIL import Image, ImageTk
from icon_k1 import base64_splitter_image
from multi_column import column_boxes
import time

#GUI Params
root = tk.Tk()
root.title('K-1 Unmask, Split and Rename v13')
root.resizable(False, False)
root.geometry('800x670')
style = ttk.Style()
style.configure("Large.TCheckbutton", font=("Arial", 13))

# boolean var to reverse the names
reverse_name=tk.BooleanVar()

# boolean var to spell out the names 
spell_out_names=tk.BooleanVar()


#function to check the revere_name var
def reverse_name_change():
    if(reverse_name.get()):
        tk.messagebox.showinfo(title='Info',
            message="Reverse name selected")
    else:
        tk.messagebox.showinfo(title='Info',
            message="Reverse name unselected")  
        
#function to spell out full name of the fund 
def full_name_fund_partnership():
    if(spell_out_names.get()):
        tk.messagebox.showinfo(title='Info',
            message="Spell out full names selected")
    else:
        tk.messagebox.showinfo(title='Info',
            message="Spell out full names unselected")  


# variable that holds the backgroudn image of the K1 program                    
image = Image.open(BytesIO(base64.b64decode(base64_splitter_image)))
image = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=image)
image_label.pack()

# button for selection the reverse name functionnality
ttk.Checkbutton(root, style="Large.TCheckbutton",
                text='Reverse Name',
                command=reverse_name_change,
                variable=reverse_name,
                onvalue=True,
                offvalue=False).place(x=350, y=450)

# button for selection the spell out names functionnality
ttk.Checkbutton(root, style="Large.TCheckbutton",
                text='Spell out names',
                command=full_name_fund_partnership,
                variable=spell_out_names,
                onvalue=True,
                offvalue=False).place(x=350, y=480)

# label text for information
label_text = tk.Label(root, text="The K-1 Program will retrieve the EINs from Form 8879-PE \n so ensure the EIN is unmasked",font=("Arial 15 bold"))
label_text.place(x=145, y=535)
EIN=None
#Backend params
Form_8879_PE="8879-PE"
Form_1065="1065"
form_k1="Schedule K-1 \n(Form 1065)"

#Function to modify a specific text field in a pdf page
def search_and_replace(page,to_search_and_replace,one_time):

    for b in page.get_text("dict")["blocks"]:
        for l in b["lines"]:
            for s in l['spans']:
                xl=fitz.Rect(s['bbox']).tl.x
                yl=fitz.Rect(s['bbox']).tl.y
                xr=fitz.Rect(s['bbox']).br.x
                yr=fitz.Rect(s['bbox']).br.y     
                font_size=yr-yl  
                for to_search in list(to_search_and_replace.keys()):
                    if(to_search in s['text']):
                        #print(to_search_and_replace[to_search])
                        # number_of_words=to_search_and_replace[to_search].count("\n")
                        split_words=to_search_and_replace[to_search].split("\n")[:-1]
                        if(len(split_words)==0):
                            split_words=to_search_and_replace[to_search].split("\n")
                        #print(split_words)
                        for i,line in enumerate(split_words):
                        #print(to_search)
                            text_lenght = fitz.get_text_length(line, fontname="Courier", fontsize=10)
                            rect_x2 = xl + text_lenght + 2  # needs margin
                            rect_y2 = yl + font_size + 2  # needs margin
                            Bbox_text=fitz.Rect(xl, yl + (font_size + 2) * i, rect_x2, rect_y2 + (font_size + 2) * i)
                            annot=page.add_redact_annot(Bbox_text, line, fontname="Courier", fill=False,fontsize=font_size,align=fitz.TEXT_ALIGN_LEFT)  # more parameters
                        if(one_time):
                            return


# function to get the name of the K_1 before splitting it from the rest of pages.
def get_name_of_k1(page,file_name):
    global EIN
    found_partnership_var=0
    found_partner_name_id=0
    partner_name=''
    partner_name_final=''
    partnership_name=''
    TIN_number=''
    name_of_file=file_name
    year=""
    check_name=False
    TIN_picked=False
    found_EIN=True
    check_TIN=False
    TIN_picked_id=0
    check_ind=0
    Indiv=True
    #print(page.get_text_blocks(sort=True))
    list_of_varibales=[]
    check_indiv_var=None

    for l in page.get_text_blocks(sort=True):
        if str(l[0])[:4]=="57.4": #00001525878906
            list_of_varibales.append(l[4])
        try:
            if l[0]==173.0 or str(l[0])[:4]=='78.19':
                check_indiv_var=l[4]
                if("Indiv" in check_indiv_var):
                    Indiv=True
                elif("Partnership" in check_indiv_var):
                    Indiv=False
                else:
                    Indiv=True
        except Exception as e:
            print(str(e))
            pass
        if("For calendar year" in l[4]):
            year=l[4][l[4].find('202'):l[4].find('202')+4]

    TIN_number=list_of_varibales[2].split("\n")[0][-4:]
    

    if(len(list_of_varibales[0])>=9 and found_EIN):
        if(not(EIN==None)):
            search_and_replace(page,{list_of_varibales[0][:-1]:EIN},True)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        found_EIN=False

    temp_partner_name=list_of_varibales[3][:-1].split(" ")
    
    if("GNUS" in TIN_number):
        slice=-1
        if(Indiv):
            slice=-1
        else:
            slice=1
        for name in temp_partner_name[::slice]:
            partner_name+=name[0].upper()+name[1:].lower()+'_'

        partner_name+='Foreign'
    else:
        found=False
        #print(temp_partner_name)
        
        for name in temp_partner_name[1*int(Indiv):]:
            #print(name.upper())
            if(len(name)==1 or ("LLC" in name) or name.upper()=='A' or name.upper()=='THE' or name.upper()=='AN' or name.upper()=='AND'):
                continue

            partner_name=name[:4]
            found=True
            break
            

        if(not(found)):
            partner_name=temp_partner_name[0]

    if(not("GNUS" in TIN_number)):
        partner_name=partner_name.lower()

    partnership_name=list_of_varibales[1][:-1]
    partner_name_final=partner_name
    
    if("@" in partner_name):
        try:
            partner_name_final=partner_name.split('\n')[0]
            #partner_name_final=partner_name.split('\n')[1]
            partner_email=partner_name.split('\n')[1]
        except Exception as e:
            print(str(e))

    partner_name_final=partner_name_final.replace('\n','')  
    partnership_name=partnership_name.replace('\n','')

    if("GNUS" in TIN_number):
        full_name_k1=name_of_file+'_'+year+'_k-1_'+partner_name_final
        if(reverse_name.get()):
            full_name_k1=partner_name_final+'_'+year+'_k-1_'+name_of_file 
    else:
        full_name_k1=name_of_file+'_'+year+'_k-1_'+partner_name_final+TIN_number
        if(reverse_name.get()):
            full_name_k1=partner_name_final+TIN_number+'_'+year+'_k-1_'+name_of_file 
    
    partnerhsip_name_and_address=list_of_varibales[1].split("\n")[:-1]

    new_partner_name_temp=list_of_varibales[3:][0]
    
    new_partner_name=''
    partnerhsip_name_final=""
    for xname in new_partner_name_temp.split(" "):
        new_partner_name+=xname[0].upper()+xname[1:].lower()+' ' 

    partner_name_final=new_partner_name

    #print(partner_name_final.split())

    if("," in partnerhsip_name_and_address[0]):
        partnerhsip_name_final=partnerhsip_name_and_address[0].split(",")[0]
    elif("A Series" in partnerhsip_name_and_address[0]):
        partnerhsip_name_final=partnerhsip_name_and_address[0].split("A Series")[0] #partnerhsip_name_final='A Series '+partnerhsip_name_and_address[0].split("A Series")[1]
    else:
        partnerhsip_name_final=partnerhsip_name_and_address[0]
    
    rm_space_ps=0
    rm_space_p=0
   
    for i in partnerhsip_name_final[::-1]:
        if(i==' ' or i=='\n'):
            rm_space_ps+=1
        else:
            break
   
    for i in partner_name_final[::-1]:
        if(i==' ' or i=='\n'):
            rm_space_p+=1
        else:
            break

    if(spell_out_names.get()):
        full_name_k1=partnerhsip_name_final[:len(partnerhsip_name_final)-rm_space_ps]+'_'+year+'_k-1_'+partner_name_final[:len(partner_name_final)-rm_space_p]
        if(reverse_name.get()):
            full_name_k1=partner_name_final[:len(partner_name_final)-rm_space_p]+'_'+year+'_k-1_'+partnerhsip_name_final[:len(partnerhsip_name_final)-rm_space_ps]
        # print(partner_name_final)
        # print(partnerhsip_name_final)

    return full_name_k1

#Verifiy that static text exists in the list
def verify_additional_k1_data(page):
    try:
        for data in page.get_text_blocks(sort=True):
            if("Additional Information From Schedule K-1" in data[4]):
                return True
        return False
    except Exception as e:
        print(e)
        return False

# verify if to pick an upcoming page or not and how much page to pick ?
def pick_next_pages(doc,page):
    try:
        number=0
        for p in doc.pages(page.number+1):
            try:
                if("Form 1065" in p.get_text_blocks()[0][4]):
                    return number
                elif(not(verify_additional_k1_data(p))):
                    return number                    
                else:
                    number+=1
            except:
                pass
    except Exception as e:
        print(e)
        return 0       
    

def run(doc,file_path,file_name):
    try:
        global EIN
        found_EIN=False
        proceed_or_not=False
        
        for page in doc:
            # print(page.get_text_blocks())
            selector=page.get_text_blocks()[0][4]


            if(Form_8879_PE in selector):
                search_and_replace(page,{"Brian A. Lang":"UpstreamConsulting.tax"},False)
                bboxes = column_boxes(page, footer_margin=50, no_image_text=True)
                for rect in bboxes[:10]: #IRect(36, 108, 481, 120)
                    ch=page.get_text(clip=rect, sort=True)
                    for EIN_try in ch.split():
                        if('-'  in EIN_try and len(EIN_try)==10) and (EIN_try[:2].isnumeric() and EIN_try[3:].isnumeric()):
                            EIN=EIN_try
                            found_EIN=True
                            break

                if(not(EIN) and proceed_or_not==False):
                    proceed_or_not=askyesnocancel(
                                    message="EIN on 8879 is Masked for %s\nDo you want to continue ?"%(file_name),
                                    title="K-1 Unmask, Split and Rename v13"
                                )
                    
                    if(not(proceed_or_not)):
                        showinfo(
                            title='Info',
                            message="Split aborted for "+str(file_name)
                        )
                        return 0
                
                    
            
            elif(Form_1065 in selector):
                search_and_replace(page,{"Brian A. Lang":"UpstreamConsulting.tax","1125 Maxwell Lane, #1124 Hoboken,NJ 07030":"6586 Atlantic Ave Num 2066, Delray Beach, FL 33446"},False)
                search_and_replace(page,{"1125 Maxwell Lane, #1124 Hoboken,NJ 07030":"6586 Atlantic Ave Num 2066, Delray Beach, FL 33446"},False)
                search_and_replace(page,{"46-5698651":"92-2981121"},False) 
                search_and_replace(page,{"(646)580-2430":"(646)580-2430"},False)  

            ###if(form_k1 in selector):
            # search_and_replace(page,"**-***",EIN)
            page.apply_redactions(images=PDF_REDACT_IMAGE_NONE)


            if(form_k1 in selector):

                doc_k1 = fitz.open()
                custom_name=get_name_of_k1(page,file_name)

                number= pick_next_pages(doc,page) if not(pick_next_pages(doc,page)==None) else 0
      
                doc_k1.insert_pdf(doc,page.number,page.number+number)
                #print(file_path)
                file_path_k1=file_path+custom_name+'.pdf'
                doc_k1.save(file_path_k1, incremental=False, encryption=0)

        return 1        
    except Exception as e:
        showinfo(
            title='Error',
            message="Please Report the error to the Technical Support of WiseWend Tech : \ncontact@wisewend.tech\n"+str(e)
        )



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
    
    #print(current_path)
    
    if(len(filenames)!=0):
        
        # for windows compilation via pyinstaller
        # for file in filenames:
        #    path_to_save_windows=""
        #    for c in file:
        #        if(c=="/"):
        #           path_to_save_windows+="\\"
        #         else:
        #             path_to_save_windows+=c
        #     doc = open(path_to_save_windows)
        #     #print(path_to_save_windows)
        #     file_name=path_to_save_windows.split('\\')[-1].split('_')[0]
        #     try:
        #         EIN=return_EIN(file_name)
        #     except Exception as e:
        #         EIN=''
        #     run(doc,EIN,file,file_name)
        err=1
        for file in filenames:
            doc = open(file)
            file_name=file.split('/')[-1].split('_')[0]
            file=file[:len(file)-file[::-1].find('/')]
            err=run(doc,file,file_name)
            EIN=''
        if(not(err)):
            pass
        else:          
            showinfo(
                title='Selected File',
                message="Generated the files successfuly"
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
)

open_button.place(x=350, y=620)


# run the application
root.mainloop()


