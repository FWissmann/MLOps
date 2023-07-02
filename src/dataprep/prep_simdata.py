#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')

if 'GX_SIMDATA_FILENAME' in os.environ:
    path = os.environ['GX_SIMDATA_FILENAME']
else:
    path = '/app/01_gx/01_gx_simdata.csv'

if 'DATAPREP_SIMDATA_FILENAME' in os.environ:
    filename = os.environ['DATAPREP_SIMDATA_FILENAME']
else:
    filename = '02_dataprep_simdata.csv'
if 'DATAPREP_SIMDATA_PATH' in os.environ:
    container_path = os.environ['DATAPREP_SIMDATA_PATH']
else:
    container_path = '/app/data/02_dataprep_simdata'

# erstes CSV einlesen mit den Log-Daten
sim_data = pd.read_csv(path)

# zweites CSV einlesen mit den Abschlussnoten
#grade_data = pd.read_csv('')

sim_data.head()
#grade_data.head()

# In[3]:

sim_data.info()

# In[4]:

# eindeutige Werte der Spalten 'Voll.Name', 'Komponente', 'Herkunft' von sim_data als array ausgeben 

unique_name = sim_data['Vollständiger Name'].unique()
unique_komponente = sim_data['Komponente'].unique()
unique_herkunft = sim_data['Herkunft'].unique()

# länge der Arrays ausgeben 

length_name = len(unique_name)
length_komponente = len(unique_komponente)
length_herkunft = len(unique_herkunft)

# In[5]:


# neues df mit Auswertparameter von sim_data nach Spalte 'Vollständiger Name' erstellen
# pro eindeutiger Parameter in den Spalten 'Komponente' und 'Herkunft' soll eine neue Spalte in grouped_sim erstellen werden
# Hierzu beziehen wir uns auf die zuvor erstellen arrays mit der Anzahl der eindeutigen Werte einer Spalte unique_komponente
# Nur so viele neue Spalten werden generiert, wie es eindeutige Werte pro Spalte hat
# Der Name der neuen Spalte entspricht 'Anzahl' + Name eindeutiger Wert 

sim_data['Herkunft'] = sim_data['Herkunft'].astype(str)
sim_data['Komponente'] = sim_data['Komponente'].astype(str)

# Neues gruppiertes DataFrame erstellen und Index zurücksetzen
grouped_data = sim_data.groupby('Vollständiger Name').agg({
    'Komponente': [(f'Anzahl {name}', lambda x, name=name: (x == name).sum()) for name in unique_komponente],
    'Herkunft': [(f'Anzahl {name}', lambda x, name=name: (x == name).sum()) for name in unique_herkunft],
    'IP-Adresse': 'nunique'
}).reset_index()

grouped_data.head()


# In[6]:


grouped_data.info()

# i.O. - 30 Zeilen - es wurden auch 30 Studierende im data_gen simuliert


# In[7]:


from datetime import datetime
import locale

# im Datengenerator leider englische Namen verwendet... kann auskommentiert werden:
locale.setlocale(locale.LC_TIME, "en_US") # englische Monatsbezeichnung
'en_US"'

# Anzahl der Vorkommen eines Users im ursprünglichen sim_data
user_counts = sim_data['Vollständiger Name'].value_counts().rename('Anzahl_log_all')

# nur das Datum extrahieren
# teilweise gemisches Datenformat... d.h. Formatangabe rausnehmen #, format='%d. %B %Y, %H:%M:%S'
sim_data['Zeit'] = pd.to_datetime(sim_data['Zeit']).dt.date

# Definiere den Start- und Endzeitpunkt für den ersten Zeitraum
# Start: erster Log-Eintrag
start_date = sim_data['Zeit'].min()

# 16 Wochen später als der erste Eintrag (Dauer eines Semesters)
end_date = start_date + pd.DateOffset(weeks=20)
# Beobachtung: teilweise Einträge nach 16 Wochen - Enddatum = Letzter Log-Eintrag der Logdatei
# end_date = sim_data['Zeit'].max()

# Definiere den Zeitraumabstand
period_offset = pd.DateOffset(weeks=2)

# Liste zur Speicherung der Zeitraumgrenzen
period_boundaries = []

# Generiere die Zeitraumgrenzen mit einem Abstand von zwei Wochen
# pro Zeitraumgrenze wird es eine neue Spalte in dem DataFrame log_counts geben
# Wenn keine Werte für die Zeiträume z.B. bei 16 Wochen vorhanden sind, werden die Spalten mit dem Mittelwert der vorherigen
# Zeitraumsgrenzen aufgefüllt

current_date = start_date
while current_date <= end_date:
    period_boundaries.append(current_date)
    current_date += period_offset

# Erstelle das DataFrame log_counts mit den Zeitraumspalten
log_counts = pd.DataFrame()
log_counts['Vollständiger Name'] = user_counts.index.unique() # Eindeutige Namen im Index verwenden
log_counts['Anzahl_log_all'] = user_counts.reindex(log_counts['Vollständiger Name']).values # Werte entsprechend den eindeutigen Namen im Index reindexieren

# Überprüfung des letzten Datums in sim_data
last_date = sim_data['Zeit'].max()

# Auffüllen der fehlenden Zeiträume basierend auf dem letzten Datum
for i in range(len(period_boundaries)):
    period_start = period_boundaries[i]
    if i == len(period_boundaries) - 1:
        # Letzter Zeitraum, fiktiven Wert verwenden - Mittelwert der vorherigen Zeiträume
        log_counts[f'Anzahl_log_f{i+1}'] = np.mean(log_counts[[f'Anzahl_log_f{j}' for j in range(1, i+1)]], axis=1).astype(int)
    else:
        period_end = period_boundaries[i + 1]
        
        if last_date >= period_end:
            # Datum liegt im Zeitraum, Log-Einträge zählen
            log_entries_by_period = sim_data[(sim_data['Zeit'] >= period_start) & (sim_data['Zeit'] < period_end)].groupby('Vollständiger Name').count()
            log_counts[f'Anzahl_log_f{i+1}'] = log_entries_by_period['Zeit'].reindex(log_counts['Vollständiger Name'], fill_value=0).values
        else:
            # Datum liegt außerhalb des Zeitraums, mit Mittelwert auffüllen als Ganzzahl
            log_counts[f'Anzahl_log_f{i+1}'] = np.mean(log_counts[[f'Anzahl_log_f{j}' for j in range(1, i+1)]], axis=1).astype(int)

log_counts.head()


# In[8]:


# Anzahl log-Einträge mit sim_data mergen nach 'Vollständiger Name'
grouped_data_sim = grouped_data.merge(log_counts, on='Vollständiger Name')

grouped_data_sim.head()


# In[9]:


# Abschlussnote aus dem zweiten df grade_data_log dem jeweiligen User zuordnen

#grouped_data_grade = pd.merge(grouped_data_log, grade_data, on='Vollständiger Name', how='left')

#grouped_data_grade.head()


# In[10]:


grouped_data_sim.to_csv(filename, index=False)
