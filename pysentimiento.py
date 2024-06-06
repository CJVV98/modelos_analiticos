# -*- coding: utf-8 -*-
"""PySentimiento.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CQYGjCk59VYN_OSefBwoTl5HzDtNhTzi
"""

!pip install nltk
!pip install unidecode
!pip install spacy
!pip install tabula-py pandas
!pip install pysentimiento

!python -m spacy download es_core_news_sm

import nltk
import pandas as pa;
import numpy as np;
import re;
import tabula
import spacy
from unidecode import unidecode
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pysentimiento import create_analyzer
from nltk import SnowballStemmer
from pysentimiento.preprocessing import preprocess_tweet
import numpy as np
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt

from sklearn import svm, datasets
from google.colab import drive
drive.mount('/content/drive')

"""#Conversión de PDF a Excel

#Procesamiento de texto
"""



dwn_url_pruebas='/content/drive/MyDrive/ProyectoGrado/Maestria/Evaluaciones/dataset_test__.csv'
df_pruebas = pa.read_csv(dwn_url_pruebas, encoding='utf-8',header=None, sep=';');
df_pruebas.columns=["Comentario","Emocion"]
df_test = pa.DataFrame(columns=['Comentario', 'Emocion'])
for index, row in df_pruebas.iterrows():
    comment = str(row['Comentario']);
    comment_proc = preprocess_tweet(comment);
    df_test = pa.concat([df_test, pa.DataFrame([{'Comentario': comment_proc, 'Emocion': row['Emocion']}])], ignore_index=True)
df_test_1=df_test

"""# Pysentimiento"""

emotion_analyzer = create_analyzer(task="emotion", lang="es")
# Obtener predicciones del modelo
predictions_ = emotion_analyzer.predict(df_test_1["Comentario"])
predictions = [max(output.probas, key=output.probas.get) for output in predictions_]

#Mapa de emociones de pysentimiento
map_emotion = {"anger": 0, "sadness": 1, "joy": 3, "fear": 4, "surprise": 5, "others":6, "disgust":6}
#Mapa de emociones del DataSet
map_emotion_data =  {'scared': 4, 'mad': 0, 'sad': 1, 'surprise':5,'joyful':3, 'trust':6,'others':6}

predictions_test = [map_emotion[prediction] for prediction in predictions]
value_prediction=[map_emotion_data[prediction] for prediction in df_test_1["Emocion"]]

predictions_=[map_emotion_data[prediccion] for prediccion in df_test_1["Emocion"]]

# Calcular precision, recall y f1-score
precision = precision_score(value_prediction, predictions_test, average='weighted')

print(f'Precisión: {precision}')
recall = recall_score(value_prediction, predictions_test, average='weighted')
f1 = f1_score(value_prediction, predictions_test, average='weighted')

print(f'Recall: {recall}')
print(f'F1-Score: {f1}')

from sklearn.metrics import confusion_matrix,ConfusionMatrixDisplay
cm = confusion_matrix(value_prediction, predictions_test)
print(cm)

disp_emotion = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['mad', 'sad', 'joyful', 'surprise','scared','others'])
disp_emotion.plot(cmap=plt.cm.Blues)
plt.title('Matriz de Confusión para la Emoción')
plt.xlabel('Predicción')
plt.ylabel('Etiqueta Verdadera')
plt.show()
