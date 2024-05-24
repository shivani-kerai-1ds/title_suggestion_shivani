





import streamlit as st
import faiss
import numpy as np
from angle_emb import AnglE
import pandas as pd
from tqdm import tqdm
from boltons.iterutils import chunked
import pickle


import requests

API_URL_ner = "https://api-inference.huggingface.co/models/shivanikerai/TinyLlama-1.1B-Chat-v1.0-sku-title-ner-generation-reversed-v1.0"

headers = {"Authorization": "Bearer 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"}



def ner_title(title):
    # Define the roles and markers
    B_SYS, E_SYS = "<<SYS>>", "<</SYS>>"
    B_INST, E_INST = "[INST]", "[/INST]"
    B_in, E_in = "[Title]", "[/Title]"
    # Format your prompt template
    prompt = f"""{B_INST} {B_SYS} You are a helpful assistant that provides accurate and concise responses. {E_SYS}\nExtract named entities from the given product title. Provide the output in JSON format.\n{B_in} {title.strip()} {E_in}\n{E_INST}\n\n### NER Response:\n{{"{title.split()[0].lower()}"""
    output = query(API_URL_ner,{
    "inputs": prompt,
    "parameters": {"return_full_text":False,},
    "options":{"wait_for_model": True}
    })

    #return eval(pipe(text)[0]["generated_text"].split("### NER Response:\n")[-1])
    return ('{"'+title.split()[0].lower()+(output[0]['generated_text']))#.split("### NER Response:\n")[-1]))


def query(API_URL,payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def convert_to_dictionary(input_string):
    try:
        input_string = input_string.replace('</s>', '')
        input_string = input_string.replace("\n ","\n")
        input_string = input_string.replace(" :",":")
        input_string = input_string.replace("\n"," ")
        data_dict = {}
        for item in input_string.split('", "'):
            key, value = item.split('": "')
            key = key.strip('{}"')
            value = value.strip('{}"')
            data_dict[key] = value
        inverted_dict = {}
        for key, value in data_dict.items():
            if value in inverted_dict:
                if not isinstance(inverted_dict[value], list):
                    inverted_dict[value] = [inverted_dict[value]]
                inverted_dict[value].append(key)
            else:
                inverted_dict[value] = [key]
        return inverted_dict
    except Exception as e:
        #print(f"\nAn error occurred: {e}\n{input_string}")
        return({})

@st.cache_data
def uae_model():
    from angle_emb import AnglE

    uae = AnglE.from_pretrained('WhereIsAI/UAE-Large-V1', pooling_strategy='cls')#.cuda()
    return uae

# pkl_file_path = "save_model.pkl"
# with open(pkl_file_path, "rb") as f:
#   uae = pickle.load(f)

# Function to load the FAISS index from disk
@st.cache_data
def load_cat_index():
    return faiss.read_index("category_faiss_index.index")

@st.cache_data
def load_ams_index():
    return faiss.read_index("ams_faiss_index.index")

# Load the Excel file containing the documents
@st.cache_data
def load_cat_documents():
    df = pd.read_csv("amazon tree for indexing.csv")
    return list(df['tree'])

@st.cache_data
def load_ams_documents():
    df = pd.read_csv("ams keywords.csv")
    return list(df['input_search_term'])

# Search function using the loaded index and documents

def search_in_cat(index, docs, title, model, k):
    vec = model.encode([title])
    D, I = index.search(vec, k)
    doc_values = [docs[doc_id] for doc_id in I[0]]
    return doc_values

def search_in_ams(index, docs, title, model, k):
    vec = model.encode([title])
    D, I = index.search(vec, k)
    doc_values = [docs[doc_id] for doc_id in I[0]]
    return doc_values


def cat(title):
    return(search_in_cat(load_cat_index(), load_cat_documents(), title, uae_model(), 1)[0])

def keys(cat):
    return(search_in_ams(load_ams_index(), load_ams_documents(), cat, uae_model(), 12))




def main():


    st.title("Amazon Title Suggestion")
    initialize_state()

    if not st.session_state.submitted_title:
        submit_title()
    elif st.session_state.submitted_title and not st.session_state.submitted_ner_keywords:
        submit_ner_keywords()

    if st.button("Reset"):
        reset_app()


def initialize_state():
    if "title" not in st.session_state:
        st.session_state.title = ""
    if "ner_dict" not in st.session_state:
        st.session_state.ner_dict = {}
    if "selected_keywords" not in st.session_state:
        st.session_state.selected_keywords = []
    if "submitted_title" not in st.session_state:
        st.session_state.submitted_title = False
    if "submitted_ner_keywords" not in st.session_state:
        st.session_state.submitted_ner_keywords = False

def submit_title():

    title = st.text_input("Enter Product Title:", value=st.session_state.title)
    if st.button("Submit Title"):
        st.session_state.title = title
        ner_result = ner_title(title)
        ner=convert_to_dictionary(ner_result)
        category=cat(title)
        st.session_state.category = category
        st.session_state.ner_dict = ner
        st.session_state.ner_result_dict = ner_result
        st.session_state.submitted_title = True



def submit_ner_keywords():
    title=st.session_state.title
    st.write("Product Title:", title)

    # Display the title with NER annotations
    st.subheader("1DS Artificial Intelligence")

    # Start from the original title and replace phrases one by one
    annotated_title = st.session_state.title
    ner_result=eval(st.session_state.ner_result_dict )

    entities = sorted(ner_result, key=lambda x: title.lower().find(x.lower()))

    # Apply HTML tags to each entity found in the title
    for entity in entities:
        start_index = title.lower().find(entity.lower())
        if start_index != -1:  # Only proceed if the entity is found
            original_text = title[start_index:start_index + len(entity)]
            # Replace the original text with the annotated version in the title
            annotated_title = annotated_title.replace(original_text,
                f"{original_text}<span style='color:green;'>({ner_result[entity]})</span>", 1)

    # Display the fully annotated title using HTML to allow styling
    st.markdown(annotated_title, unsafe_allow_html=True)
    
    st.write("This product is categorized under <span style='font-weight:bold; color:yellow'>", st.session_state.category, "</span>", unsafe_allow_html=True)


    st.subheader("Product Features:")
    selected_features = []
    for key, value in st.session_state.ner_dict.items():
        if st.checkbox(f"{key}: {value}"):
            selected_features.append(value)

    st.subheader("AMS Search Terms:")
    #st.write(st.session_state.ner_dict['product'])

    #keyword_list=keys(st.session_state.ner_dict['product'][0])
    keyword_list=keys(st.session_state.category)#keyword_list[:20]#['a','b','c','f','g',"Feature", "Price", "Quality", "Availability"]
    # for keyword in keyword_list:
    #     st.checkbox(keyword, key=keyword)
    col1, col2, col3, col4 = st.columns(4)
    columns = [col1, col2, col3, col4]

    # Distribute keywords evenly across the four columns
    for i, keyword in enumerate(keyword_list):
        with columns[i % 4]:
            if st.checkbox(keyword, key=keyword):
                selected_features.append(keyword)
    if st.button("Suggest Titles"):
        model2_keywords = [keyword for keyword in keyword_list if st.session_state[keyword]]
        st.session_state.selected_keywords = model2_keywords
        st.session_state.submitted_ner_keywords = True
        st.write("Selected Keywords for Model2:", model2_keywords)
        st.write("Selected features for Model2:", selected_features)




def reset_app():
    # Clear relevant session states
    st.session_state.title = ""
    st.session_state.ner_dict = {}
    st.session_state.selected_keywords = []
    st.session_state.submitted_title = False
    st.session_state.submitted_ner_keywords = False

    # Optionally clear any dynamic states you may have added
    # such as checkboxes or other inputs

    dynamic_keys = [key for key in st.session_state.keys() if key.startswith('dynamic_')]
    for key in dynamic_keys:
        del st.session_state[key]

    # Display the initial title input UI
    submit_title()




if __name__ == "__main__":
    main()



