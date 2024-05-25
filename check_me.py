import fitz

doc = fitz.Document("f8804.pdf")

# its work when we update first-time
widgets = doc[1].widgets()
i=1
for field in widgets:
    if field.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
        if(i==2):
            field.field_value = True
            field.update() 
        i+=1

# # now after we set to read-only the checked symbol that we check before is gone.
# for page in doc:
#     widgets = page.widgets()
#     for field in widgets:
#         if field.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
#             field.field_flags |= fitz.PDF_FIELD_IS_READ_ONLY
#         field.update()  

doc.save("f8804_to_use.pdf")