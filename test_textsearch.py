import re

import PyPDF2

search_term = "phúc thẩm"

reader = PyPDF2.PdfFileReader("/home/loctx/Downloads/document.pdf")

num_pages = reader.getNumPages()


print(f"{num_pages=}")
for i in range(num_pages):
    page = reader.getPage(i)
    text = page.extractText()
    search_result = re.search(search_term, text)
    print(search_result)
    print("#" * 20)
