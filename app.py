import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
USERS_DB = "users_db.json"

# ------------------ User Auth ------------------

def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_DB, "w") as f:
        json.dump(users, f)

def signup(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    return users.get(username) == password

# ------------------ WhatsApp Analyzer ------------------

def whatsapp_analyzer():
    st.markdown("<h2 style='text-align: center; color: #1DB954;'>📊 WhatsApp Chat Analyzer</h2>", unsafe_allow_html=True)

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

            st.markdown("### 📅 Monthly Timeline")
            timeline = helper.monthy_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='#28A745')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.markdown("### 📆 Daily Activity")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#007BFF')
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

# ------------------ Auth UI ------------------

def auth_ui():
    st.markdown("<h1 style='text-align: center; color: green;'>📱 WhatsApp Chat Analyzer</h1>", unsafe_allow_html=True)

    menu = st.selectbox("Choose an option", ["Login", "Sign Up"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Sign Up":
        if st.button("Sign Up"):
            if signup(username, password):
                st.success("Sign up successful! Please log in.")
            else:
                st.error("Username already exists.")
    else:
        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Logged in successfully!")
                st.experimental_rerun()  # <--- this solves the double click issue
            else:
                st.error("Invalid username or password")

# ------------------ App Entry ------------------

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        whatsapp_analyzer()
    else:
        auth_ui()

if __name__ == "__main__":
    main()
