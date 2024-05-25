

import streamlit as st
import time
import random

def api_1(title):
    # Simulate a delay for the API call
    time.sleep(2)  # Simulate a 2-second delay
    return {"key1": "value1", "key2": "value2", "key3": "value3"}

def api_2(title):
    # Simulate a delay for the API call
    time.sleep(2)  # Simulate a 2-second delay
    return "Category_Example"

def api_3(category):
    # Simulate a delay for the API call
    time.sleep(2)  # Simulate a 2-second delay
    return [f"keyword_{i}" for i in range(1, 51)]

def api_4(selected_dict, selected_keywords):
    # Simulate a delay for the API call
    time.sleep(2)  # Simulate a 2-second delay
    return [f"New Title {i}" for i in range(1, 6)]

def api_5(titles):
    # Simulate a delay for the API call and return a list of scores between 0 and 1
    time.sleep(2)  # Simulate a 2-second delay
    return [round(random.uniform(0, 1), 2) for _ in titles]

def reset_state():
    st.session_state.clear()
    st.session_state.step = 1

def main():
    st.title("Product Title Generation")

    # Step 1: User inputs the product title
    if 'step' not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        title = st.text_input("Enter the product title:")
        if st.button("Submit"):
            with st.spinner("Calling API 1..."):
                st.session_state.title = title
                st.session_state.api_1_response = api_1(title)
            st.session_state.step = 2

    # Step 2: Display title and API 1 response
    if st.session_state.step == 2:
        st.write(f"Title: {st.session_state.title}")
        st.write("API 1 Response:", st.session_state.api_1_response)
        with st.spinner("Calling API 2..."):
            st.session_state.category = api_2(st.session_state.title)
        with st.spinner("Calling API 3..."):
            st.session_state.keywords = api_3(st.session_state.category)
        st.session_state.step = 3

    # Step 3: Display keywords and dictionary response with checkboxes
    if st.session_state.step == 3:
        st.write(f"Category: {st.session_state.category}")
        
        st.write("Select from the dictionary response:")
        selected_dict = {}
        for key, value in st.session_state.api_1_response.items():
            if st.checkbox(f"{key}: {value}", key=key):
                selected_dict[key] = value

        new_key = st.text_input("Add new key:")
        new_value = st.text_input("Add new value:")
        if st.button("Add Key-Value Pair"):
            if new_key and new_value:
                st.session_state.api_1_response[new_key] = new_value
                st.experimental_rerun()

        st.write("Select keywords:")
        selected_keywords = []
        for keyword in st.session_state.keywords:
            if st.checkbox(keyword, key=keyword):
                selected_keywords.append(keyword)

        new_keyword = st.text_input("Add new keyword:")
        if st.button("Add Keyword"):
            if new_keyword:
                st.session_state.keywords.append(new_keyword)
                st.experimental_rerun()

        if st.button("Suggest Titles"):
            with st.spinner("Calling API 4..."):
                st.session_state.selected_dict = selected_dict
                st.session_state.selected_keywords = selected_keywords
                st.session_state.new_titles = api_4(selected_dict, selected_keywords)
            st.session_state.step = 4

    # Step 4: Display original and new product titles only after clicking "Suggest Titles"
    if st.session_state.step == 4:
        st.write(f"Original Title: {st.session_state.title}")
        st.write("New Product Titles:")
        titles = [st.session_state.title] + st.session_state.new_titles
        for title in titles:
            st.write(title)

        if st.button("Get Scores"):
            with st.spinner("Calling API 5..."):
                st.session_state.scores = api_5(titles)
            st.session_state.step = 5

    # Step 5: Display scores for each title on a new screen
    if st.session_state.step == 5:
        st.write("Product Titles with Scores:")
        titles = [st.session_state.title] + st.session_state.new_titles
        scores = st.session_state.scores
        for title, score in zip(titles, scores):
            st.write(f"{title}: {score}")
            st.progress(score)

    # Add Reset button
    if st.button("Reset"):
        reset_state()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
