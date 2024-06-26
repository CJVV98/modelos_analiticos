# -*- coding: utf-8 -*-
"""NaivesBayes.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DV1B909tgI60DV6QA6I1NYm8Rekuia_S
"""

!pip install nltk
!pip install unidecode
!pip install spacy
!pip install tabula-py
!pip install pandas==2.2

!python -m spacy download es_core_news_sm

import nltk
import pandas as pa;
import numpy as np;
import re;
from unidecode import unidecode
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
from nltk import SnowballStemmer
import tabula

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import nltk

nltk.download('vader_lexicon')

from google.colab import drive
drive.mount('/content/drive')

"""#PROCESAMIENTO DE TEXTO"""

#Descargar tokenizador y stopwords
nltk.download('punkt')
nltk.download('stopwords')

def proc_info(word):
  #Eliminar caracteres especiales
  letters_comment = re.sub("[^A-Za-záéíóúñÁÉÍÓÚÑ]", " ", word)
  #Eliminar palabras repetidas más de dos veces
  repeat_words = re.sub("(.)\\1{2,}", "\\1\\1", letters_comment)
  #Si vienen con guion intermedio
  union_words = re.sub("([A-Za-z]+)-([A-Za-z]+)", "\\1\\2", repeat_words);
  #Conversión de mayúsculas a minúsculas
  lower_words=union_words.lower();
  return lower_words;

def proc_tokenize(lower_words):
  #Tokenizar el comentario por palabras
  tokens = word_tokenize(lower_words)
  tokens_words=[x for x in tokens if len(x) > 1]
  return tokens_words;

# Eliminar StopWords de los comentarios
def delete_stop_word(tokens_words):
  stop = set(stopwords.words('spanish'))
  # Guardar en la lista las palabras que no son stopwords
  stop.discard("no");
  stop.discard("es");
  stop_tokens = [w for w in tokens_words if not w in stop]
  stop_token_ = [word.strip() for word in stop_tokens]
  return stop_token_;

#Lematización de textos
nlp = spacy.load('es_core_news_sm')

#Definir lema para cada palabra
def lemmatize_words(word):
  doc = nlp(word)
  lemmas = [tok.lemma_.lower() for tok in doc]
  return lemmas

def proc_lemmatize_and_stemming(stop_tokens):
  spanishstemmer=SnowballStemmer('spanish')
  #Se lematiza por palabra
  lemmas = [lemmatize_words(word) for word in stop_tokens]
  #flattened_list = [item[0] for item in lemmas]
  stems = [' '.join([item[0] for item in lemmas])];
  #Se hace stemming para definir las raices de las palabras
  #stems = [' '.join([spanishstemmer.stem(lemma) for lemma in flattened_list])]
  comment_proc=str(stems);
  comment_proc = re.sub("[^A-Za-záéíóúñÁÉÍÓÚÑ]", " ", comment_proc)
  return comment_proc

#Remover emojis
def remove_emojis(text):
    # Utiliza una expresión regular para eliminar emojis
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticones
                           u"\U0001F300-\U0001F5FF"  # símbolos y pictogramas
                           u"\U0001F680-\U0001F6FF"  # transporte y mapas
                           u"\U0001F700-\U0001F77F"  # alquimia, flechas, etc.
                           u"\U0001F780-\U0001F7FF"  # Geométricos Extendidos
                           u"\U0001F800-\U0001F8FF"  # Suplemento de Área de Planos
                           u"\U0001F900-\U0001F9FF"  # Símbolos de Lenguaje de Señas
                           u"\U0001FA00-\U0001FA6F"  # Símbolos Arqueológicos
                           u"\U0001FA70-\U0001FAFF"  # Símbolos CJK de Letras y Puntuación
                           u"\U00002702-\U000027B0"  # Diversos (Check, Cross, etc.)
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)

    # Reemplaza los emojis con una cadena vacía
    return emoji_pattern.sub(r'', text)

#Funcion para procesamiento de texto
def proc_text(comment):
  words_one=proc_info(comment);
  words_two=proc_tokenize(words_one);
  words_four=delete_stop_word(words_two);
  words_end=proc_lemmatize_and_stemming(words_four);
  return words_end;

#Corpus de comentarios
dwn_url_pruebas='/content/drive/MyDrive/ProyectoGrado/Maestria/Evaluaciones/dataset_test__.csv'
df_pruebas = pa.read_csv(dwn_url_pruebas, encoding='utf-8',header=None, sep=';');
df_pruebas.columns=["Comentario","Emocion"]

#df compuesto por dos columnas comentario y emoción
df_test = pa.DataFrame(columns=['Comentario', 'Emocion'])


#Proceso de limpieza y eliminacion
for index, row in df_pruebas.iterrows():
    comment = str(row['Comentario']);
    comment_without_emojis = remove_emojis(comment)
    comment_proc = proc_text(comment_without_emojis);
    if(len(comment_proc)==0):
      continue
    new_row = pa.DataFrame({'Comentario': comment_proc, 'Emocion': row['Emocion']},index=[0])
    df_test = pa.concat([df_test, new_row], ignore_index=True)

df_test_1=df_test

mapeo = {'scared': 0, 'mad': 1, 'sad': 2, 'surprise':3,'joyful':4, 'trust':5,'others':6}
df_test_1['Emocion'] = df_test_1['Emocion'].map(mapeo)
print(df_test_1['Emocion'])

"""#BUSQUEDA DE HIPERPARÁMETROS"""

X_train, X_test, y_train, y_test = train_test_split(df_test_1["Comentario"],df_test_1["Emocion"], test_size=0.2, random_state=42)
clf = MultinomialNB()
metric = 'accuracy'
# Definir el espacio de búsqueda de hiperparámetros
parameters = {'alpha': [0.01, 0.1, 1.0], 'fit_prior': [True, False]}
#Escalamiento de datos
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
#Busqueda de hiperparametros
from sklearn.model_selection import GridSearchCV
grid_search = GridSearchCV(clf, parameters, n_jobs=-1, cv=5)
grid_search.fit(X_train_tfidf, y_train)
#Impresión de los hiperparametros
print('The best model:\n', grid_search.best_params_)
clf_best = grid_search.best_estimator_
pred = clf_best.predict(X_test_tfidf)
print(f'The accuracy is: {clf_best.score(X_test_tfidf, y_test)*100:.1f}%')

"""#ENTRENAMIENTO DEL ALGORITMO"""

# Dividir los datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(df_test_1["Comentario"],df_test_1["Emocion"], test_size=0.2, random_state=42)

#Escalamiento de datos
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Inicializar y entrenar el modelo NB
clasificador = MultinomialNB(alpha=1.0, fit_prior=False)
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
clasificador.fit(X_train_tfidf, y_train_encoded)
# Realizar predicciones en el conjunto de prueba
y_pred = clasificador.predict(X_test_tfidf)


y_test_encoded = label_encoder.fit_transform(y_test)
accuracy = accuracy_score(y_test_encoded, y_pred)
print(f'Precisión del modelo: {accuracy}')

#Matriz de confusión
cm = confusion_matrix(y_test_encoded, y_pred);


print('\nReporte de clasificación:')
print(classification_report(y_test_encoded, y_pred))
print('\nMatriz de confusión:')
print(cm)

#Generación de matriz de confusión
disp_emocion = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['scared', 'mad', 'sad', 'surprise','joyful', 'trust'])
disp_emocion.plot(cmap=plt.cm.Blues)
plt.title('Matriz de Confusión para la Emoción')
plt.xlabel('Emociones')
plt.ylabel('Emociones')
plt.show()
