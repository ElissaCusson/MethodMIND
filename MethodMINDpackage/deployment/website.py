import streamlit as st
from PIL import Image
st.set_page_config(layout="wide")

def home_page():
    #home page

    #displaying logo at the center

    abs_path = "/home/jplanaslee/code/jplanaslee2/MethodMIND/logo.png"
    image = Image.open(abs_path)
    st.columns(3)[1].image(image)

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
    expander.write('''
        explaining how it works
    ''')

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

    #request
    text_input = st.text_area('Type your request here:')

    #loading spinner
    if st.button('Submit'):
        with st.spinner('Processing... Please wait'):

            #loading progress
            with st.empty():
                bar = st.progress(0)

                #here we do the task
                task(text_input)
                #task 2 : bar.progress(50), etc.

                bar.progress(100)

    #disclaimer
    #st.caption('MethodMIND can make mistakes. Please check important information')
    st.markdown("""
        <p style="text-align: center; font-size: 18px; color: gray;">
            <strong>MethodMIND can make mistakes. Please check important information carefully.</strong>
        </p>
    """, unsafe_allow_html=True)




def help_page():
    #help page

    st.title('Help')
    st.write('##')

    help_input = st.text_area('What can I help you with?')
    if st.button('Submit'):
        st.write("We haven't implemented this part yet")

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

def task(input):
    pass


#navigation sidebar (left column)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Home", "Help", "Disclaimer", "About"])

if page == "Home":
    home_page()
elif page == "Help":
    help_page()
elif page == "Disclaimer":
    disclaimer_page()
elif page == "About":
    about_page()
