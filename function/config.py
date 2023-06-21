import streamlit as st
from deta import Deta

key = st.secrets["db_key"]
deta = Deta(key)
db = deta.Base("users")

db_drive = deta.Drive("datas")


def insert_user(username,name,password,auth):
    try:
        db.insert({"key": username, "name": name, "password": password, "level": auth})
        return st.success("Berhasil Registrasi")
    except:
        return st.warning("username telah dipakai") 

def fetch_all_users():
    res = db.fetch()
    return res.items

def get_user(username):
    return db.get(username)

def update_user(username, updates):
    return db.update(updates, username)

def delete_user(username):
    return db.delete(username)