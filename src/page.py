import utils

class Page:
    id = ""
    url = ""
    title = ""

    def __init__(self, title) -> None:
        self.title = title
        self.add_page()

    def add_page(self):
        print(self.title)
    
    def get_page(self):
        print ("Ciao" + self.title)
