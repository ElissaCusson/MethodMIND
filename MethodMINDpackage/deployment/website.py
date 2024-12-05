import streamlit as st
from PIL import Image
from MethodMINDpackage.orchestration.LLM import llm_gemini_response_generation
from MethodMINDpackage.orchestration.retrieval import user_input_enhancing, search_similarity, query_by_id, get_abstract_by_doi, handle_multiple_similarities
from MethodMINDpackage.deployment.firewall import firewall_all_keywords
from MethodMINDpackage.orchestration.reranking import reranking

st.set_page_config(layout="wide")

number_of_abstracts_to_search_similarity = 30

#                                                   HOME

def home_page():
    #home page

    #displaying logo at the center

    image_path = "MethodMINDpackage/deployment/images/New_Logo.jpg"
    try:
        # Try to open the image
        image = Image.open(image_path)
        st.columns(3)[1].image(image)
    except Exception:
        # If file not found, display a placeholder message
        st.columns(3)[1].write('Image not found or cannot be opened.')

    #displaying title at the center
    st.markdown("<h1 style='text-align: center;'>Welcome to MethodMIND</h1>", unsafe_allow_html=True)

    #subheader
    st.markdown(
        "<h1 style='text-align: center; color: gray; font-size: 30px;'>Your research companion for brain diseases</h1>",
        unsafe_allow_html=True)

    #description
    st.subheader('Description:')
    with st.container(border = True):
        st.markdown('''
        Our platform helps researchers like you discover the most relevant and up-to-date methods for studying and treating brain diseases.
        Simply enter your research question or hypothesis, and our model will search through a vast database of PubMed
        abstracts, pinpointing studies and methodologies most related to your query.

        Instead of spending hours reading all the different abstracts to find a solution, start by submitting your
        hypothesis, and let us do the rest!
        ''')


    #space
    st.write('##')

    #frequently asked questions
    st.subheader('Example questions:')
    columns = st.columns(2)

    st.markdown("""
        <style>
            .container-border {
                border: 2px solid #4CAF50; /* Green border */
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .container-border p {
                font-size: 16px;
                color: #333;
            }
        </style>
    """, unsafe_allow_html=True)

    # First column with a container and border
    with columns[0]:
        st.markdown('<div class="container-border">Which methods can I use to measure gait improvement in Parkinson patients receiving deep brain stimulation?</div>', unsafe_allow_html=True)

    # Second column with a container and border
    with columns[1]:
        st.markdown('<div class="container-border">Which methods can I use to measure migraine intensity?</div>', unsafe_allow_html=True)

    #number of abstracts
    slider_values = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    number_of_abstracts = st.select_slider('Select a number of abstracts to return:', options=slider_values, value=10)

    #request
    text_input = st.text_area('Type your request here:')


#                                                      TASKS
    #TASK START
    #loading spinner
    if st.button('Submit'):

        with st.spinner('Processing... Please wait'):

            #loading progress
            progress_bar = st.empty()
            progress_bar.progress(0)
            progress_text = st.empty()

            #verifying each step
            done_processing = True
            stopped_by_firewall = False
            stopped_at_similarity = False
            stopped_at_query_by_id = False
            stopped_at_abstract_by_doi = False

            #here we do the task
            progress_text.text('Validating input...🤔')

            #new firewall
            is_valid = firewall_all_keywords(text_input)
            if is_valid:

                progress_text.text('Searching for relevant abstracts...🔍')
                progress_bar.progress(15)

                #enhancing input
                text_enhanced = user_input_enhancing(text_input)
                similarity = search_similarity(text_enhanced, k = number_of_abstracts_to_search_similarity)

                #best similarity threshold at 0.88

                #verify similarity step
                if similarity[1] is False:
                    stopped_at_similarity = True
                    done_processing = False
                    ids = 0
                else:
                    ids = handle_multiple_similarities(similarity[0][0])

                    progress_text.text('Fetching DOI information...🎣')
                    progress_bar.progress(25)

                #important data here
                metadata_list = query_by_id(ids)

                #verify query by id step
                if metadata_list[1] is False:
                    stopped_at_query_by_id = True
                    done_processing = False
                else:
                    progress_text.text('Retrieving abstracts...🛒')
                    progress_bar.progress(40)

                abstract_by_doi_list = get_abstract_by_doi(metadata_list[0])

                #verify abstract by doi step
                if abstract_by_doi_list[1] is False:
                    stopped_at_abstract_by_doi = True
                    done_processing = False
                else:
                    progress_text.text('Reranking relevant abstracts...🔄')
                    progress_bar.progress(55)

                # #reranking
                reranked = reranking(text_input, abstract_by_doi_list[0], number_of_abstracts)

                progress_text.text('Generating answer...🚀')
                progress_bar.progress(75)

                #final list of dictionaries
                final_form = reranked

                #full text input for llm
                #make abstracts in sequence
                abstracts_in_sequence = ''
                i=1
                for a in final_form:
                    abstracts_in_sequence += f'\n\n{i,a["abstract"]}'
                    i=1+1

                #full text input
                #full_text_input = f'''Based on the following abstracts, {text_input} \n\n Abstracts: {abstracts_in_sequence}'''
                full_text_input = f'''You are a lecturer specializing in central nervous system, brain and neurodegenerative diseases. Your role is to provide detailed, accurate, and evidence-based explanations to answer the following question: {text_input}.
                                    Analyze the data provided in the abtracts bellow and synthesize the information into a clear and concise explanation to answer the question. Your responses must:
                                    1. Explain concepts in a way suitable for a professional audience, such as researchers, or health practitioners, while remaining approachable for non-experts if necessary. You don't give your opinion.
                                    2. Use medical terminology appropriately, but ensure definitions or explanations are provided for complex terms.
                                    3. Provide references to the abtract number into brackets after each corresponding sentences.
                                    4. Organize responses into structured formats when appropriate (e.g., bullet points, numbered lists).
                                    If the input data is unclear or insufficient, request clarification or more context to ensure an accurate response.
                                    Here are the abstract data: {abstracts_in_sequence}'''

                #full llm
                output = llm_gemini_response_generation(full_text_input)

            else:
                #in case there are other types of errors
                stopped_by_firewall = True
                done_processing = False


            progress_bar.progress(100)

        #                                               OUTPUT

        if done_processing:

            progress_text.text('Done ✅')

            #results output
            st.markdown(f"""<div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px;">{output}</div>""", unsafe_allow_html=True)

            # For multiple abstracts
            abstracts_list = []
            j = 1

            for abs in final_form:
                dictionary = {}
                dictionary['num'] = j
                dictionary['title'] = abs.get('title')
                dictionary['link'] = abs.get('link')
                dictionary['date'] = abs.get('date')
                abstracts_list.append(dictionary)
                j += 1


            # Generate the HTML for multiple abstracts
            abstracts_html = "".join([
                f'''<strong>{index + 1}. {abstract["title"]}</strong>
                <span style="font-style: italic; color: #aaa;">({abstract["date"]})</span>:
                <a href="{abstract["link"]}" target="_blank" style="color: orange; text-decoration: none; word-wrap: break-word;">{abstract["link"]}</a>
                <br><br>'''
                for index, abstract in enumerate(abstracts_list)
            ])

            st.write('###')

            #displaying abstracts
            st.markdown('### Abstracts:')
            st.markdown(f"""<div style="border: 2px solid gray; padding: 10px; border-radius: 5px;">{abstracts_html}</div>""", unsafe_allow_html=True)

        #if request is outside of scope
        elif stopped_by_firewall:
            progress_text.text('Stopped 🛑')
            st.subheader('The request is outside of the scope of the model.🥺')
            st.subheader('Please try again with another request.🙏')

        #if stopped at similarity step
        elif stopped_at_similarity:
            progress_text.text('Stopped 🛑')
            st.subheader(similarity[2])

        #if stopped at query by id step
        elif stopped_at_query_by_id:
            progress_text.text('Stopped 🛑')
            st.subheader(metadata_list[2])

        #if stopped at abstract by doi
        elif stopped_at_abstract_by_doi:
            progress_text.text('Stopped 🛑')
            st.subheader('stopped at abstract_by_doi')

    #disclaimer
    #st.caption('MethodMIND can make mistakes. Please check important information')
    st.markdown("""
        <p style="text-align: center; font-size: 18px; color: gray;">
            <strong>MethodMIND can make mistakes. Please check important information carefully.</strong>
        </p>
    """, unsafe_allow_html=True)

#                                                    DISCLAIMER

def disclaimer_page():
    #disclaimer page

    st.title('Disclaimer')
    with st.container(border = True):
        st.markdown('''While MethodMIND is designed to provide helpful insights
             based on PubMed abstracts, please note that the model may occasionally
             generate inaccurate or incomplete information. The results are intended
             to assist in your research but should not be considered definitive.
             We strongly recommend carefully reviewing and verifying the answers before
             applying them to your work. Always consult primary sources and expert opinions
             when making important research decisions.''')

        st.markdown('''
            Please note that the abstracts provided are sourced exclusively from publications between 2014 and 2024.
        ''')

        st.markdown('''
            If you're not satisfied with the publications or the answer provided, there's a chance you may receive a different response by clicking the submit button again.
        ''')

#                                                      ABOUT

def about_page():
    #about page

    st.title('About MethodMIND')
    st.markdown('''## What is MethodMIND?''')
    st.markdown('''MethodMIND is an advanced research tool designed to empower scientists, researchers, and healthcare professionals by providing tailored recommendations for experimental methodologies. It bridges the gap between complex scientific queries and actionable insights, helping users identify the best methods for their research needs.''')
    st.markdown('''## Why is MethodMIND Important?''')
    st.markdown('''In the era of information overload, researchers often face challenges in finding precise, evidence-based answers to their specific scientific questions. MethodMIND solves this problem by leveraging cutting-edge technology to curate and deliver methodologically sound recommendations. This tool aims to accelerate innovation and improve the reproducibility of scientific research across diverse domains, including neuroscience, biomedical research, and more.''')
    st.markdown('''## How Does MethodMIND Work?''')
    st.markdown('''MethodMIND combines powerful technologies to provide accurate and context-aware recommendations:
Retrieval-Augmented Generation (RAG): Ensures access to a curated, up-to-date knowledge base, linking user queries with relevant literature and methodologies.
SciBERT: A specialized language model trained on scientific texts to understand and analyze complex research language and concepts effectively.
Large Language Models (LLMs): Enhance the tool’s ability to provide comprehensive and coherent responses tailored to user queries.''')

    st.markdown('## Our Vision')
    st.markdown('''At MethodMIND, we believe in unlocking the potential of cutting-edge AI to advance science. By streamlining the process of hypothesis testing and methodology selection, we aim to empower the global research community to achieve breakthroughs faster and more efficiently.''')

    st.markdown('''
        ## Credits

        Our platform utilizes the following advanced technologies:

        - **Gemini LLM**: A powerful language model used to generate the answer given.
        - **SciBERT Embeddings**: A BERT-based model optimized for scientific text understanding.
        - **Milvus**: A high-performance vector database for efficient similarity search and data management.
        - **PubMed**: A resource used for obtaining and referencing scientific abstracts.

        These tools and resources are integral to the functionality of our platform, and their use is subject to their respective terms and conditions.

    ''')



def team_page():
    st.markdown('## The Team')

    ############################
    ### Elissa
    ############################

    image_ecu_path = "MethodMINDpackage/deployment/images/Elissa.jpg"
    try:
        # Try to open the image
        image_ecu = Image.open(image_ecu_path)
        col1, col2 = st.columns([1, 2])  # Set the first column smaller than the second
        with col1:
            st.image(image_ecu)
        with col2:
            col2.markdown(
                f"""
                <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
                    <h3>Elissa Cusson, CEO & Programmer</h3>
                    <p>With an MSc in neuroscience and extensive experience as a consultant, I specialize in leveraging AI and machine learning to optimize market access, evidence value, and scientific research in healthcare. Passionate about advancing innovation, I apply my expertise to transform healthcare processes, making them more efficient and impactful. Outside of my professional work, I enjoy climbing and mountaineering, exploring the great outdoors and challenging myself with new summits.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        # st.columns(3)[1].image(image_ecu)
    except Exception:
        # If file not found, display a placeholder message
        col1, col2 = st.columns([1, 2])
        with col1:
            st.columns(3)[1].write('Image not found or cannot be opened.')
        with col2:
            col2.markdown(
                f"""
                <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
                    <h3>Elissa Cusson, CEO & Programmer</h3>
                    <p>With an MSc in neuroscience and extensive experience as a consultant, I specialize in leveraging AI and machine learning to optimize market access, evidence value, and scientific research in healthcare. Passionate about advancing innovation, I apply my expertise to transform healthcare processes, making them more efficient and impactful. Outside of my professional work, I enjoy climbing and mountaineering, exploring the great outdoors and challenging myself with new summits.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    # with col2:
    #     st.markdown('''### Elissa Cusson, CEO & Programmer''')
    #     st.markdown('''With an MSc in neuroscience and extensive experience as a consultant, I specialize in leveraging AI and machine learning to optimize market access, evidence value, and scientific research in healthcare. Passionate about advancing innovation, I apply my expertise to transform healthcare processes, making them more efficient and impactful. Outside of my professional work, I enjoy climbing and mountaineering, exploring the great outdoors and challenging myself with new summits.''')


    ############################
    ### Jean-marc
    ############################

    image_jma_path = "MethodMINDpackage/deployment/images/JeanMarc.JPG"
    try:
        # Try to open the image
        image_jma = Image.open(image_jma_path)
        col1, col2 = st.columns([2, 1])  # Set the second column smaller than the second
        with col2:
            st.image(image_jma)
    except Exception:
        # If file not found, display a placeholder message
        col1, col2 = st.columns([2, 1])
        with col2:
            st.columns(3)[1].write('Image not found or cannot be opened.')

    with col1:
        st.markdown('''### Jean-Marc André, Programmer & System Administrator''')
        st.markdown('''With over 20 years leading a cybersecurity company, I’ve shifted my focus to artificial intelligence, specializing in RAG and vector database consultancy for SMEs. A lifelong tech enthusiast, I bring expertise spanning electronics, networks, systems, and the web, while also sharing my passion as a podcast producer. Beyond tech, I explore Europe in a campervan with my wife, embracing diverse cultures, cuisines, and stories to inspire innovation and connection.''')

    ############################
    ### Liam
    ############################

    image_lwc_path = "MethodMINDpackage/deployment/images/Liam.jpg"
    try:
        # Try to open the image
        image_lwc = Image.open(image_lwc_path)
        col1, col2 = st.columns([1, 2])  # Set the first column smaller than the second
        with col1:
            st.image(image_lwc)
    except Exception:
        # If file not found, display a placeholder message
        col1, col2 = st.columns([1, 2])
        with col1:
            st.columns(3)[1].write('Image not found or cannot be opened.')
    with col2:
        st.markdown('''### Liam , Programmer & Git Administrator''')
        st.markdown('''An ex-ski instructor who spent years traveling from cliff to cliff setting up highlines, walking, and doing tricks on them. He is curious and geeky, with a passion for learning about science, history, and anything that sparks interest. Now working in tech with a focus on machine learning engineering, he brings a keen eye for detail, ensures smooth team coordination, and focuses on the robustness of the development process. He’ll continue to keep things interesting with his great terrible jokes.''')

    ############################
    ### Jaime
    ############################

    # image_jpa_path = "MethodMINDpackage/deployment/images/jpa.jpg"
    # try:
    #     # Try to open the image
    #     image_jpa = Image.open(image_jpa_path)
    #     col1, col2 = st.columns([2, 1])  # Set the second column smaller than the second
    #     with col2:
    #         st.image(image_jpa)
    # except Exception:
    #     # If file not found, display a placeholder message
    #     col1, col2 = st.columns([2, 1])
    #     with col2:
    #         st.columns(3)[1].write('Image not found or cannot be opened.')

    with col1:
        st.markdown('''### Jaime, Programmer & Web Application Designer''')


#                                                    NAVIGATION

#navigation sidebar (left column)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Home", "Disclaimer", "About", "Team"])

if page == "Home":
    home_page()
elif page == "Disclaimer":
    disclaimer_page()
elif page == "About":
    about_page()
elif page == "Team":
    team_page()
