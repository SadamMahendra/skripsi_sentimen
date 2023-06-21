import streamlit as st
from deta import Deta
import streamlit_authenticator as stauth

#admin
from page_admin.admin_home import admin_home
from page_admin.admin_record import admin_record
from page_admin.admin_regis import admin_register

#user
from page_user.user_home import homePage as user_home
from page_user.user_record import user_record
from page_user.user_update import user_update

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

def app():
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
    name, authenticator_status, username = authenticator.login("Login", "main")

    if authenticator_status == False:
        st.error("Username/Passwordnya salah")

    if authenticator_status == None:
         st.warning("Tolong masukan username dan passsword anda")

    if authenticator_status == True:
        st.sidebar.title(f"Selamat Datang, {name}")      
        response = get_user(username) 
        user_data = response 
        level = user_data["level"]
        
        if level == "admin":
            menu = ["HOME","LAPORAN","REGISTER"]
            selected = st.sidebar.selectbox("Navigasi",menu)
            authenticator.logout("logout","sidebar")  
            if selected == "HOME":
                admin_home()
            if selected == "LAPORAN":
                admin_record()
            if selected == "REGISTER":
                admin_register(username)


        if level == "user":
            menu = ["HOME","LAPORAN", "SETTING"]
            selected = st.sidebar.selectbox("Navigasi",menu)
            authenticator.logout("logout","sidebar")  
            if selected == "HOME":
                user_home()
            if selected == "LAPORAN":
                user_record()
            if selected == "SETTING":
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