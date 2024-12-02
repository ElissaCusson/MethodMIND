import streamlit as st
from PIL import Image
from MethodMINDpackage.orchestraDitector.LLM import llm_test
from MethodMINDpackage.orchestraDitector.retrival import search_similarity, query_by_id, get_abstract_by_doi, handle_multiple_similarities, handle_multiple_metadata
from MethodMINDpackage.deployment.firewall import firewall_all_keywords

st.set_page_config(layout="wide")

#                                                  TO DO

#code for number of abstracts
#add emoji/gif while loading
#explain how it works


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



#############################################################################################################
        # #hard coded
#        similarity = search_similarity(text_input)
 #       ids = handle_multiple_similarities(similarity[0][0])
  #      metadata_list = query_by_id(ids)
   #     metadata_dict = handle_multiple_metadata(metadata_list[0])
    #    dois = set(metadata_dict['doi'])
     #   abstract_by_doi = get_abstract_by_doi(dois= dois)[0]                              #####
#############################################################################################################

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
                similarity = search_similarity(text_input)

                #verify similarity step
                if similarity[1] is False:
                    stopped_at_similarity = True
                    done_processing = False
                    id = 0
                else:
                    id = similarity[0][0][0].id

                progress_text.text('Fetching DOI information...🎣')
                progress_bar.progress(25)

                #important data here
                doi_from_ID = query_by_id(id)

                #verify query by id step
                if doi_from_ID[1] is False:
                    stopped_at_query_by_id = True
                    done_processing = False
                    doi = ''
                else:
                    doi = doi_from_ID[0][0]['doi']

                progress_text.text('Retrieving abstracts...🛒')
                progress_bar.progress(40)

                abstract_by_doi = get_abstract_by_doi(doi= doi)[0]

                #verify abstract by doi step
                if abstract_by_doi[1] is False:
                    stopped_at_abstract_by_doi = True
                    done_processing = False

                progress_text.text('Generating answer...🚀')
                progress_bar.progress(55)

                #testing llm
                output = llm_test(text_input)

                #full text input for llm
                full_text_input = f'''Based on the following abstracts, {text_input} \n\n Abstracts: \n {abstract_by_doi}'''

                # #full llm
                #output = llm_test(full_text_input)

            else:
                #in case there are other types of errors
                stopped_by_firewall = True

            progress_text.text('Done ✅')
            progress_bar.progress(100)

        #                                               OUTPUT

        if done_processing:
            #results output
            st.markdown(f"""<div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px;">{output}</div>""", unsafe_allow_html=True)


            #abstracts output
            abstract_title = doi_from_ID[0][0]['title']
            full_text_link = doi_from_ID[0][0]['full_text_link']

            #FOR MULTIPLE ABSTRACTS
            abstracts_list = [
                {"title": "Abstract 1", "link": "https://example.com/1"},
                {"title": "Abstract 2", "link": "https://example.com/2"},
                {"title": "Abstract 3", "link": "https://example.com/3"},
            ]

            # Generate the HTML for multiple abstracts
            abstracts = ""
            for abstract in abstracts_list:
                abstracts += f'''
                            {abstract["title"]}:
                            <a href="{abstract["link"]}" target="_blank" style="color: yellow;">{abstract["link"]}</a><br><br>
                        '''

            #FOR 1 ABSTRACT!
            abstracts = f'''
                {abstract_title}:
                <a href="{full_text_link}" target="_blank" style="color: yellow;">{full_text_link}</a><br><br>
            '''

            st.write('###')

            #displaying abstracts
            st.markdown('### Abstracts:')
            st.markdown(f"""<div style="border: 2px solid white; padding: 10px; border-radius: 5px;">{abstracts}</div>""", unsafe_allow_html=True)

        #if request is outside of scope
        elif stopped_by_firewall:
            st.subheader('The request is outside of the scope of the model. Please try again with another request.')

        #if stopped at similarity step
        elif stopped_at_similarity:
            st.subheader(similarity[2])

        #if stopped at query by id step
        elif stopped_at_query_by_id:
            st.subheader(doi_from_ID[2])

        #if stopped at abstract by doi
        elif stopped_at_abstract_by_doi:
            st.subheader(abstract_by_doi[2])

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
