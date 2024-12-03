import streamlit as st
from PIL import Image
from MethodMINDpackage.orchestraDitector.LLM import llm_test
from MethodMINDpackage.orchestraDitector.retrival import search_similarity, query_by_id, get_abstract_by_doi, handle_multiple_similarities, handle_multiple_metadata
from MethodMINDpackage.deployment.firewall import firewall_all_keywords
from MethodMINDpackage.orchestraDitector.reranking import reranking

st.set_page_config(layout="wide")

#                                                  TO DO

#code for number of abstracts
#add emoji/gif while loading
#explain how it works
#remove duplicates /set


#                                                   HOME

def home_page():
    #home page

    #displaying logo at the center

    image_path = "MethodMINDpackage/deployment/images/logo.png"
    try:
        # Try to open the image
        image = Image.open(image_path)
        st.columns(3)[1].image(image)
    except Exception as e:
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
        Our platform helps researchers like you find the most relevant and up-to-date methods for proving your hypothesis.
        Simply enter your research question or hypothesis, and our model will search through a vast database of PubMed
        abstracts, pinpointing studies and methodologies most related to your query.

        Instead of spending hours reading all the different abstracts to find a solution, start by submitting your
        hypothesis, and let us do the rest!
        ''')


    #space
    st.write('##')

    #explaining how it works
    expander = st.expander("How it works:")
    expander.write("""
        we'll implement this last
    """)

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
        st.markdown('<div class="container-border">Which methods can I use to measure tremor decrease and gait improvement in Parkinson patients receiving deep brain stimulation?</div>', unsafe_allow_html=True)

    # Second column with a container and border
    with columns[1]:
        st.markdown('<div class="container-border">Which methods can I use to measure migraine pain intensity?</div>', unsafe_allow_html=True)

    #space
    st.write('###')

    #number of abstracts
    slider_values = [5, 7, 10, 15, 20, 30]
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

                # #hard coded
                similarity = search_similarity(text_input, k = 30)

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

                #testing llm
                output = llm_test(text_input)

                #final list of dictionaries
                final_form = reranked

                #full text input for llm
                #make abstracts in sequence
                abstracts_in_sequence = ''
                for a in final_form:
                    abstracts_in_sequence += f'\n\n{a["abstract"]}'

                #full text input
                full_text_input = f'''Based on the following abstracts, {text_input} \n\n Abstracts: {abstracts_in_sequence}'''

                #full llm
                output = llm_test(full_text_input)

            else:
                #in case there are other types of errors
                stopped_by_firewall = True


            progress_bar.progress(100)

        #                                               OUTPUT

        if done_processing:

            progress_text.text('Done ✅')

            #results output
            st.markdown(f"""<div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px;">{output}</div>""", unsafe_allow_html=True)

            # For multiple abstracts
            abstracts_list = []

            for abs in final_form:
                dictionary = {}
                dictionary['title'] = abs.get('title')
                dictionary['link'] = abs.get('link')
                dictionary['date'] = abs.get('date')
                abstracts_list.append(dictionary)


            # Generate the HTML for multiple abstracts
            abstracts_html = "".join([
                f'''<strong>{abstract["title"]}</strong>
                <span style="font-style: italic; color: #aaa;">({abstract["date"]})</span>:
                <a href="{abstract["link"]}" target="_blank" style="color: yellow; text-decoration: none; word-wrap: break-word;">{abstract["link"]}</a>
                <br><br>'''
                for abstract in abstracts_list
            ])

            st.write('###')

            #displaying abstracts
            st.markdown('### Abstracts:')
            st.markdown(f"""<div style="border: 2px solid white; padding: 10px; border-radius: 5px;">{abstracts_html}</div>""", unsafe_allow_html=True)

        #if request is outside of scope
        elif stopped_by_firewall:
            st.subheader('The request is outside of the scope of the model. Please try again with another request.')

        #if stopped at similarity step
        elif stopped_at_similarity:
            st.subheader(similarity[2])

        #if stopped at query by id step
        elif stopped_at_query_by_id:
            st.subheader(metadata_list[2])

        #if stopped at abstract by doi
        elif stopped_at_abstract_by_doi:
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

#                                                      ABOUT

def about_page():
    #about page

    st.title('About us')
    st.markdown("Elissa is our one and only leader. That's all you need to know")
    st.markdown('''
        ## Credits
        insert credits
    ''')

#                                                    NAVIGATION

#navigation sidebar (left column)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Home", "Disclaimer", "About"])

if page == "Home":
    home_page()
elif page == "Disclaimer":
    disclaimer_page()
elif page == "About":
    about_page()
