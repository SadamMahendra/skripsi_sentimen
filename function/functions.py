import re
from unidecode import unidecode
import pandas as pd
# from nlp_id.lemmatizer import Lemmatizer
from nlp_id.stopword import StopWord
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import nltk
from nltk import word_tokenize
from sklearn.svm import SVC
from sklearn import metrics
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#kamuss
df_positive = pd.read_csv('https://raw.githubusercontent.com/SadamMahendra/ID-NegPos/main/positive.txt', sep='\t',names=['positive'])
list_positive = list(df_positive.iloc[::,0])
df_negative = pd.read_csv('https://raw.githubusercontent.com/SadamMahendra/ID-NegPos/main/negative.txt', sep='\t',names=['negative'])
list_negative = list(df_negative.iloc[::,0])

#CaseFolding
def CaseFolding(text):
    text = text.lower()
    text = unidecode(text)
    return text

def cleansing(text):
    # menghapus karakter yang bukan huruf, angka, atau spasi
    text = re.sub(r'[^\w\s]', ' ', text)
    # menghapus angka menjadi satu spasi
    text = re.sub(r'\d+', '', text)
    # menghapus multi-spasi menjadi satu spasi
    text = re.sub(r'\s+', ' ', text).strip()
    return text

#lematizer
# lemmatizer = Lemmatizer()

#Stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

#slangword
kbba_dictionary = pd.read_csv('https://raw.githubusercontent.com/SadamMahendra/kamus_kbba/main/kbba.txt', delimiter='\t', names=['slang', 'formal'], header=None, encoding='utf-8')
slang_dict = dict(zip(kbba_dictionary['slang'], kbba_dictionary['formal']))

#convert Slangword
def convert_slangword(text):
    words = text.split()
    normalized_words = [slang_dict[word] if word in slang_dict else word for word in words]
    normalized_text = ' '.join(normalized_words)
    return normalized_text

#stopword
stopword = StopWord()

#split text
def split_word(teks):
    list_teks = []
    for txt in teks.split(" "):
        list_teks.append(txt)
    return list_teks

#menghilangkan kata kata yang tidak ingin dipakai
unwanted_words = ['jan','feb','mar','apr','mei','jun','jul','aug','sep','oct','nov','dec','uaddown','weareuad','Iam','https','igshid']
nltk.download('punkt')

def RemoveUnwantedwords(text):
    word_tokens = word_tokenize(text)
    filtered_sentence = [word for word in word_tokens if not word in unwanted_words]
    return ' '.join(filtered_sentence)

#menghitung polarty
def sentiment_analysis_lexicon_indonesia(text):
    positive_words = []
    negative_words = []
    neutral_words = []
    score = 0
    for word in text:
        if (word in list_positive):
            score += 1
            positive_words.append(word)
        if (word in list_negative):
            score -= 1
            negative_words.append(word)
        if (word not in list_positive and word not in list_negative): 
            neutral_words.append(word)

    polarity=''
    if (score > 0):
        polarity = 'positive'
    elif (score < 0):
        polarity = 'negative'
    else:
        polarity = 'neutral'
    
    result = {'positif': positive_words,'negatif':negative_words,'netral': neutral_words}
    return score, polarity, result, positive_words, negative_words

#Polarity Tahunan
def Polarity_Tahunan(df):
    # Mengubah kolom 'at' menjadi tipe datetime jika belum
    df['at'] = pd.to_datetime(df['at'])

    # Membuat kolom baru 'year' untuk menyimpan tahun dari kolom 'at'
    df['year'] = df['at'].dt.year

    # Menghitung jumlah nilai positif dan negatif untuk setiap tahun
    df_grouped = df.groupby(['year', 'polarity']).size().unstack(fill_value=0)

    # Menghilangkan tanda koma pada label sumbu x
    df_grouped.index = df_grouped.index.astype(str)
    return df_grouped

#tfidf
def process_data(df):
    df['Text_Clean_New'] = df['Text_Clean'].astype(str)
    tfidf = TfidfVectorizer()
    ulasan = df['Text_Clean_New'].values.tolist()
    tfidf_vect = tfidf.fit(ulasan)
    X = tfidf_vect.transform(ulasan)
    y = df['polarity']
    return X, y

# def hitung_kamus(df):
#     # Mengubah kolom 'Text_Clean' menjadi tipe data string
#     df['Text_Clean_New'] = df['Text_Clean'].astype(str)

#     # Menghitung frekuensi kemunculan kata dengan CountVectorizer
#     count_vectorizer = CountVectorizer(tokenizer=word_tokenize)
#     ulasan = df['Text_Clean_New'].values.tolist()
#     X_count = count_vectorizer.fit_transform(ulasan)

#     # Menginisialisasi dan melatih model TF-IDF dengan TfidfVectorizer
#     tfidf = TfidfVectorizer()
#     X_tfidf = tfidf.fit_transform(ulasan)

#     # Mendapatkan kata-kata unik dari kamus
#     kata_unik = count_vectorizer.get_feature_names()

#     # Menghitung frekuensi kemunculan dan nilai TF-IDF untuk setiap kata
#     kamus = {}
#     for i, kata in enumerate(kata_unik):
#         kamus[kata] = {
#             'Frekuensi': X_count[:, i].sum(),
#             'TF-IDF': tfidf.idf_[tfidf.vocabulary_[kata]]
#         }

#     # Membuat DataFrame dari kamus
#     df_kamus = pd.DataFrame.from_dict(kamus, orient='index')
#     df_kamus.index.name = 'Kata'

#     return df_kamus

#ranking
def calculate_tfidf_ranking(df):
    max_features = len(df)

    tf_idf = TfidfVectorizer(max_features=max_features, binary=True)
    tfidf_mat = tf_idf.fit_transform(df["Text_Clean"]).toarray()

    terms = tf_idf.get_feature_names_out()

    sums = tfidf_mat.sum(axis=0)

    data = []
    for col, term in enumerate(terms):
        data.append((term, sums[col]))

    ranking = pd.DataFrame(data, columns=['term', 'rank'])
    ranking.sort_values('rank', ascending=False, inplace=True)

    return ranking


#user
def hasilTextMining(text):
    text = re.sub(r'j&t', 'jnt', text, flags=re.IGNORECASE)
    caseFolding = CaseFolding(text)
    clean = cleansing(caseFolding)
    # lematisasi = lemmatizer.lemmatize(clean)
    stemmerWord = stemmer.stem(clean)    
    slangWord = convert_slangword(stemmerWord)
    stopWord = stopword.remove_stopword(slangWord)
    unwatedWord = RemoveUnwantedwords(stopWord)
    hapusTigaHuruf = ' '.join(re.findall(r'\w{3,}', unwatedWord))
    splitWord = split_word(hapusTigaHuruf)
    
    return splitWord

def hasilUltimatum(text):
    h1 = hasilTextMining(text)
    score, polarity, result, positive_words, negative_words = sentiment_analysis_lexicon_indonesia(h1)

    return score, polarity, result

#admin
def hasilFileMining(df, selected_column):
    df[selected_column] = df[selected_column].str.replace('j&t', 'jnt', case=False)
    df["caseFolding"] = df[selected_column].apply(CaseFolding)
    df["cleansing"] = df["caseFolding"].apply(cleansing)
    # df["lemmatizer"] = df["cleansing"].apply(lemmatizer.lemmatize)
    df["stemmer"] = df["cleansing"].apply(stemmer.stem)
    df["slang"] = df["stemmer"].apply(convert_slangword)
    df["stopword"] = df["slang"].apply(stopword.remove_stopword)
    df["Text_Clean"] = df["stopword"].apply(RemoveUnwantedwords)
    df["Text_Clean"] = df["Text_Clean"].str.findall('\w{3,}').str.join(' ')
    df["Text_Clean_split"] = df["Text_Clean"].apply(split_word)

    hasil = df['Text_Clean_split'].apply(sentiment_analysis_lexicon_indonesia)
    hasil = list(zip(*hasil))
    df['polarity_score'] = hasil[0]
    df['polarity'] = hasil[1]
    df = df[df.polarity != 'neutral']
    hasil_positive = hasil[3]
    hasil_negative = hasil[4]

    return df, hasil_positive, hasil_negative

#wordCloud
def wordcloud_positive(df):
    df_positive = df[df["polarity"] == "positive"]

    text_positive = ' '.join(df_positive['Text_Clean'])

    wordcloud_positive = WordCloud(width=800, height=800, background_color='white', colormap='Greens').generate(text_positive)

    fig, axs = plt.subplots(figsize=(8, 3))
    axs.imshow(wordcloud_positive, interpolation='bilinear')
    axs.set_title('Positive Words')
    axs.axis('off')

    return fig

def wordcloud_negative(df):
    df_negative = df[df["polarity"] == "negative"]

    text_negative = ' '.join(df_negative['Text_Clean'])

    wordcloud_negative = WordCloud(width=800, height=800, background_color='white', colormap='Reds').generate(text_negative)

    fig, axs = plt.subplots(figsize=(8, 3))
    axs.imshow(wordcloud_negative, interpolation='bilinear')
    axs.set_title('Negative Words')
    axs.axis('off')

    return fig

#top word setiap 10 kata negatif dan positif
def process_top_10_words(hasil_positive,hasil_negative):
    all_positive_words = [word for sublist in hasil_positive for word in sublist]
    all_negative_words = [word for sublist in hasil_negative for word in sublist]
    positive_freq = pd.Series(all_positive_words).value_counts().reset_index().rename(columns={'index': 'Positive Word', 0: 'Frequency'})
    negative_freq = pd.Series(all_negative_words).value_counts().reset_index().rename(columns={'index': 'Negative Word', 0: 'Frequency'})
    top_10_positive = positive_freq.head(10)
    top_10_negative = negative_freq.head(10)
    return top_10_positive, top_10_negative

#svm
def predic_SVM(X_train, X_test, y_train, y_test):
    svm = SVC(
    kernel = 'linear',
        C = 1)

    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    score = metrics.accuracy_score(y_test, y_pred)
    score_svmlk = score

    return score_svmlk, svm, y_pred