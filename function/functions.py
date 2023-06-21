import unicodedata,re
import pandas as pd
from nlp_id.lemmatizer import Lemmatizer
from nlp_id.stopword import StopWord
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import nltk
from nltk import word_tokenize

#kamuss
df_positive = pd.read_csv('https://raw.githubusercontent.com/ramaprakoso/analisis-sentimen/master/kamus/positif_ta2.txt', sep='\t',names=['positive'])
list_positive = list(df_positive.iloc[::,0])
df_negative = pd.read_csv('https://raw.githubusercontent.com/SadamMahendra/ID-NegPos/main/negative.txt', sep='\t',names=['negative'])
list_negative = list(df_negative.iloc[::,0])

#CaseFolding
def CaseFolding(text):
    text = unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('utf-8','ignore')
    text = re.sub(r'[\W_]+',' ',text)
    text = re.sub(r'\d+', '', text).strip()
    text = text.lower()
    text = re.sub('[\s]+', ' ', text)
    return text

#lematizer
lemmatizer = Lemmatizer()

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

#split text
def split_word(teks):
    list_teks = []
    for txt in teks.split(" "):
        list_teks.append(txt)
    return list_teks

#stopword
stopword = StopWord()
stopwords = stopword.get_stopword()

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

#menghilangkan kata kata yang tidak ingin dipakai
unwanted_words = ['jan','feb','mar','apr','mei','jun','jul','aug','sep','oct','nov','dec','uaddown','weareuad','Iam','https','igshid']
nltk.download('punkt')

def RemoveUnwantedwords(text):
    word_tokens = word_tokenize(text)
    filtered_sentence = [word for word in word_tokens if not word in unwanted_words]
    return ' '.join(filtered_sentence)

def hasilTextMining(text):
    text = re.sub(r'j&t', 'jnt', text, flags=re.IGNORECASE)
    caseFolding = CaseFolding(text)
    lematisasi = lemmatizer.lemmatize(caseFolding)
    stemmerWord = stemmer.stem(lematisasi)    
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

def hasilFileMining(df, selected_column):
    df[selected_column] = df[selected_column].str.replace('j&t', 'jnt', case=False)
    df["caseFolding"] = df[selected_column].apply(CaseFolding)
    df["lemmatizer"] = df["caseFolding"].apply(lemmatizer.lemmatize)
    df["stemmer"] = df["lemmatizer"].apply(stemmer.stem)
    df["slang"] = df["stemmer"].apply(convert_slangword)
    df["stopword"] = df["slang"].apply(stopword.remove_stopword)
    df["Text_Clean"] = df["stopword"].apply(RemoveUnwantedwords)
    df["Text_Clean"] = df["Text_Clean"].str.findall('\w{3,}').str.join(' ')
    df["Text_Clean_split"] = df["Text_Clean"].apply(split_word)

    hasil = df['Text_Clean_split'].apply(sentiment_analysis_lexicon_indonesia)
    hasil = list(zip(*hasil))
    df['polarity_score'] = hasil[0]
    df['polarity'] = hasil[1]

    return df['Text_Clean'],df['polarity'],hasil

def process_top_10_words(df,hasil):
    all_positive_words = [word for sublist in hasil[3] for word in sublist]
    all_negative_words = [word for sublist in hasil[4] for word in sublist]
    positive_freq = pd.Series(all_positive_words).value_counts().reset_index().rename(columns={'index': 'Positive Word', 0: 'Frequency'})
    negative_freq = pd.Series(all_negative_words).value_counts().reset_index().rename(columns={'index': 'Negative Word', 0: 'Frequency'})
    top_10_positive = positive_freq.head(10)
    top_10_negative = negative_freq.head(10)
    return top_10_positive, top_10_negative

# def remove_stopwords_with_exception(text, stopwords, kamus_positif, kamus_negatif):
#     words = text.split()
#     cleaned_words = []
#     for word in words:
#         word = word.strip(string.punctuation)  # Menghapus tanda baca dari kata
#         if word in kamus_positif or word in kamus_negatif or word not in stopwords:
#             cleaned_words.append(word)
#     return " ".join(cleaned_words)

#split word
# def split_words(sentence, positive_words, negative_words):
#     words = sentence.split()
#     result = []
#     i = 0
#     while i < len(words):
#         word = words[i]
#         if word in positive_words or word in negative_words:
#             result.append(word)
#             i += 1
#         elif i+1 < len(words):
#             merged_word = word + ' ' + words[i+1]
#             if merged_word in positive_words or merged_word in negative_words:
#                 result.append(merged_word)
#                 i += 2
#             else:
#                 result.append(word)
#                 i += 1
#         else:
#             result.append(word)
#             i += 1
#     return result