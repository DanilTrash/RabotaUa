import io
import logging
import re

import PyPDF2
from PyPDF2.utils import PdfReadError
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from win32com import client

import os


pattern = r"(380[\d]{9}|050[\d]{7}|06[35678][\d]{7}|09[356789][\d]{7}|073[\d]{7})"
numbers = []


class Reader:

    def __init__(self, file):
        self.file = file


class InvalidReader(Reader):

    def __call__(self):
        print(self.file + " файл не принадлежит ни одному из форматов 'rtf', 'docx', 'doc', 'pdf'")


class PdfReader(Reader):

    def __call__(self):
        pdfFileObj = open(rf"resumes\{self.file}", 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pdfReader.getPage(0)
        pdfFileObj.close()
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        with open(rf"resumes\{self.file}", 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
        converter.close()
        fake_file_handle.close()
        numbers_in_resume = re.findall(pattern, re.sub(r'\D', '', text))
        with open('targets.txt', 'a+', encoding='utf_8_sig') as f:
            for number in numbers_in_resume:
                print(number)
                f.write(f'{number}\n')
        numbers.append(numbers_in_resume)


class WordReader(Reader):

    def __call__(self):
        self.save_as_txt()
        file_content = self.read_txt()
        numbers_in_resume = re.findall(pattern, re.sub(r'\D', '', file_content))
        with open('targets.txt', 'a+', encoding='utf_8_sig') as f:
            for number in numbers_in_resume:
                print(number)
                f.write(f'{number}\n')
        numbers.append(numbers_in_resume)
        os.remove(fr'{os.getcwd()}\resumes\{self.file[:len(self.file) - 4]}.txt')

    def save_as_txt(self):
        word = client.Dispatch("Word.Application")
        doc = word.Documents.Open(fr'{os.getcwd()}\resumes\{self.file}')
        doc.SaveAs(fr'{os.getcwd()}\resumes\{self.file[:len(self.file) - 4]}.txt', FileFormat=2)
        doc.Close()
        word.Quit()

    def read_txt(self):
        with open(fr"{os.getcwd()}\resumes\{self.file[:len(self.file) - 4]}.txt", encoding='windows-1251') as f:
            file_content = f.read()
            return file_content


def get_reader(file):
    if file.endswith('pdf'):
        return PdfReader(file)
    elif file.endswith('rtf'):
        return WordReader(file)
    elif file.endswith('docx'):
        return WordReader(file)
    elif file.endswith('doc'):
        return WordReader(file)
    else:
        return InvalidReader(file)


def client_code():
    for file in os.listdir(fr'{os.getcwd()}\resumes'):
        reader = get_reader(file)
        reader()


if __name__ == '__main__':
    client_code()
