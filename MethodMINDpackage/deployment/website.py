import streamlit as st
from PIL import Image
from MethodMINDpackage.orchestraDitector.LLM import llm_test
from MethodMINDpackage.train.PubMed import get_pubmed_data
from MethodMINDpackage.deployment.firewall import firewall


st.set_page_config(layout="wide")

def home_page():
    #home page

    #displaying logo at the center

    #absolute path from my computer, may not work on other computers!!!!!
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
    #st.columns(3)[1].title("Welcome to MethodMIND")

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
        it's magic!
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

    with st.spinner('Loading... Please wait'):
        #getting PubMed keywords
        df = get_pubmed_data()

    #request
    text_input = st.text_area('Type your request here:')

    #loading spinner
    if st.button('Submit'):

        stopped_by_firewall = False
        done_processing = False
        with st.spinner('Processing... Please wait'):

            #loading progress
            with st.empty():
                bar = st.progress(0)

                #here we do the task
                is_valid = firewall(text_input, df)
                if is_valid:
                    # with st.empty():
                    #     st.write('running LLM...')
                    bar.progress(25)



                    #insert other procedures here



                    #testing llm
                    output = llm_test(text_input)
                    done_processing = True
                else:
                    #in case there are other types of errors
                    stopped_by_firewall = True


                bar.progress(100)

        #displaying output
        if done_processing:
            st.markdown(f"""<div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px;">{output}</div>""", unsafe_allow_html=True)

            abstracts = '''insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts
            insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts
            insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts insert abstracts '''
            st.write('###')

            #displaying abstracts
            st.markdown('### Abstracts:')
            st.markdown(f"""<div style="border: 2px solid white; padding: 10px; border-radius: 5px;">{abstracts}</div>""", unsafe_allow_html=True)

        #if request is outside of scope
        elif stopped_by_firewall:
            st.write('The request is outside of the scope of the model. Please try again with another request.')

    #disclaimer
    #st.caption('MethodMIND can make mistakes. Please check important information')
    st.markdown("""
        <p style="text-align: center; font-size: 18px; color: gray;">
            <strong>MethodMIND can make mistakes. Please check important information carefully.</strong>
        </p>
    """, unsafe_allow_html=True)

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

def about_page():
    #about page

    st.title('About us')
    st.markdown("Elissa is our one and only leader. That's all you need to know")
    st.markdown('''
        ## Credits
        insert credits
    ''')


#navigation sidebar (left column)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Home", "Disclaimer", "About"])

if page == "Home":
    home_page()
elif page == "Disclaimer":
    disclaimer_page()
elif page == "About":
    about_page()
