import streamlit as st
import pickle
from function.functions import hasilTextMining

pickle_in = open('./data/model.pkl', 'rb')
svm,tfidf = pickle.load(pickle_in)

def homePage():
    st.header("💬 Sentiment Predictor",
              help="Halaman untuk memprediksi postif atau negatif dari suatu kalimat")
    st.markdown("---")
    rawText =  st.text_area("Masukan Text disini :",
                            placeholder="Paket yang dipesan dengan Jnt cepat sampai")
    submitButton = st.button("analisis")
    if submitButton:
        # score,polarity,result = hasilUltimatum(rawText)
        hasil_bersih = hasilTextMining(rawText)

        positive_negative = {
            "positive": [],
            "negative": [],
            "neutral": []
        }
        for i in hasil_bersih:
            tf = tfidf.transform([i])
            hasil = svm.predict(tf)
            if (hasil[0] ==  "negative"):
                positive_negative["negative"].append(i)
            if (hasil[0] ==  "positive"):
                positive_negative["positive"].append(i)
            if (hasil[0] == "neutral"):
                positive_negative["neutral"].append(i)
        
        positive_count = len(positive_negative["positive"])
        negative_count = len(positive_negative["negative"])

        if (negative_count > positive_count):
            st.warning("Hasil: Text berdominan negative")
        else:
            st.success("Hasil: Text berdominan positive")

        st.write(positive_negative)

if __name__ == "__main__":
    homePage()