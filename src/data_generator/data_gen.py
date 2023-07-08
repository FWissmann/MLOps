#!/usr/bin/env python
# coding: utf-8

# Imports
import pandas as pd
import numpy as np
import os
import subprocess
import random
import string
from datetime import datetime, timedelta

# Variablen

# Check if environment variable is set otherwise use default value
# Output variables
if 'SIMDATA_FILENAME' in os.environ:
    SIMDATA_FILENAME = os.environ['SIMDATA_FILENAME']
else:
    SIMDATA_FILENAME = '00_simdata.csv'
if 'SIMDATA_FOLDERNAME' in os.environ:
    SIMDATA_FOLDERNAME = os.environ['SIMDATA_FOLDERNAME']
else:
    SIMDATA_FOLDERNAME = '/app/data/00_simdata'

columns =  ['Zeit', 'Vollständiger Name', 'Betroffene/r Nutzer/in', 'Ereigniskontext', 'Komponente', 'Ereignisname', 'Beschreibung', 'Herkunft', 'IP-Adresse']
sim_data = pd.DataFrame(columns = columns)

# ### Festlegung: Anzahl von Zeilen: Testdatei ca. 800 Zeilen > 1000 Zeilen generieren 

# ## 1) Zeit und Datum: Format 18. April 2023, 14:24:03

anzahl_zeilen = 1000
start = datetime(2023, 4, 1)
end = datetime.now()
# Spalte 'Zeit' leer setzen:
sim_data['Zeit'] = ''

for i in range(anzahl_zeilen):
    zufaellige_dauer = random.randint(1, int((end - start).total_seconds() // 60))
    zeitstempel = start + timedelta(minutes=zufaellige_dauer)
    sim_data.loc[i, 'Zeit'] = zeitstempel

# Format korrigieren:

# Umwandlung in Datetime-Format
sim_data['Zeit'] = pd.to_datetime(sim_data['Zeit'])

# Formatierung der Spalte 'Zeit'
sim_data['Zeit'] = sim_data['Zeit'].dt.strftime('%d. %B %Y, %H:%M:%S')

# Sortieren nach aufsteigenden Zeitstempel
sim_data = sim_data.sort_values(by='Zeit')

# Index zurücksetzen
sim_data = sim_data.reset_index(drop=True)

# Festlegen des Zufallssaatwerts für Reproduzierbarkeit auf 101
random.seed(101) 

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


sim_data['Vollständiger Name'] = ''

zeichenkette = np.random.choice(array_stringletters, size=1000, replace=True)
sim_data['Vollständiger Name'] = zeichenkette
    
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

# ## 3) Betroffene/r Nutzer/in: oftmals '-', manchmal vollständiger Name 

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
            
# ## 4) Ereigniskontext: dt. Text 

ereigniskontext = ['Kurs: Statistik','Aufgabe: Lösungen', 'Datei: xxx', 'Abstimmung: xxx', 'Forum: xxx', 'Link/URL: xxx'] 

sim_data['Ereigniskontext'] = ''

ereignis = np.random.choice(ereigniskontext, size=1000, replace=True)
sim_data['Ereigniskontext'] = ereignis

# Schreibfehler korrigieren - neue Spalte wurde hinzugefügt, diese wieder löschen... 
#sim_data = sim_data.drop('Ereginiskontext', axis = 1)
    


# ## 5) Komponente: ein Wort (System, Logdaten, Datei, Link/URL)

components = ['Logdaten', 'Datei', 'System', 'Link/URL']

# Datei: xxx > Datei; Link/URL: xxx > Link/URL, Kurs: Statistik > System 
# Rest: ('Ereigniskontext', 'Forum: xxx', 'Abstimmung: xxx'. 'Aufgabe: Lösungen') > Logdaten
# Beobachtung Bspl. Daten: Dateien, z.B. uebung5 ist manchmal unter Datei und manchmal unter System. 

def fill_components(row):
    if ereigniskontext[2] in row['Ereigniskontext']:
        return components[1] # Datei
    if ereigniskontext[5] in row['Ereigniskontext']:
        return components[3] # Link/URL
    if ereigniskontext[0] in row['Ereigniskontext']:
        return components[2] # System
    else:
        return components[0] # Logdaten

sim_data['Komponente'] = sim_data.apply(fill_components, axis=1)

# Häufigkeitsverteilung prüfen - theoretisch: System: 189, Datei: 161, Link/URL: 156, Logdaten: 494

# ## 6) Ereignisname: dt. Text 

# beliebiger deutscher Text generieren und über die 1000 Zeilen verteilen:

words_dt = ['Das ist ein Beispiel',
             'Ein weiterer Satz',
             'Test Satz erfolgreich']

num_rows = 1000

sim_data['Ereignisname'] = random.choices(words_dt, k=num_rows)

# ## 7) Beschreibung: engl. Text 

# Spalte auffüllen mit Standard-Sätzen: The user with id {id_name_Vollständiger Name} + Bsp. Sätze 
# Methode definieren

def fill_description(row):
    
    num_rows = 1000
    
    id_name = row['Vollständiger Name'] 
    text_user = 'The user with id'
    texts_eng = ['viewed the course with id 23946.', 'updated xxx.', 'created xxx.']
    random_selec = random.choice(texts_eng)
    
    return f"{text_user} {id_name} {random_selec}"

# Methode aufrufen, um die Spalte 'Beschreibung' zu füllen:
sim_data['Beschreibung'] = sim_data.apply(fill_description, axis=1)

# ## 8) Herkunft: cli, ws, web 
# Verteilung: 5% cli, 10% ws, 85% web 

total_rows = 1000
cli_rows = int(total_rows * 0.05) # 5%
ws_rows = int(total_rows * 0.10) # 10%
web_rows = total_rows - cli_rows - ws_rows # Rest mit 'web' auffüllen
 
words = ['cli'] * cli_rows + ['ws'] * ws_rows + ['web'] * web_rows

# Mischen der Liste
np.random.shuffle(words)

sim_data['Herkunft'] = words

# ### Hinweis: Verteilung ohne Bezug auf das Ereignis / Komponente. Kann z.B. sein, dass sich 'cli' nicht auf einen
# ### Admin-Job bezieht

# ## 9) IP-Adresse: anonymisiert 
# Für jeden user soll eine IP-Adresse erstellt werden + für jede Zeile mit Herkunft == 'ws'

# Methode zur Erstellung einer random-IP-Adresse:

def generate_ip_address():
    return ".".join(str(np.random.randint(0, 256)) for _ in range(4))

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

# ## 10) sim_data ohne Zusatzspalte abspeichern als .csv Datei
#sim_data.to_csv('simulated_data_noGrade.csv', index=False)

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

# ### 11) Neue Simulierte Daten inkl. Abschlussnote als .csv und .xlsx Datei abspeichern
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

save_file_with_version(SIMDATA_FILENAME, SIMDATA_FOLDERNAME, sim_data)

print("Ausschnitt der simulierten Daten:")
print(sim_data.head())