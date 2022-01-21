import io
import os
import re

import PyPDF2
import pandas as pd
from PyPDF2.utils import PdfReadError
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from win32com import client

interviews = pd.read_csv(
    'https://docs.google.com/spreadsheets/d/1GbK5YrhV7uyT3wIapgMTU-NW6GHimMA6lG8IuDB0b6Q/'
    'export?format=csv&id=1GbK5YrhV7uyT3wIapgMTU-NW6GHimMA6lG8IuDB0b6Q&gid=420698778',
    header=None,
    usecols=[6, 11],
    dtype={6: str, 11: str})  # 6 - номера, 11 - комментарий

applicants = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/1GbK5YrhV7uyT3wIapgMTU-NW6GHimMA6lG8IuDB0b6Q/\
    export?format=csv&id=1GbK5YrhV7uyT3wIapgMTU-NW6GHimMA6lG8IuDB0b6Q&gid=545937916",
    header=None,
    usecols=[5, 10],
    dtype={5: str, 10: str})  # 5 - номера, 10 - комментарий

resumes = [file for file in os.listdir(fr'{os.getcwd()}\resumes')]

pattern = r"(380[\d]{9}|050[\d]{7}|06[35678][\d]{7}|09[356789][\d]{7}|073[\d]{7})"

match_in_interviews = []
match_in_applicants = []
cant_extract_number = []


def read_word(resume):
    word = client.Dispatch("Word.Application")
    doc = word.Documents.Open(fr'{os.getcwd()}\resumes\{resume}')
    doc.SaveAs(fr'{os.getcwd()}\resumes\{resume[:len(resume) - 4]}.txt', FileFormat=2)
    doc.Close()
    word.Quit()
    with open(fr"{os.getcwd()}\resumes\{resume[:len(resume) - 4]}.txt", encoding='windows-1251') as f:
        numbers_in_resume = re.findall(pattern, re.sub(r'\D', '', f.read()))
        print(resume, numbers_in_resume)
        if not numbers_in_resume:
            cant_extract_number.append(resume)
            os.replace(f"resumes/{resume}", f"без номера/{resume}")
        search_matches(numbers_in_resume, resume)
    os.remove(fr'{os.getcwd()}\resumes\{resume[:len(resume) - 4]}.txt')


def read_pdf(resume):
    pdfFileObj = open(rf"resumes\{resume}", 'rb')
    try:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    except PdfReadError:
        return
    pdfReader.getPage(0)
    pdfFileObj.close()
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(rf"resumes\{resume}", 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    numbers_in_resume = re.findall(pattern, re.sub(r'\D', '', text)
    print(resume, numbers_in_resume)
    if not numbers_in_resume:
        cant_extract_number.append(resume)
        os.replace(f"resumes/{resume}", f"без номера/{resume}")
    search_matches(numbers_in_resume, resume)


def search_matches(numbers_in_resume, resume):
    remove = []
    for xtrctd_number in numbers_in_resume:
        if len(xtrctd_number) == 12:
            xtrctd_number = xtrctd_number[1:]
        for i, number in enumerate(interviews[6]):
            if type(number) == float:
                continue
            number = str(number)[1:]
            if str(number)[:-10:-1] == xtrctd_number[:-10:-1]:
                match = resume, number, interviews[11][i]
                print(interviews[11][i], ' - комментарий в собеседованиях')
                match_in_interviews.append(match)
                remove.append(resume)
        for i, number in enumerate(applicants[5]):
            if type(number) == float:
                continue
            number = str(number)[1:]
            if str(number)[:-10:-1] == xtrctd_number[:-10:-1]:
                match = resume, number, applicants[10][i]
                print(applicants[10][i], ' - комментарий в ПД')
                match_in_applicants.append(match)
                remove.append(resume)
    for file in set(remove):
        os.replace(f"resumes/{file}", f"совпадения/{file}")


def main():
    for resume in resumes:
        os.system("@echo off \ntaskkill /im WINWORD.EXE /f")
        if re.findall(r'\w+$', resume)[0] == 'rtf':
            read_word(resume)
        elif re.findall(r'\w+$', resume)[0] == 'docx':
            read_word(resume)
        elif re.findall(r'\w+$', resume)[0] == 'doc':
            read_word(resume)
        elif re.findall(r'\w+$', resume)[0] == 'pdf':
            read_pdf(resume)
        else:
            print(resume, " файл не принадлежит ни одному из форматов 'rtf', 'docx', 'doc', 'pdf'")
            continue

    if match_in_interviews:
        print(f'\nCовпадения в собеседованиях:')
        for i in match_in_interviews:
            print(i)
    else:
        print('\nCовпадений в собеседованиях не найдено')

    if match_in_applicants:
        print(f'\nCовпадения в ПД:')
        for i in match_in_applicants:
            print(i)
    else:
        print('\nCовпадений в ПД не найдено')

    if cant_extract_number:
        print('\nНомер не удалось извлечь из документов:')
        for resume in cant_extract_number:
            print(resume)
    else:
        print('\nВсе файлы обработаны успешно')


if __name__ == '__main__':
    main()
