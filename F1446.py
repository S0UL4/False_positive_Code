import fitz
from pdf_var_of_form8804 import form8804_base64encoded
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import os
from io import BytesIO
import base64
from PIL import Image, ImageTk
import time
from icon_8804 import base64_splitter_image
from pdf_var_of_form8805 import form8805_base64encoded
import tempfile
from multi_column import column_boxes

#GUI Params
root = tk.Tk()
root.title('Section 1446 v7')
root.resizable(False, False)
root.geometry('800x640')
try:
    api = Api('pathoq3SDkBoC72bO.f5c653233829869b8f070833d7dd6919dd9f4e4edae5b6104596ee7f4135d36c')
    table = api.table('appXXcYFouev63m3D', 'InvestmentEntities')
    records = table.all()
except Exception as e:
    print(e)
    pass

image = Image.open(BytesIO(base64.b64decode(base64_splitter_image)))
image = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=image)
image_label.pack()
label_text = tk.Label(root, text="Please upload the same input as K-1 program\n PS: Unmasked 8879 must be present\n This Program needs the Input without Watermarks",font=("Courier 15 bold"))
label_text.pack()
EIN=None
#Backend params
Form_8879_PE="8879-PE"
Form_1065="1065"
form_k1="Schedule K-1 \n(Form 1065)"
count_foreign=0
form8804_var=[]

# Function to return the EIN of the Partnership
def return_EIN(file_name):
    for r in records:
        try:
            #print(r)
            if(file_name in r['fields']['IDClient']):
                return r['fields']['EIN']
        except:
            continue



#Function to modify a specific text field in a pdf page
def search_and_replace(page,to_search_and_replace,one_time,sizey=8,sizex1=0,sizex2=0):
    # split_words=[]
    # number_of_words=to_search_and_replace
    #print(to_search_and_replace.keys())
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
                            text_lenght = fitz.get_text_length(line, fontname="helvetica-bold", fontsize=sizey)
                            rect_x2 = xl + text_lenght   # needs margin
                            rect_y2 = yl + font_size+3   # needs margin
                            Bbox_text=fitz.Rect(xl, yl+sizex1 + (font_size ) * i, rect_x2, rect_y2 +sizex2+ (font_size ) * i)
                            annot=page.add_redact_annot(Bbox_text, line, fontname="helvetica-bold", fill=False,fontsize=font_size,align=fitz.TEXT_ALIGN_LEFT)  # more parameters
                        if(one_time):
                            return

def check_indiv(page):

    check_ind=0
    Indiv=True
    for l in page.get_text_blocks(sort=True):
        if(check_ind):
            #print('----')
            if("Indiv" in l[4]):
                Indiv=True
            elif("Partnership" in l[4]):
                Indiv=False
            
            check_ind=0
            break
            #print(Indiv)
            #if("Individual")
        if("What type of entity is this partner" in l[4]):
            check_ind=1
            continue

    return Indiv

# function to get the name of the K_1 before splitting it from the rest of pages.
def run(doc,pdf_stream,page,file_name,file,save_final):
    global EIN
    global count_foreign
    global form8804_var
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
    # Indiv=check_indiv(page)
    # doc_k1=fitz.open(file)
    #print(page.get_text_blocks(sort=True))
    list_of_varibales=[]
    check_indiv_var=None
    

    for l in page.get_text_blocks(sort=True):
        if str(l[0])[:4]=="57.4":
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
    
    #print(list_of_varibales)

    if(EIN==None or len(EIN)==0):
        EIN=list_of_varibales[0][:-1]
    
    #print(list_of_varibales)
 
    TIN_number=list_of_varibales[2].split("\n")[0][-4:]

    temp_partner_name=list_of_varibales[3][:-1].split(" ")
    
    if("GNUS" in TIN_number):
        slice=-1
        if(Indiv):
            slice=-1
        else:
            slice=1
        for name in temp_partner_name[::slice]:
            partner_name+=name[0].upper()+name[1:].lower()+' '

        partner_name+='' #########################################
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
    else:
        full_name_k1=name_of_file+'_'+year+'_k-1_'+partner_name_final+TIN_number

    partnerhsip_name_and_address=list_of_varibales[1].split("\n")[:-1]
    address_partnership="".join([ch+"\n" for ch in partnerhsip_name_and_address[1:]])
    address_partner="".join([ch for ch in list_of_varibales[3:][1:]])
    country=list_of_varibales[-1].split(" ")[-1][:-1]
    
    

    if(country.isnumeric() or len(country)>2):
        country=list_of_varibales[-1].split(" ")[-2]
    
    
    if('GNUS' in TIN_number):
        count_foreign+=1
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


        search_and_replace(doc[0],{"1A":partner_name_final},False,sizey=8,sizex1=-2,sizex2=-2)
        search_and_replace(doc[0],{"4C":country},False)
        search_and_replace(doc[0],{"Y1":year},True,sizey=9,sizex1=0,sizex2=0)
        search_and_replace(doc[0],{"2B":"None"},False,sizey=8,sizex1=-2,sizex2=-2)
        search_and_replace(doc[0],{"5A":partnerhsip_name_final},False,sizey=8,sizex1=-2,sizex2=-2)
        search_and_replace(doc[0],{"BEIN":EIN},False,sizey=8,sizex1=-2,sizex2=-2)
        search_and_replace(doc[0],{"C1":address_partner},False)
        search_and_replace(doc[0],{"C2":address_partnership},False)
        search_and_replace(doc[0],{"3Type":check_indiv_var},False,sizey=8,sizex1=0,sizex2=-1)
        search_and_replace(doc[0],{"6A":"SAME"},False,sizey=8,sizex1=-3,sizex2=-3)
        doc[0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    #print(partner_name_final)

    if(len(partnerhsip_name_and_address)>=4):
        partnerhsip_long_name=partnerhsip_name_and_address[0]+','+partnerhsip_name_and_address[1]
        address_partnership=partnerhsip_name_and_address[2]
        City_partnerhsip=partnerhsip_name_and_address[3]

    else:
        partnerhsip_long_name=partnerhsip_name_and_address[0] 
        address_partnership=partnerhsip_name_and_address[1]
        City_partnerhsip=partnerhsip_name_and_address[2]

    if(save_final):
        form8804_var.clear()
        form8804_var.append(partnerhsip_long_name)
        form8804_var.append(City_partnerhsip)
        form8804_var.append(year)
        form8804_var.append(address_partnership)
        

    return (full_name_k1,year,TIN_number)


def select_file():
    global EIN
    global count_foreign
    global form8804_var
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
        try:
            for file in filenames:
                doc=None
                pdf_stream_8804=BytesIO(base64.b64decode(form8804_base64encoded))
                pdf_stream_8805=BytesIO(base64.b64decode(form8805_base64encoded))

                file_name=file.split('/')[-1].split('_')[0]
                big_k1=fitz.open(file)
                file_path=file[:len(file)-file[::-1].find('/')]
                count_foreign=0
                try:
                    EIN=return_EIN(file_name)
                except Exception as e:
                    print(e)
                    EIN=''

                doc_generate_8804 = fitz.open(filetype="pdf")
                doc_generate_8805 = fitz.open(filetype="pdf")
                doc_combined=fitz.open()
                to_save_partner=True
                found_EIN=False
                for page in big_k1:
                    selector=page.get_text_blocks()[0][4]

                    if(Form_8879_PE in selector and not(found_EIN)):
                        bboxes = column_boxes(page, footer_margin=50, no_image_text=True)
                        
                        for rect in bboxes[:10]: #IRect(36, 108, 481, 120)
                            ch=page.get_text(clip=rect, sort=True)
                            for EIN_try in ch.split():
                                if('-'  in EIN_try and len(EIN_try)==10) and (EIN_try[:2].isnumeric() and EIN_try[3:].isnumeric()):
                                    EIN=EIN_try
                                    found_EIN=True
                                    break
                    
                    if(form_k1 in selector):
                        doc_8805 = fitz.open(stream=pdf_stream_8805, filetype="pdf")
                        
                        name_of_file,year,typeP=run(doc_8805,pdf_stream_8805,page,file_name,file_path,to_save_partner)
                        to_save_partner=False
                        #time.sleep(10000)
                        # name_of_file,year,typeP=run(doc,pdf_stream,page,file_name,file_path,True)
                        # name_of_file=run(doc,pdf_stream,page,file_name,file_path)[0]
                        # year=
                        if("GNUS" in typeP):
                            doc_generate_8805.insert_pdf(doc_8805,0,0)
                        
                doc_8804 = fitz.open(stream=pdf_stream_8804, filetype="pdf")
                             
                #print()
                #print(form8804_var)

                search_and_replace(doc_8804[0],{"5A":form8804_var[0]},False,sizey=8,sizex1=-2,sizex2=-3)
                search_and_replace(doc_8804[0],{"X1-C":form8804_var[1]},False)
                search_and_replace(doc_8804[0],{"1Y":year[2:]},True,sizey=10,sizex1=-2,sizex2=-2)
                search_and_replace(doc_8804[0],{"2B":"None"},False)
                # search_and_replace(doc[0],{"5A":partnerhsip_name_and_address[0].split(",")[0]},False)
                search_and_replace(doc_8804[0],{"BEIN":EIN},False)
                search_and_replace(doc_8804[0],{"C1":form8804_var[3]},False,sizey=8,sizex1=5)
                search_and_replace(doc_8804[0],{"BUSEIN":''},False)
                search_and_replace(doc_8804[0],{"2A":'SAME'},False)
                search_and_replace(doc_8804[0],{"CNS":''},False)
                search_and_replace(doc_8804[0],{"DCT":''},False)
                search_and_replace(doc_8804[0],{"3A":str(count_foreign)},False)
                search_and_replace(doc_8804[0],{"3B":str(count_foreign)},False)
                search_and_replace(doc_8804[1],{"Enrolled Agent":"Enrolled Agent"},False)
                search_and_replace(doc_8804[1],{"D1":""},False)
                search_and_replace(doc_8804[1],{"Brian Alan Lang EA":"Brian Alan Lang EA"},False)
                search_and_replace(doc_8804[1],{"Brian Alan Lang":"Brian Alan Lang EA"},False)
                search_and_replace(doc_8804[1],{"1125 Maxwell Lane, Hoboken, New Jersey 07030":"1125 Maxwell Lane, Hoboken, New Jersey 07030"},False)
                search_and_replace(doc_8804[1],{"P01641043":"P01641043"},False)
                search_and_replace(doc_8804[1],{"46-5698651":"46-5698651"},False)
                search_and_replace(doc_8804[1],{"646.580-2430":"646.580-2430"},False)
                # search_and_replace(doc[0],{"3Type":check_indiv_var},False)
                # search_and_replace(doc[0],{"6A":"SAME"},False)
                doc_8804[0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                doc_8804[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)


                widgets0 = doc_8804[0].widgets()
                for field in widgets0:
                    if(field.field_type == fitz.PDF_WIDGET_TYPE_TEXT):
                        field.field_value=""
                        field.update() 
                                                
                widgets1 = doc_8804[1].widgets()
                i=1
                for field in widgets1:
                    if(field.field_type == fitz.PDF_WIDGET_TYPE_TEXT):
                        field.field_value=""
                        field.update() 
                        
                    if(field.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX):
                        #print(field)
                        if(i==2):
                            field.field_value=True
                            field.update() 
                        i+=1
                        
                        
                # 2nd alternative        
                # with tempfile.TemporaryDirectory() as tmpdir:
                #     file_8804_temp = os.path.join(tmpdir, "_8804_temp.pdf")
                #     print(file_8804_temp)
                #     doc_8804.save(file_8804_temp, encryption=0)
                #     doc_generate_8804=fitz.open(file_8804_temp,filetype="pdf")  


                # doc_8804.save(file_path+file_name+'_'+str(year)+'_8804_6666.pdf', encryption=0)
                # doc_generate_8804.insert_pdf(doc_8804)
                
                # doc_combined.insert_pdf(doc_generate_8804)
                doc_8804.insert_pdf(doc_generate_8805)                
                doc_8804.save(file_path+file_name+'_'+str(year)+'_1446.pdf', encryption=0)

        except Exception as e:
            if(count_foreign==0):
                print(e)
                print(fitz.TOOLS.mupdf_warnings())
                showinfo(
                title='Error',
                message="No Foreign Partners for "+str(file_name))
                #return
            showinfo(
                title='Error',
                message=str(e)
            )
        if(count_foreign!=0):
            showinfo(
                title='Selected File',
                message="Form 1446 Generated Successfully"
            )
        else:
            showinfo(
                title='Error',
                message="No Foreign Partners for "+str(file_name)
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

open_button.pack(expand=True)


# run the application
root.mainloop()


