import streamlit as st
import pickle
from function.functions import hasilUltimatum, hasilTextMining

pickle_in = open('./data/model.pkl', 'rb')
svm,tfidf = pickle.load(pickle_in)

def homePage():
    st.header("Streamlit Predictor")
    rawText =  st.text_area("Masukan Text disini :")
    submitButton = st.button("analisis")
    if submitButton:
        score,polarity,result = hasilUltimatum(rawText)
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
 
        # col1,col2 = st.columns(2)
        # if polarity == 'negative':
        #     with col1:
        #         st.warning(f"Polarity berdominan {polarity} dengan score {score}")
        #     with col2:
        #         st.write(result)
        # elif polarity == 'positive':
        #     with col1:
        #         st.success(f"Polarity berdominan {polarity}")
        #     with col2:
        #         st.write(result)
        # else:
        #     with col1:
        #         st.info(f"Polarity berdominan {polarity}")
        #     with col2:
        #         st.write(result)

if __name__ == "__main__":
    homePage()