# app.py
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import bcrypt
import warnings
warnings.filterwarnings("ignore")

# Page Configuration
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# ------------------ Authentication ------------------
DB_FILE = "users_db.json"

# Load users from file
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

# Save users to file
def save_users(users):
    with open(DB_FILE, "w") as file:
        json.dump(users, file)

# Hash the password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Signup Page
def signup():
    st.subheader("Sign Up")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Create Account"):
        users = load_users()
        if new_user in users:
            st.error("Username already exists!")
        else:
            users[new_user] = hash_password(new_pass)
            save_users(users)
            st.success("Account created successfully. Please log in.")

# Login Page
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        if username in users and check_password(password, users[username]):
            st.success(f"Welcome, {username}!")
            return True
        else:
            st.error("Invalid credentials.")
    return False

# Main App
def main():
    st.title("🔍 WhatsApp Chat Analyzer")

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Sign Up":
        signup()
    else:
        if login():
            st.info("Now show your main app UI here...")

if __name__ == "__main__":
    main()
# ------------------ WhatsApp Analyzer ------------------
# Custom CSS Styling
st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .section-header {
        font-size: 20px;
        margin-top: 30px;
        color: #2E8B57;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: #1DB954;'>📱 WhatsApp Chat Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/whatsapp.png", width=80)
st.sidebar.header("📂 Upload WhatsApp Chat")
uploaded_file = st.sidebar.file_uploader("Upload a .txt chat export", type=["txt"])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Analyze for", user_list)

    if st.sidebar.button("🚀 Start Analysis"):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.markdown("### 📊 Key Chat Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💬 Messages", num_messages)
        col2.metric("📝 Words", words)
        col3.metric("📸 Media", num_media_messages)
        col4.metric("🔗 Links", num_links)

        st.markdown("---")

        if selected_user == "Overall":
            st.markdown("### 👥 Most Active Participants")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            ax.bar(x.index, x.values, color='#FF7F50')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            st.dataframe(new_df.style.highlight_max(axis=0))

        st.markdown("### ☁️ Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        st.markdown("### 💬 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color="#00BFFF")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.markdown("### 📅 Monthly Message Timeline")
        timeline = helper.monthy_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='#28A745', linewidth=2)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.markdown("### 📆 Daily Activity")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#007BFF', linewidth=2)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.markdown("### 🗓️ Activity Patterns")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🔁 Weekday Activity**")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color="#9370DB")
            st.pyplot(fig)

        with col2:
            st.markdown("**📆 Monthly Activity**")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="#F4A460")
            st.pyplot(fig)

        st.markdown("### 🔥 Weekly Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(user_heatmap, ax=ax, cmap="YlOrBr", linewidths=0.3, linecolor='gray')
        st.pyplot(fig)

        st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color: gray;'>Made with 💚 Streamlit</p>", unsafe_allow_html=True)
