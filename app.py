import streamlit as st
from deta import Deta
import streamlit_authenticator as stauth
import base64

#admin
from page_admin.admin_home import admin_home
from page_admin.admin_record import admin_record
from page_admin.admin_regis import admin_register
from page_admin.admin_upload import admin_upload

#user
from page_user.user_dashboard import user_dashboard
from page_user.user_home import homePage as user_home
from page_user.user_record import user_record
from page_user.user_update import user_update

def add_background():
    image_file = 'data/bg.png'
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

deta = Deta(st.secrets["db_key"])
db = deta.Base("users")

def insert_user(username,name,password,auth):
    try:
        db.put({"key": username, "name": name, "password": password, "level": auth})
        return st.success("Berhasil Registrasi")
    except:
        return st.warning("username telah dipakai") 

def fetch_all_users():
    res = db.fetch()
    return res.items

def get_user(username):
    return db.get(username)

st.set_page_config(
    page_title="Sentimen Analisis App",
    page_icon="📦",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/SadamMahendra',
        'About': "Aplikasi Sentimen Analisis Jnt dibuat untuk memenuhi skripsi"
    }
)

def app():
    add_background()

    users = fetch_all_users()
    usernames = [user["key"] for user in users]
    names = [users["name"] for users in users]
    passwords = [user["password"] for user in users]
    levels = [user["level"] for user in users]

    credentials = {"usernames":{}}

    for un, name, pw, lvl in zip(usernames, names, passwords,levels):
        user_dict = {"name":name,"password":pw, "level":lvl}
        credentials["usernames"].update({un:user_dict})

    authenticator = stauth.Authenticate(credentials, "app_home", "auth", cookie_expiry_days=30)
    name_user, authenticator_status, username = authenticator.login("Login", "main")

    if authenticator_status == False:
        st.error("Username/Passwordnya salah")

    if authenticator_status == None:
         st.warning("Tolong masukan username dan passsword anda")

    if authenticator_status == True:   
        response = get_user(username) 
        user_data = response
        nama = user_data["name"] 
        level = user_data["level"]

        st.sidebar.title(f"Hallo, {nama}")   
        
        if level == "admin":
            menu = ["🏡 Home","💬 Sentiment Predictor","📖 Report","⚙️ Account Management"]
            selected = st.sidebar.selectbox("Navigasi",menu)
            authenticator.logout("logout","sidebar")  
            if selected == "🏡 Home":
                admin_home()
            if selected == "💬 Sentiment Predictor":
                user_home()
            if selected == "📖 Report":
                admin_record()
            if selected == "⚙️ Account Management":
                admin_register(username)

        if level == "user":
            menu = ["💬 Sentiment Predictor","📖 Report", "⚙️ Account Management"]
            selected = st.sidebar.selectbox("Navigasi",menu)
            authenticator.logout("logout","sidebar")  
            # if selected == "📊 Home":
            #     user_dashboard()
            if selected == "💬 Sentiment Predictor":
                user_home()
            if selected == "📖 Report":
                user_record()
            if selected == "⚙️ Account Management":
                user_update(username)

if __name__ == "__main__":
    app()

# -- Menghilangkan Streamlit Style --
hide_st_style = """
    <style>
    footer {visibility: hidden;}
    </style>
"""

st.markdown(hide_st_style,unsafe_allow_html=True)