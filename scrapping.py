import requests
import pandas as pd

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# URL de la page de la liste de produits
url = 'https://www.rueducommerce.fr/rayon/telephonie-92/samsung-galaxy-7546/occasions'
socle = urlparse(url).scheme + "://" + urlparse(url).hostname

# Récupération de tous les liens de produits sur la page
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
product_links = [a.a.get('href') for a in soup.find_all('p', class_='item__caracs')] 

next_link = soup.select_one('link[rel="next"]')
while next_link:
    next_url = urljoin(socle, next_link.get('href'))
    next_response = requests.get(next_url)
    next_soup = BeautifulSoup(next_response.content, 'html.parser')
    next_product_links = [a.a.get('href') for a in next_soup.find_all('p', class_='item__caracs')]
    product_links += next_product_links
    next_link = next_soup.select_one('link[rel="next"]')

# Récupération de tous les liens des produits sur la page
soup_catalog = BeautifulSoup(requests.get(url).content, 'html.parser')
product_links = list(set(
    [a.a.get('href') for a in soup_catalog.find_all('p', class_='item__caracs')]
))

# Récupération des fiches marchands et le nom des vendeurs
marchands_links  = []
marchands_names = []

for link in product_links:
    soup_product = BeautifulSoup(requests.get(socle + link).content, 'html.parser')
    marchand_name = soup_product.find_all('a', class_="produit__vendeur-nom")[0].text
    if marchand_name not in marchands_names: # On récupère seulement les valeurs uniques
        marchands_links.append(
            soup_product.find_all('a', class_="produit__vendeur-nom")[0].get("href")
        )
        marchands_names.append(marchand_name)

# Récupération des SIREN
def get_siren(txt):
    if "TVA" in txt.text.strip():
        return txt.text.strip()[-9:]
    else:
        return txt.text.strip().split(" ")[-1][:9]

marchands_SIREN = []

for marchand_link in marchands_links:
    if marchand_link != "/marchand/rue-du-commerce":
        soup_siren = BeautifulSoup(requests.get(socle + marchand_link).content, 'html.parser')
        marchands_SIREN.append(
            get_siren(soup_siren.find_all('p', class_="legal")[0])
        )
    else:
        marchands_SIREN.append(
            422797720
        )

print(marchands_names, marchands_SIREN)
# Exporter le fichier csv avec les infos
#pd.DataFrame({'vendor_name': marchands_names, 'siren': marchands_SIREN}).to_csv('vendors.csv', index=False)

# pas pris en comtpe :https://www.rueducommerce.fr/p-samsung-galaxy-z-flip3-5g-sm-f711b-samsung-2012168170-27453.html?articleOfferId=63573044
