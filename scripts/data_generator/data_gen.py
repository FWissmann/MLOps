#!/usr/bin/env python
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#get_ipython().run_line_magic('matplotlib', 'inline')


# In[30]:


columns =  ['Zeit', 'Vollständiger Name', 'Betroffene/r Nutzer/in', 'Ereigniskontext', 'Komponente', 'Ereignisname', 'Beschreibung', 'Herkunft', 'IP-Adresse']
sim_data = pd.DataFrame(columns = columns)
sim_data.head()


# ### Festlegung: Anzahl von Zeilen: Testdatei ca. 800 Zeilen > 1000 Zeilen generieren 

# ## 1) Zeit und Datum: Format 18. April 2023, 14:24:03

# In[31]:


import random
from datetime import datetime, timedelta


# In[37]:


anzahl_zeilen = 1000
start = datetime(2023, 4, 1)
end = datetime.now()
# Spalte 'Zeit' leer setzen:
sim_data['Zeit'] = ''


# In[38]:


for i in range(anzahl_zeilen):
    zufaellige_dauer = random.randint(1, int((end - start).total_seconds() // 60))
    zeitstempel = start + timedelta(minutes=zufaellige_dauer)
    sim_data.loc[i, 'Zeit'] = zeitstempel

sim_data.head()


# In[39]:


# Format korrigieren:

# Umwandlung in Datetime-Format
sim_data['Zeit'] = pd.to_datetime(sim_data['Zeit'])

# Formatierung der Spalte 'Zeit'
sim_data['Zeit'] = sim_data['Zeit'].dt.strftime('%d. %B %Y, %H:%M:%S')

sim_data.head()


# In[41]:


# Sortieren nach aufsteigenden Zeitstempel
sim_data = sim_data.sort_values(by='Zeit')

# Index zurücksetzen
sim_data = sim_data.reset_index(drop=True)

sim_data.head(1000)


# In[42]:


# überprüfen, ob nur 1000 Zeilen erstellen worden sind:
#sim_data.info()

# 1000 Zeilen OK - Enddatum zwar nicht der 19.05.2023, aber irrelevant für die simulierten Daten. 


# ## 2) Vollständiger Name: alphanumerische Zeichenkette

# In[61]:


import string


# In[62]:


# Festlegen des Zufallssaatwerts für Reproduzierbarkeit auf 101
random.seed(101) 


# In[63]:


# Methode zum Erstellen von Zeichenketten erstellen
#def generate_random_string():
    # random Buchstabenkette erstellen 
 #   random_letters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    # random Zahlen erstellen 
  #  random_string = random.choice(strings)
    
   # random_stringletter = f'{random_string}{random_letters}'
    #return random_stringletter


# In[89]:

def generate_random_string():
    # Zufällige Buchstabenkette erstellen
    random_letters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    # Zufällige Zahl erstellen
    random_number = random.choice([str(num) for num in range(10)])

    random_string_letter = f'{random_number}{random_letters}'
    return random_string_letter

# Methode in einer Schleife aufrufen
# 30 eindeutige, verschiedene Zeichenketten a 5 Zeichen erstellen lassen
# 30 Verschiedene 30, da in einem Kurs ca. 30 Studierende eingeschrieben sind (Annahme)

array_stringletters = []

for _ in range(30):
    zeichenkette = generate_random_string()
    array_stringletters.append(zeichenkette)


# In[90]:


# array mit 30 verschiedenen Zeichenketten anzeigen lassen:
array_stringletters

# OK - nur nicht immer genau 5 Zeichen pro Kette > irrelevant für die simulierten Daten. 


# In[92]:


sim_data['Vollständiger Name'] = ''

zeichenkette = np.random.choice(array_stringletters, size=1000, replace=True)
sim_data['Vollständiger Name'] = zeichenkette
    
sim_data.head()


# In[93]:


# Überprüfen, ob nur 30 eindeutige Werte erstellt worden sind:
sim_data['Vollständiger Name'].nunique()

# OK!


# In[94]:


sim_data['Vollständiger Name'].unique()


# In[95]:


# Verteilung überprüfen
value_counts = sim_data['Vollständiger Name'].value_counts()
value_counts

# Versuch 1: Jeder Schüler war ca. geich oft auf der Homepage... nicht sehr repräsentativ!
# Versuch 2: zufällig verteilt - ja - ABER niemand dabei, der nur 1-2 mal RELAX besucht hat...


# In[97]:


# Versuch 3: Häufigkeitsverteilung selbst angeben, um Extreme abbilden zu können - z.B. ein Name war nur 1x auf RELAX

#sim_data['Vollständiger Name'] = ''

#haeufigkeiten = [85, 70, 67, 67, 64, 55, 50, 40, 40, 38, 35, 25, 25, 25, 25, 25, 25, 25, 21, 21, 21, 14, 13, 12, 5, 3, 3,
#                 1, 1, 1]

#zeichenkette = random.choices(array_stringletters, weights=haeufigkeiten, k=1000)
#sim_data['Vollständiger Name'] = zeichenkette
    
#sim_data.head()


# In[98]:


# Verteilung überprüfen - ok...
#value_counts = sim_data['Vollständiger Name'].value_counts()
#value_counts


# In[100]:


# Versuch 4: normalverteilte Verteilung:

anzahl_zeichenketten = len(array_stringletters)

# Erzeugung der Gewichte basierend auf einer Normalverteilung
mu = anzahl_zeichenketten / 2  # Mittelwert
sigma = anzahl_zeichenketten / 6  # Standardabweichung
gewichte = np.random.normal(mu, sigma, anzahl_zeichenketten)
gewichte = np.abs(gewichte)  # Nur positive Gewichte

# Normalisierung der Gewichte, um sicherzustellen, dass die Summe 1 ergibt
gewichte = gewichte / np.sum(gewichte)

# Verteilung der Zeichenketten auf die Zeilen des Dataframes
zeichenketten_verteilung = random.choices(array_stringletters, weights=gewichte, k=1000)
sim_data['Vollständiger Name'] = zeichenketten_verteilung

sim_data.head()


# In[101]:


# Verteilung überprüfen - bestes Ergebnis mit Normalverteilung - so lassen!
value_counts = sim_data['Vollständiger Name'].value_counts()
value_counts


# ## 3) Betroffene/r Nutzer/in: oftmals '-', manchmal vollständiger Name 

# In[103]:


# in 95% der Zeilen soll das Minus '-' eingetragen werden. In den verbleibenden Zeilen soll eine beliebige
# Zeichenkette aus dem array_stringletters herausgenommen werden.

anzahl_minus = int(anzahl_zeilen * 0.95)

# Auffüllen der Spalte mit '-'
sim_data['Betroffene/r Nutzer/in'] = '-'

# Zufällige Auswahl von Zeichenketten aus dem Array
zeichenketten_verteilung = np.random.choice(array_stringletters, size=anzahl_zeilen - anzahl_minus)

# Zufällige Auswahl der Indizes, an denen die Zeichenketten eingetragen werden sollen
indizes = np.random.choice(range(anzahl_zeilen), size=len(zeichenketten_verteilung), replace=False)

# Eintragen der ausgewählten Zeichenketten in die entsprechenden Zeilen der Spalte
sim_data.loc[indizes, 'Betroffene/r Nutzer/in'] = zeichenketten_verteilung
             

sim_data.head()


# In[104]:


# Verteilung überprüfen - OK!
value_counts_betr = sim_data['Betroffene/r Nutzer/in'].value_counts()
value_counts_betr


# ## 4) Ereigniskontext: dt. Text 

# In[111]:


ereigniskontext = ['Kurs: Statistik','Aufgabe: Lösungen', 'Datei: xxx', 'Abstimmung: xxx', 'Forum: xxx', 'Link/URL: xxx'] 

sim_data['Ereigniskontext'] = ''

ereignis = np.random.choice(ereigniskontext, size=1000, replace=True)
sim_data['Ereigniskontext'] = ereignis

# Schreibfehler korrigieren - neue Spalte wurde hinzugefügt, diese wieder löschen... 
#sim_data = sim_data.drop('Ereginiskontext', axis = 1)
    
sim_data.head()


# In[113]:


# Verteilung überprüfen - gleichmäßig verteilt - ok für sim. Daten 
value_counts_ekontext = sim_data['Ereigniskontext'].value_counts()
value_counts_ekontext


# ## 5) Komponente: ein Wort (System, Logdaten, Datei, Link/URL)

# In[117]:


components = ['Logdaten', 'Datei', 'System', 'Link/URL']


# In[118]:


# Datei: xxx > Datei; Link/URL: xxx > Link/URL, Kurs: Statistik > System 
# Rest: ('Ereigniskontext', 'Forum: xxx', 'Abstimmung: xxx'. 'Aufgabe: Lösungen') > Logdaten
# Beobachtung Bspl. Daten: Dateien, z.B. uebung5 ist manchmal unter Datei und manchmal unter System. 


# In[122]:


def fill_components(row):
    if ereigniskontext[2] in row['Ereigniskontext']:
        return components[1] # Datei
    if ereigniskontext[5] in row['Ereigniskontext']:
        return components[3] # Link/URL
    if ereigniskontext[0] in row['Ereigniskontext']:
        return components[2] # System
    else:
        return components[0] # Logdaten


# In[123]:


sim_data['Komponente'] = sim_data.apply(fill_components, axis=1)
sim_data.head()


# In[124]:


# Häufigkeitsverteilung prüfen - theoretisch: System: 189, Datei: 161, Link/URL: 156, Logdaten: 494

value_counts_components = sim_data['Komponente'].value_counts()
value_counts_components


# ## 6) Ereignisname: dt. Text 

# In[141]:


# beliebiger deutscher Text generieren und über die 1000 Zeilen verteilen:

words_dt = ['Das ist ein Beispiel',
             'Ein weiterer Satz',
             'Test Satz erfolgreich']

num_rows = 1000

sim_data['Ereignisname'] = random.choices(words_dt, k=num_rows)


sim_data.head()


# In[143]:


# Verteilung ausgeben - gleichmäßig verteilt ok
value_counts_ename = sim_data['Ereignisname'].value_counts()
value_counts_ename


# ## 7) Beschreibung: engl. Text 

# In[153]:


# Spalte auffüllen mit Standard-Sätzen: The user with id {id_name_Vollständiger Name} + Bsp. Sätze 
# Methode definieren


def fill_description(row):
    
    num_rows = 1000
    
    id_name = row['Vollständiger Name'] 
    text_user = 'The user with id'
    texts_eng = ['viewed the course with id 23946.', 'updated xxx.', 'created xxx.']
    random_selec = random.choice(texts_eng)
    
    return f"{text_user} {id_name} {random_selec}"


# In[154]:


# Methode aufrufen, um die Spalte 'Beschreibung' zu füllen:
sim_data['Beschreibung'] = sim_data.apply(fill_description, axis=1)

sim_data.head()


# ## 8) Herkunft: cli, ws, web 

# In[ ]:


# Verteilung: 5% cli, 10% ws, 85% web 


# In[155]:


total_rows = 1000
cli_rows = int(total_rows * 0.05) # 5%
ws_rows = int(total_rows * 0.10) # 10%
web_rows = total_rows - cli_rows - ws_rows # Rest mit 'web' auffüllen
 
words = ['cli'] * cli_rows + ['ws'] * ws_rows + ['web'] * web_rows

# Mischen der Liste
np.random.shuffle(words)

sim_data['Herkunft'] = words

sim_data.head()


# In[156]:


# Verteilung überprüfen 
value_counts_herkunft = sim_data['Herkunft'].value_counts()
value_counts_herkunft


# ### Hinweis: Verteilung ohne Bezug auf das Ereignis / Komponente. Kann z.B. sein, dass sich 'cli' nicht auf einen
# 
# ### Admin-Job bezieht

# ## 9) IP-Adresse: anonymisiert 

# In[ ]:


# Für jeden user soll eine IP-Adresse erstellt werden + für jede Zeile mit Herkunft == 'ws'


# In[164]:


# Methode zur Erstellung einer random-IP-Adresse:

def generate_ip_address():
    return ".".join(str(np.random.randint(0, 256)) for _ in range(4))


# In[168]:


# Methode aufrufen

# Generieren von genau einer IP-Adresse für jeden User
# Ausnahme: bei Herkunft 'ws' wird für den User eine 2. IP-Adresse erstellt

# Dictionary zum Speichern der IP-Adressen je User
user_ip_addresses = {}

ip_addresses = []

for _, row in sim_data.iterrows():
    user_id = row['Vollständiger Name']
    herkunft = row['Herkunft']
    if herkunft == 'ws':
        if user_id not in user_ip_addresses:
            ip_web = generate_ip_address()  # Erste IP-Adresse generieren
            user_ip_addresses[user_id] = ip_web

        ip_ws = generate_ip_address()   # Zweite IP-Adresse generieren

        # Prüfen, ob die zweite IP-Adresse sich von der ersten IP-Adresse unterscheidet
        while ip_ws == user_ip_addresses[user_id]:
            ip_ws = generate_ip_address()

        ip_addresses.append(ip_ws)
    else:
        if user_id not in user_ip_addresses:
            user_ip_addresses[user_id] = generate_ip_address()
        ip_addresses.append(user_ip_addresses[user_id])

        
sim_data['IP-Adresse'] = ip_addresses

sim_data.head()


# In[183]:


# Anzahl an einzigartigen IP-Adressen ausgeben lassen - theoreitsch: Anzahl an user + ws Herkunft = 30 + 100 = 130x - OK!

#count_value_counts_ip = len(sim_data['IP-Adresse'].value_counts())
#count_value_counts_ip


# In[180]:


# IP-Adressen, die nur 1x vorkommen - erwartet wird 100 einzigartige IP-Adressen, da 100x ws - OK!

#count_values_occuring_once = len(value_counts_ip[value_counts_ip == 1].index)
#count_values_occuring_once


# ## 10) sim_data ohne Zusatzspalte abspeichern als .csv Datei

# In[187]:


#sim_data.to_csv('simulated_data_noGrade.csv', index=False)


# In[192]:


# als excel Datei
#sim_data.to_excel('simulated_data_noGrade.xlsx', index=False)


# # 11) Hinzufügen einer neuen Spalte 'Abschlussnote'
# 
# Annahmen 'sehr guter Studierender' - 1,0 - 1,5
# - Mindestens 50 Einträge im df
# - Mindestens 10x etwas mit der Komponente 'Datei' gemacht
# - Herkunft 'web' und 'ws'
# 
# Annahmen 'guter Studierender' 1,6 - 2,5
# - Mindestens 35 Einträge im df
# - Mindestens 5x etwas mit der Komponente 'Datei' gemacht
# 
# Annahmen 'durchschnittlicher' Studierender 2,6 - 3,5
# - Mindestens 16 Einträge im df
# - Mindestens 1x etwas mit der Komponente 'Datei' gemacht
# 
# Annahmen 'unzureichender Studierender 3,6 - 5,0'
# - <= 15 Einträge im df 
# - Nie eine Datei geöffnet 

# In[212]:


def berechne_abschlussnote(row):
    name = row['Vollständiger Name']
    component = row['Komponente']
    herkunft = row['Herkunft']

    if sim_data['Vollständiger Name'].value_counts()[name] >= 50 and sim_data[sim_data['Vollständiger Name'] == name]['Komponente'].value_counts().get('Datei', 0) >= 10 and 'ws' in sim_data[sim_data['Vollständiger Name'] == name]['Herkunft'].tolist():
        return round(random.uniform(1.0, 1.5), 1) # eine Nachkommastelle
    
    if sim_data['Vollständiger Name'].value_counts()[name] >= 35 and sim_data[sim_data['Vollständiger Name'] == name]['Komponente'].value_counts().get('Datei', 0) >= 5:
        return round(random.uniform(1.6, 2.5), 1)
    
    if sim_data['Vollständiger Name'].value_counts()[name] >= 16 and sim_data[sim_data['Vollständiger Name'] == name]['Komponente'].value_counts().get('Datei', 0) >= 1:
        return round(random.uniform(2.6, 3.5), 1)
    
    else:
        return round(random.uniform(3.6, 5.0), 1)
    

# Neue Spalte 'Abschlussnote' hinzufügen
sim_data['Abschlussnote'] = sim_data.apply(berechne_abschlussnote, axis=1)

sim_data.head()


# In[213]:


# Diagramm Verteilung der Abschlussnote:

#plt.hist(sim_data['Abschlussnote'], bins=15, edgecolor='black')

#plt.xlabel('Abschlussnote')
#plt.ylabel('Anzahl')
#plt.title('Verteilung der Abschlussnoten')

#plt.show()


# In[229]:


# Gruppierung nach Namens-ID und Berechnung der Abschlussnote
#grouped = sim_data.groupby('Vollständiger Name').agg({'Abschlussnote': 'mean', 'Vollständiger Name': 'count'})
#grouped.rename(columns={'Vollständiger Name': 'Anzahl'}, inplace=True)

#plt.scatter(grouped['Anzahl'], grouped['Abschlussnote'], color='blue')

#plt.xlabel('Anzahl der RELAX-Einträge')
#plt.ylabel('Abschlussnote')
#plt.title('Verteilung der Abschlussnoten nach Anzahl der RELAX-Einträge')

#plt.show()


# In[222]:


filtered_datei = sim_data[sim_data['Komponente'] == 'Datei']

# Gruppierung nach ID und Berechnung der Durchschnittsnote und Anzahl der Vorkommen von 'Datei'
#grouped = filtered_datei.groupby('Vollständiger Name').agg({'Abschlussnote': 'mean', 'Komponente': 'count'})
#grouped.rename(columns={'Komponente': 'Anzahl Datei'}, inplace=True)

# Diagramm erstellen
#plt.scatter(grouped['Anzahl Datei'], grouped['Abschlussnote'], color='blue')

# Achsentitel und Diagrammtitel hinzufügen
#plt.xlabel('Anzahl der Vorkommen von "Datei" für eine ID')
#plt.ylabel('Abschlussnote')
#plt.title('Verbindung von Abschlussnote und Anzahl der Vorkommen von "Datei" nach ID')

# Diagramm anzeigen
#plt.show()


# ### 11) Neue Simulierte Daten inkl. Abschlussnote als .csv und .xlsx Datei abspeichern

# In[230]:


import os
import pandas as pd

def save_file_with_version(filename, container_path, data_frame):
# Überprüfe, ob die Datei bereits existiert
    if os.path.exists(os.path.join(container_path, filename)):
        base_name, ext = os.path.splitext(filename)
        version = 3

        while True:
            # Erzeuge den neuen Dateinamen mit fortlaufender Nummer
            new_filename = f"{base_name}_V{version}{ext}"
            new_filepath = os.path.join(container_path, new_filename)

            if not os.path.exists(new_filepath):
                break

            version += 1

        # Benenne die bestehende Datei um
        os.rename(os.path.join(container_path, filename), new_filepath)
        print(f'Die Datei {filename} wurde umbenannt zu {new_filename}.')    

    # Speichere das DataFrame als CSV-Datei unter dem ursprünglichen Dateinamen
    new_filepath = os.path.join(container_path, filename)
    data_frame.to_csv(new_filepath, index=False)
    print(f'Das DataFrame wurde als CSV-Datei unter {filename} gespeichert.')

filename = 'simulated_data_grade.csv'
container_path = '/home/jovyan/00_sim_data_output'


save_file_with_version(filename, container_path, sim_data)


#sim_data.to_csv('/home/jovyan/00_sim_data_output/simulated_data_grade.csv', index=False)


print("Ausschnitt der simulierten Daten:")
print(sim_data.head())

#fkt. nicht - modul 'container' fehlt...
import subprocess

def copy_file_to_host(src_path, dest_path):
    command = f"docker cp {src_path} data_generator:{dest_path}"
    subprocess.run(command, shell=True)

#copy_file_to_host('/home/jovyan/00_sim_data_output/simulated_data_grade.csv', '/home/aml/data_generator_output/simulated_data_grade.csv')
