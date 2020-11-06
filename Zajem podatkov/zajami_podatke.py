import requests
import re
import os
import csv

# Url glavne strani
url_vsi_psi = 'https://www.akc.org/expert-advice/dog-breeds/2020-popular-breeds-2019/'
# Shranjujem v mapo:
mapa = 'psi'
# Ime datoteke, v kateri je glavna stran
datoteka_vsi_psi = 'vsi_psi.html'
# Ime CSV datoteke, v katero shranjujem podatke
csv_datoteka = 'psi.csv'



# Shrani vsebino spetne strani v html datoteko
# ---------------------------------------------

def url_v_niz(url):
    ''' Sprejme niz (url), vrne vsebino spletne strani kot niz '''
    try:
        odziv = requests.get(url)                   # Če je odziv 200, ne potrebuje exceptiona
    except requests.exceptions.ConnectionError:
        print('Napaka pri povezovanju do:', url)    # Če pride do napake pri povezovanju
        return None
    
    if odziv.status_code == requests.codes.ok:      # Če ni bilo errorja
        return odziv.text                           # Vrne vsebino spletne strani
    else:
        print('Napaka pri prenosu strani:', url)


def niz_v_file(niz, mapa, datoteka):
    ''' niz pretvori v datoteko in so shrani v mapo, če že obstaja, naredi novo'''
    os.makedirs(mapa, exist_ok=True)      
    path = os.path.join(mapa, datoteka)    # Ustvari path do datoteke v katero shranjujemo
    with open(path, 'w', encoding='utf-8') as dat:
        dat.write(niz)                     # V datoteko vpiš niz
    return None


def shrani_stran(url, mapa, datoteka):
    ''' Vrne vsebino datoteke kot niz '''
    niz = url_v_niz(url)
    niz_v_file(niz, mapa, datoteka)
    return None


# Začnemo pridobivati podatke iz html datoteka za obdelavo.
# ----------------------------------------------------------

def preberi_file(mapa, datoteka):
    path = os.path.join(mapa, datoteka)
    with open(path, 'r', encoding='utf-8') as dat:
        return dat.read()


def ustvari_seznam_psov(vsebina):
    """ 
    Funkcija iz niza izlušči podakte o imenu pasme in naslovu 
    spletne strani in naredi seznam html datotek vseh pasem. 
    """
    vzorec = (
        r'<td .*?-hyperlink="'
        r'(?P<url>https://www.akc.org/dog-breeds/.*?/)'
        r'">.*?'
        r'rel="noopener">(?P<pasma>.*?)</a></td>\n'
        r'.*?}">(?P<mesto>\d+)</td>'
    )

    seznam_datotek = list()
    for zadetek in re.finditer(vzorec, vsebina):
        # Ustvarim seznam imen datotek pasem, na katerega se bom kasneje sklicovala 
        url = zadetek.group('url')
        ime_datoteke = zadetek.group('pasma').lower().replace(' ', '-') + '.html'
        seznam_datotek.append(ime_datoteke)
        # Shranim še spletne strani vsake pasme v posamezno datoteko
        shrani_stran(url, mapa, ime_datoteke)
    return seznam_datotek

#################################################################################################################################################
# VSI VZORCI

vzorec_psa = re.compile(
    r'<meta name="og:breed" content="(?P<pasma>.*?)" />'
)

vzorec_psa_mesto = (
    r'<Attribute name="akc_breed_popularity">AKC Breed Popularity: Ranks (?P<mesto>\d*) of 196</Attribute>'
)

vzorec_psa_visina_po_spolu = (
    r'<Attribute name="height">Height: (?P<visina_moski_dol>\d*\.?\d?)-(?P<visina_moski_gor>\d*\.?\d?) inches \(male\), (?P<visina_zenske_dol>\d*\.?\d?)-(?P<visina_zenske_gor>\d*\.?\d?) inches \(female\)</Attribute>'
)   

vzorec_psa_visina = (
    r'<Attribute name="height">Height: (?P<visina_dol>\d*)-(?P<visina_gor>\d*) inches</Attribute>'
)

vzorec_psa_teza_po_spolu = (
    r'<Attribute name="weight">Weight: (?P<teza_moski_dol>\d*\.?\d?)-(?P<teza_moski_gor>\d*\.?\d?) pounds \(male\), (?P<teza_zenske_dol>\d*\.?\d?)-(?P<teza_zenske_gor>\d*\.?\d?) pounds \(female\)</Attribute>'
)

vzorec_psa_teza = (
    r'<Attribute name="weight">Weight: (?P<teza_dol>\d*\.?\d?)-(?P<teza_gor>\d*\.?\d?) pounds</Attribute>'
)

vzorec_psa_starost = (
    r'<Attribute name="life_expectancy">Life Expectancy: (?P<starost_dol>\d*)-(?P<starost_gor>\d*) years</Attribute>'
)
    
vzorec_psa_skupina = (
    r'<Attribute name="group">Group: (?P<skupina>.*?) Group</Attribute>'
)

vzorec_psa_nega = re.compile(
    r'<h4 class="bar-graph__title">Grooming Frequency</h4>'
    r'.*?'                
    r'<div class="bar-graph__text">(?P<nega>.*?)</div>',
    re.DOTALL    
)

vzorec_psa_ucenje = re.compile(
    r'<h4 class="bar-graph__title">Trainability</h4>'
    r'.*?'                
    r'<div class="bar-graph__text">(?P<hitrost_ucenja>.*?)</div>',
    re.DOTALL
)

vzorec_psa_temperament = re.compile(
    r'<h4 class="bar-graph__title">Temperament/Demeanor</h4>'
    r'.*?'                
    r'<div class="bar-graph__text">(?P<temperament>.*?)</div>',
    re.DOTALL
)

vzorec_psa_opis = re.compile(
    r'<h3 class="mb0">GENERAL APPEARANCE</h3>\n'
    r'\W*<div class="breed-standard__content-wrap"><p>(?P<opis>.*?)</p>',
    
    re.DOTALL
)
###############################################################################################################################################


# Naredim slovar, ki ga bom pretvorila v tabelo v csv datoteki
# -----------------------------------------------------------------------
def ustvari_seznam_lastnosti(vsebina):
    seznam_lastnosti = list()
    
    for ime_datoteke in ustvari_seznam_psov(vsebina):
        vsebina_psa = preberi_file(mapa, ime_datoteke)
        
        pasma = re.search(vzorec_psa, vsebina_psa)
        slovar = pasma.groupdict()
        
        # Dodamo uvrščeno mesto
        mesto = re.search(vzorec_psa_mesto, vsebina_psa)
        slovar['mesto'] = mesto.group('mesto')
        
        # Dodamo skupino v katero pripada
        skupina = re.search(vzorec_psa_skupina, vsebina_psa)
        slovar['skupina'] = skupina.group('skupina')
        
        # Dodamo povprečno življensko dobo
        starost = re.search(vzorec_psa_starost, vsebina_psa)
        if starost:
            slovar['min_starost'] = int(float(starost.group('starost_dol')))
            slovar['max_starost'] = int(float(starost.group('starost_gor')))
        else:
            slovar['min_starost'] = None
            slovar['max_starost'] = None
        
        # Dodamo povprečno višino pasme
        visina_1 = re.search(vzorec_psa_visina, vsebina_psa)
        visina_2 = re.search(vzorec_psa_visina_po_spolu, vsebina_psa)
        if visina_1 is not None:
            slovar['max_visina'] = int(float(visina_1.group('visina_gor')))
            slovar['min_visina'] = int(float(visina_1.group('visina_dol')))
        elif visina_2 is not None:
            slovar['min_visina'] = (int(float(visina_2.group('visina_moski_dol'))) + int(float(visina_2.group('visina_zenske_dol')))) / 2
            slovar['max_visina'] = (int(float(visina_2.group('visina_moski_gor'))) + int(float(visina_2.group('visina_zenske_gor')))) / 2
        else:
            slovar['min_visina'] = None
            slovar['max_visina'] = None
        
        # Dodamo povprečno težo pasme
        teza_1 = re.search(vzorec_psa_teza, vsebina_psa)
        teza_2 = re.search(vzorec_psa_teza_po_spolu, vsebina_psa)
        if teza_1 is not None:
            slovar['min_teza'] = int(float(teza_1.group('teza_dol')))
            slovar['max_teza'] = int(float(teza_1.group('teza_gor')))
        elif teza_2 is not None:
            slovar['min_teza'] = (int(float(teza_2.group('teza_moski_dol'))) + int(float(teza_2.group('teza_zenske_dol')))) / 2
            slovar['max_teza'] = (int(float(teza_2.group('teza_moski_gor'))) + int(float(teza_2.group('teza_zenske_gor')))) / 2
        else:
            slovar['min_teza'] = None
            slovar['max_teza'] = None

        # Dodamo potrebe po negovanju
        nega = re.search(vzorec_psa_nega, vsebina_psa)
        if nega is not None:
            slovar['nega'] = nega.group('nega')
        else:
            slovar['nega'] = None

        # Dodamo sposobnost učenja 
        hitrost_ucenja = re.search(vzorec_psa_ucenje, vsebina_psa)
        if hitrost_ucenja is not None:
            slovar['hitrost_ucenja'] = hitrost_ucenja.group('hitrost_ucenja')
        else:
            slovar['hitrost_ucenja'] = None
        
        # Dodamo karakter / temperament pasme
        temperament = re.search(vzorec_psa_temperament, vsebina_psa)
        if temperament is not None:
            slovar['temperament'] = temperament.group('temperament')
        else:
            slovar['temperament'] = None

        # Dodamo opis psa
        opis = re.search(vzorec_psa_opis, vsebina_psa)
        if opis is not None:
            # Odstranimo prelome vrstic in html oznake za konec vrstice
            izboljsan_opis = opis.group('opis').replace('<br />', ' ').replace('\n', ' ')
            slovar['opis'] = izboljsan_opis
        else:
            slovar['opis'] = None

        
        # Dodajmo slovar psa v seznam lastnosti vseh pasem
        seznam_lastnosti.append(slovar)
    seznam_lastnosti.sort(key=lambda pasma: pasma['mesto'])
        
    return seznam_lastnosti


# -------------------------------------------------------------------------
# Podatke shranim v csv datoteko
# ------------------------------

def naredi_csv(imena_lastnosti, seznam_slovarjev, mapa, datoteka):
    """
    Funkcija v csv datoteko shrani vrednosti iz slovarja,
    shrani v vrstice v istem vrstnem redu kot v parametru 'imena_lastnosti'.
    """

    os.makedirs(mapa, exist_ok=True)
    path = os.path.join(mapa, datoteka)

    with open(path, 'w', encoding='utf-8') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_lastnosti)
        writer.writeheader()
        for slovar in seznam_slovarjev:
            writer.writerow(slovar)
    return None


def __main__(redownload=True, reparse=True):
    # Ustvarimo glavno datoteko, ki vsebuje povezave do vseh ostalih strani.
    shrani_stran(url_vsi_psi, mapa, datoteka_vsi_psi)

    # Shranimo vse strani pasem
    ustvari_seznam_psov(preberi_file(mapa, datoteka_vsi_psi))

    # Podatke datotek shranimo v seznam slovarjev in pretvorimo v csv datoteko
    naredi_csv(
        ['pasma', 'mesto', 'skupina', 'min_starost', 'max_starost', 'min_visina', 'max_visina', 'min_teza', 'max_teza', 'nega', 'hitrost_ucenja', 'temperament', 'opis'], 
        ustvari_seznam_lastnosti(preberi_file(mapa, datoteka_vsi_psi)), 
        mapa, 
        csv_datoteka
        )

if __name__ == '__main__':
    main()

