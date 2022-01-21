import pandas as pd
from collections.abc import Iterator


dataframe = pd.read_csv('https://docs.google.com/spreadsheets/d/1rRSGmvwnPjrV5QhcX7X-BI8SL7U7RM5znb7y9a81EgI/'
                        'export?format=csv&id=1rRSGmvwnPjrV5QhcX7X-BI8SL7U7RM5znb7y9a81EgI&gid=128190461')


class Data(Iterator):
    TOKEN = "2062101487:AAHFs7AgtRB4nQJFD-JUgCVnupJ73OngdjM"

    def __init__(self, argument):
        self._collection = dataframe[argument].dropna().tolist()
        self.position = 0

    def __next__(self):
        try:
            value = self._collection[self.position]
            self.position += 1
            return value
        except IndexError:
            raise StopIteration
