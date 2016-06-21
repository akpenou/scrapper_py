import re
import urllib.request
import urllib.parse
import bs4 as BeautifulSoup
import sys

class Leboncoin():
    def __init__(self, query):
        self.query = query

    def __get_price(self, product):
        try: # teste le float
            price = float(product.section.h3.contents[0].strip().replace('\xa0', '')[:-1].replace(',', '.').replace(' ',''))
        except Exception as e:
            print('line 15', e, ' | You may change research')
            exit()
        return price

    def get_first_item(self):
        """
            None -> tuple(str * 3)
        """
        params = urllib.parse.urlencode({'o':'1', 'q':self.query})
        url = 'https://www.leboncoin.fr/annonces/offres/ile_de_france/?{:s}'.format(params) # Cree l'url de recherche en get
        html = urllib.request.urlopen(url)
        if url != html.geturl():
            return None
        soup = BeautifulSoup.BeautifulSoup(html, 'html5lib')
        try:
            products = soup.section.find_all('a', 'list_item clearfix trackable')
        except Exception as e:
            print('Nothing found on leboncoin')
            return None
        for product in products: # recupere les differentes informations de chaque produit
            if str(product.section.h2).strip() == 'None':
                continue
            name = product.section.h2.contents[0].strip()
            price = self.__get_price(product)
            link = 'http:' + product['href']
            return (name, price, link)
        return None

class Ldlc():
    def __init__(self, query):
        self.query = query

    def __get_price(self, l_price):
        s_price = str(l_price[0]).strip()[:-1]
        if len(l_price) > 1:
            s_price += '.' + l_price[1].contents[0]
        try: # teste le float
            price = float(s_price.replace('\xa0', ''))
        except Exception as e:
            print('line 50', e, ' | You may change research')
            exit()
        return price

    def get_first_item(self):
        """
            None -> tuple(str * 3)
        """
        params = urllib.parse.quote(self.query)
        url = 'http://www.ldlc.com/navigation/{:s}/'.format(params) # Cree l'url de recherche en get
        html = urllib.request.urlopen(url)
        if url != html.geturl(): # Verfie qu'on arrive bien sur le lien de notre recherche et non une page d'article
            return None
        soup = BeautifulSoup.BeautifulSoup(html, 'html5lib')
        try:
            table = soup.find('table')
            products = table.find_all('tr', class_ = re.compile('e\d+'))
        except Exception as e:
            print('Nothing found on ldlc')
            return None
        for product in products: # recupere les differentes informations de chaque produit
            name = product.find('a',class_='nom').attrs['title']
            price = self.__get_price(product.find('span', class_ = 'price').contents)
            link = product.find('a',class_='nom').attrs['href']
            return (name, price, link)
        return None

class Ebay():
    def __init__(self, query):
        self.query = query

    def __get_name(self, content):
        for block in content:
            if type(block) == BeautifulSoup.element.NavigableString:
                return block.strip()

    def __get_price(self, content):
        if type(content) == BeautifulSoup.element.NavigableString:
            try: # test le float
                return float(content.replace(',', '.').strip())
            except Exception as e:
                print('line 87', e, ' | You may change research')
                exit()
        else :
            content = content.contents
            for item in content:
                if type(content) == BeautifulSoup.element.NavigableString:
                    try: # Test le float
                        return float(content.replace(',', '.').strip())
                    except Exception as e:
                        print('line 96', e, ' | You may change research')
                        exit()

    def get_first_item(self):
        param = urllib.parse.quote(self.query)
        url = 'http://www.ebay.fr/' # Connection sur ebay.fr
        html = urllib.request.urlopen(url)
        soup = BeautifulSoup.BeautifulSoup(html, 'html5lib')
        form = soup.find('form').find_all('input') # Cherche le formulaire
        query = {i.get('name'): i.get('value') for i in form if i and i.has_attr('name')} # filtre les champs
        query['_nkw'] = param
        params = urllib.parse.urlencode(query)
        html = urllib.request.urlopen('http://www.ebay.fr/sch/i.html?{:s}'.format(params)) #renvoie le formulaire en get
        soup = BeautifulSoup.BeautifulSoup(html, 'html5lib')
        try:
            products = soup.find('div', id = 'ResultSetItems').find('ul').find_all('li', id = re.compile('^item')) # cherche les produits
        except Exception as e:
            print('Nothing found on ebay')
            return None
        for product in products: # recupere les differentes informations de chaque produit
            link = product.find(class_ = 'lvtitle').find('a').get('href')
            name = self.__get_name(product.find(class_ = 'lvtitle').find('a').contents)
            price = self.__get_price(product.find(class_ = 'lvprice prc').find('span').contents[0])
            return (name, price, link)

def get_param():
    if len(sys.argv) != 2:
        print('Usage : python3 {:s} [-h] keywords'.format(sys.argv[0]))
    elif sys.argv[1] == '-h':
        print('You can do a research on Ldlc, leboncoin and ebay this program returns you the better offer')
        print('In order to do a multiple keywords search you need to write them with double quote, ex : "word word word" ')
        print('-h : help')
    elif not re.compile('^[\w ]+').match(sys.argv[1]):
        print('Error : Your research contain forbbiden characters you only can use letters, numbers and spaces')
    else:
        return (sys.argv[1])
    exit()

def main():
    query = get_param()
    find = []
    query_lbc = Leboncoin(query)
    query_ldlc = Ldlc(query)
    query_ebay = Ebay(query)
    find.append(query_ebay.get_first_item())
    find.append(query_lbc.get_first_item())
    find.append(query_ldlc.get_first_item())
    find = [item for item in find if item]
    if len(find) < 1:
        print('Nothing found for {:s}'.format(query))
        exit()
    find.sort(key = lambda x : x[1])
    print('{:s} : {:s} {:f} {:s}'.format(query, find[0][0], find[0][1], find[0][2]))

if __name__ == '__main__':
    main()
