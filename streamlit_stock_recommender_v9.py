
# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, cross_val_predict
from sklearn.model_selection import cross_validate
import seaborn as sns
from IPython.display import display
import sklearn.datasets
#import classifier models
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier

#import model eval tools
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import accuracy_score,recall_score, precision_score, f1_score, plot_confusion_matrix, roc_auc_score, recall_score
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score,plot_confusion_matrix
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.inspection import permutation_importance



import streamlit as st
import altair as alt
import streamlit.components.v1 as components
import shap
shap.initjs()
import eli5
from eli5.formatters import format_as_dataframe, format_as_dataframes

# Format page layout
st.set_page_config(layout="wide")
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {4}rem;
        padding-right: {5}rem;
        padding-left: {5}rem;
        padding-bottom: {10}rem;
    }} </style> """, unsafe_allow_html=True)

# set header for the app
col1, mid, col2 = st.columns([3,0.5,2])
with col1:
    st.title("Personalized Stock Recommender System 🚀")
    st.subheader("Welcome to our stock recommender system!")

with col2:
    st.image(
                "https://media3.giphy.com/media/S4178TW2Rm1LW/giphy.gif","From GIPHY",
                width=200, # Manually Adjust the width of the image as per requirement
            )



# read parquet file
def read_parquet(file):
    parquet_file = pd.read_parquet(file, engine='pyarrow')
    return parquet_file

#Hide menu button
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# define header/subheader/texts in different color, make it more obvious
def userguide(url):
    st.markdown(f'<p style=color:Grey;font-size:14px;border-radius:2%;">{url}</p>',
                unsafe_allow_html=True)

def partseparate(url):
    st.markdown(f'<p style=color:Orange;font-size:35px;border-radius:2%;">{url}</p>',
                unsafe_allow_html=True)
def section_title(url):
    st.markdown(f'<p style=color:Black;font-size:25px;border-radius:2%;">{url}</p>',
                unsafe_allow_html=True)


### Part 0 Preparation: Give high-level introduction
partseparate("Introduction to The System")
with st.expander("Discover the system and how it works...", expanded=True):
    st.markdown('''This app is designed to provide portfolio managers with both buy and sell recommendations based on their current portfolios.  
                Personalized recommendations are generated by analyzing the financial ratios that the portfolio manager prioritizes within their current portfolio, 
                developing a scoring system around this analysis, and then attaching assigned scores to each of these stocks, as well as the stocks in the PM’s watchlist.''')
    st.markdown("__Steps:__")
    st.markdown('''1️⃣ Upload your portfolio and watchlist.''')
    st.markdown('''2️⃣ Explore top Buy and Sell recommendations in Part II Section A.''')
    st.markdown('''3️⃣ Explore explanations for individual Buy or Sell Recommendations in Part II Section B.''')
    st.markdown('''4️⃣ Understand the financial ratios that the portfolio prioritizes as a whole in Part II Section C.''')
    st.markdown('''5️⃣ Lastly, Explore the stock universe using some extra functions provided in Part III.''')
# Ask user to upload file
section_title("Upload Your Stock Dataset")
# with st.expander("instruction", expanded=False):
st.markdown('''Please upload your portfolio and watchlist. This dataset should be formatted as a parquet file.
            Please confirm the stock ticker/id column is named “entity_id” and indicate whether the stock is currently held or not using the following labeling convention in a column named "target":''')
st.markdown('''           
            __• “1” for owned__\n
            __• “0” for NOT owned in a column labeled as “target”__''')
st.markdown('''Include as many financial ratios as you'd like (Minimum of 10).''')
st.markdown(
        "**Download [a sample data here](https://github.com/JessieTao98/Capstone-Project/raw/3abbab999505ecf886d94adaf6fcfb16b782318c/export-Global%20Equity-08-31.parquet)! ** ")

#this instruction can be prompt as a error alert if the user apload n unqualified file.
# Load data
# st.warning(
#     """
#     ✏️ **NOTE: Please read the instruction before uploading your file, make sure you get a qualified file.**
# """
# )
parquet_file = st.file_uploader("",help="This dataset should be formatted as a parquet file. The stock ticker/id column should be named “entity_id” and whether the stock is currently held or not should be labeled as a “1” for owned and “0” for NOT owned in a column labeled “target”", type=['parquet'])

if parquet_file is not None:
    # store data in session state
    if parquet_file:
        if 'read_parquet' in st.session_state:
            df = st.session_state.read_parquet
        else:
            df = read_parquet(parquet_file)
            st.session_state.read_parquet = df
        userguide(parquet_file.name + ' is loaded successfully')
        st.markdown("Preview of Stock Universe:") # st.markdown("_**Preview of the dataset:**_")
        st.write(df)

        ### Part 1 Core of the system-recommendation and explaination
        st.markdown("____")
        partseparate("II. Stocks Recommendations")
## Sec 1: Show buy and sell recommendations separately
        st.write("")
        section_title("A. Top Buy & Sell Recommendations") #section_title("A. Algorithm Generated Top Sell & Buy Recommendations")
        # build model
        df_new = st.session_state.read_parquet.copy()
        y = df_new['target']
        X = df_new.drop(columns=['target'], axis=1)
        # split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        RF_clf = RandomForestClassifier(max_depth = 3, random_state=12, class_weight='balanced')
        clf = RF_clf.fit(X,y)

        # make predictions
        class_probabilitiesDec = clf.predict_proba(X)
        prob0list = []
        prob1list = []
        for i in range(len(df)):
            prob0 = class_probabilitiesDec[i][0]
            prob1 = class_probabilitiesDec[i][1]
            prob0list.append(prob0)
            prob1list.append(prob1)
        # add probabilities to df
        df_new['Sell_Score'] = prob0list
        df_new['Buy_Score'] = prob1list
        with st.expander("Instructions:", expanded=True):
            st.markdown(
            """
                • The recommendations are sorted by the scores provided by the app’s algorithm.\n
                • Please see the recommendations below. You can adjust the number of recommendations using the +/- box below.\n
                • Please note: the Buy recommendations are for stocks that are NOT currently owned by the portfolio manager, while the Sell Recommendations are for stocks that are currently owned.  This system is purely for long investing, no short selling is recommended.\n 
            """)

        with st.expander("How are these scores generated?", expanded=True):
            st.markdown(
            """
                The app considers each of the stocks that are held by the portfolio manager and ranks the importance of each of the financial ratio metrics.
                It is capable of distinguishing your preference in each of the financial ratios values.  i.e. the algorithm will be able to understand if your portfolio favors a large gross margin ratio or a low pay out ratio.  These ranked financial ratios each provide a contribution to the Buy or Sell score.  These contributions are referred to as SHAP values trhoughout the app and either add value or subtract value to the stocks Buy or Sell scores.  
                Specific breakdowns of each score on the recommendation lists can be found in the following section.
            """)

        col1,col2 = st.columns(2)
        with col1:
            choose_n_of_stock = st.number_input("Enter the Number of Stocks Recommendations You'd Like To See:", min_value=1, max_value=40, value=10, step=5)
            choose_n_of_stock = int(choose_n_of_stock)
        col1,col2 = st.columns(2)
        with col1:
            with st.expander("Buying Recommendations", expanded=False):
                # TOP 10 buy
                df_result_buy10 = df_new[df_new['target'] == 0].sort_values('Buy_Score',
                                                                             ascending=False).head(choose_n_of_stock).reset_index()
                st.table(df_result_buy10.iloc[:,[0,-3,-1]])
        with col2:
            with st.expander("Selling Recommendations", expanded=False):
                # TOP 10 sell
                df_result_sell10 = df_new[df_new['target'] == 1].sort_values('Sell_Score',
                                                                              ascending=False).head(choose_n_of_stock).reset_index()
                st.table(df_result_sell10.iloc[:,[0,-3,-2]])



## Sec 2: Be able to explain each stock Buy/Sell
        st.write("")
        section_title("B. Explanation of Individual Stock Buy/Sell Recommendation")

        with st.expander("Instructions:", expanded=True):
            st.markdown(
            """
                Please select individual stocks from the recommendation lists to see a detailed explanation for each recommendation score.  The Buy and Sell scores are generated by adding all of the financial ratio SHAP values (positive or negative contributions of each financial ratio).  The scores for each financial ratio are calculated by analyzing the importance of each ratio according to the positions held in the current portfolio. 
            """)

        # st.warning(
        #     """
        #     ✏️ **NOTE: To Change the number of stock recommendations, go back to section A and reselect the number.
        #     The Recommendations table is the same as in section A.**
        # """
        # )

        col1, col2 = st.columns(2)
        with col1:
            # TOP 10 buy
            with st.expander("Explanations for Buying Recommendations: ", expanded=False):
                df_results = df_new.sort_values('Buy_Score', ascending=False).reset_index()
                df_result_buy10 = df_new[df_new['target'] == 0].sort_values('Buy_Score',ascending=False).head(choose_n_of_stock).reset_index()
                buy_10_id = df_result_buy10['entity_id']
                choose_buy = st.selectbox('Select Stock: ', buy_10_id)
                st.write("The Stock You Selected is:  ", choose_buy)
                choose_buy_idx = df_results.index[df_results['entity_id'] == choose_buy][0]
                # feature score for all features on one prediction

                original_title = '<p style=" color:Black; font-size: 16px;' \
                                 '">Ranked Importance for each financial ratio on buying prediction:</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                # choose_buy_index = df_result_buy10.index[df_result_buy10['entity_id'] == choose_buy]
                # feature_pred = eli5.show_prediction(clf, df_result_buy10[list(X.columns)].iloc[choose_buy_index],
                #                                     feature_names=list(X_train.columns), show_feature_values=True)
                # feature_pred = feature_pred.data.replace("\n", "")
                # st.markdown(feature_pred, unsafe_allow_html=True)
                explainer = shap.TreeExplainer(clf)
                shap_values = explainer.shap_values(X)

                class ShapObject:
                    def __init__(self, base_values, data, values, feature_names):
                        self.base_values = base_values  # Single value
                        self.data = data  # Raw feature values for 1 row of data
                        self.values = values  # SHAP values for the same row of data
                        self.feature_names = feature_names  # Column names
                df_results.set_index('entity_id', inplace=True)
                # st.write(explainer.shap_values(df_results))
                shap_object = ShapObject(base_values=explainer.expected_value[1],
                                         values=explainer.shap_values(df_results)[1][int(choose_buy_idx)][:-3],
                                         feature_names=df_results.columns[:-3],
                                         data=df_results.iloc[int(choose_buy_idx)][:-3])
                fig, ax = plt.subplots()
                ax = shap.waterfall_plot(shap_object, max_display=12)
                st.pyplot(fig)


            # top 10 sell
            with st.expander("Explanations for Selling Recommendations: ", expanded=False):
                df_results = df_new.sort_values('Sell_Score', ascending=False).reset_index()
                df_result_sell10 = df_new[df_new['target'] == 1].sort_values('Sell_Score',
                                                                    ascending=False).head(choose_n_of_stock).reset_index()
                # st.table(df_result_buy10.iloc[:,[0,-3,-1]])
                sell_10_id = df_result_sell10['entity_id']
                choose_sell = st.selectbox('Select the Stock You Are interested: ', sell_10_id)
                st.write("The Stock You Selected is:  ", choose_sell)
                choose_sell_idx = df_results.index[df_results['entity_id'] == choose_sell][0]
                # feature score for all features on one prediction

                original_title = '<p style=" color:Black; font-size: 16px;' \
                                 '">Ranked Importance for each financial ratio on selling prediction:</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                df_results.set_index('entity_id', inplace=True)
                # st.write(explainer.shap_values(df_results))

                shap_object = ShapObject(base_values=explainer.expected_value[0],
                                         values=explainer.shap_values(df_results)[0][int(choose_sell_idx)][:-3],
                                         feature_names=df_results.columns[:-3],
                                         data=df_results.iloc[int(choose_sell_idx)][:-3])

                fig, ax = plt.subplots()
                ax = shap.waterfall_plot(shap_object, max_display=12)
                st.pyplot(fig)


            with col2:
                with st.expander("Financial Ratio Importance Visuals", expanded = False):
                    class_selector = st.selectbox("Select Buying or Selling Group: ( 0 as Sell, 1 as Buy )", pd.unique(y.values))
                    feature_selector = st.selectbox("Select the Ratio You'd Like to Explore:", X.columns)
                    #interaction_selector = st.selectbox("Interaction feature: ", X.columns)

                    explainer = shap.TreeExplainer(clf)
                    shap_values = explainer.shap_values(X)
                    # dependence plot
                    cmap = plt.get_cmap("Dark2")
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    st.pyplot(shap.dependence_plot(feature_selector, shap_values[class_selector], X,
                                                   #interaction_index=interaction_selector,
                                                   interaction_index=None,
                                                   x_jitter=0.95,
                                                   alpha=0.68,
                                                   dot_size=12,
                                                   color=cmap.colors[0]))

## Sec 3: Algorithm Generated Top Feature Importance
        st.write("")
        section_title("C. Portfolio Financial Ratio Importance 🤖") #section_title("C. Algorithm Generated Top Feature Importance 🤖")
        with st.expander("How to Interpret the Plots in this Section", expanded=True):
            st.markdown('''
                        This plot describes the importance of each financial ratio for the entire model. The horizontal axis represents the SHAP value (contribution to Buy or Sell Score). The vertical axis is the list of all the financial ratios.
                        Each dot represents a stock of the stock universe.  The color of the dots on the plot show the value of each financial ratio.  If the dot is red, the stock has a higher value for the specific ratio.  If the dot is blue, stock has a lower value for the specific ratio. 
                        ''')

            st.markdown('''
                        Main picture:\n
                        For each financial ratio:\n
                        • If the dots are RED and clustered towards the RIGHT (positive values on horizontal axis), it means that the ratio is favored to be LARGER and has a positive impact on the score.  The further the dots trend to the right, the greater contribution to the recommendation score.\n 
                        • If the dots are BLUE and clustered towards the RIGHT, it means that the ratio is favored to be SMALLER and has a positive impact on the score.  The further the dots trend to the right, the greater contribution to the recommendation score.\n
                        Vice versa for when the dots trend to the left (negative side of the horizontal axis):\n
                        • If the dots are RED and clustered towards the LEFT, it means that when the ratio is LARGER it has a NEGATIVE impact on the score.  The further the dots trend to the left, the lower the recommendation score.\n   
                        • If the dots are BLUE and clustered towards the LEFT, it means that when the ratio is SMALLER it has a NEGATIVE impact on the score.  The further the dots trend to the left, the lower the recommendation score.\n 
                        ''')


        col1, col2 = st.columns([2, 2])
        #plots
        # X = df_new.drop(columns=['target', 'Sell_Score','Buy_Score'])
        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X)
        with col1:
            with st.expander("Graph on how financial ratios contribute to Buy Score ", expanded=False):
                original_title = '<p style="color:Black; font-size: 18px;">Impact of financial ratios on Buy Score</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                st.pyplot(shap.summary_plot(shap_values[1], X))

        # plots
        with col2:
            with st.expander("Graph on how financial ratios contribute to Sell Score ", expanded=False):
                original_title = '<p style="color:Black; font-size: 18px;">Impact of financial ratios on Sell Score</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                st.pyplot(shap.summary_plot(shap_values[0], X))


### Part 2 Some other functions available
# The below several functions is not relate to the main purpose, just use to explore the original dataset,
        # should be added after the core as subparts
        st.markdown("____")
        partseparate("III. Explore the original dataset")
        st.write("")
        section_title("A. Overall Stock Universe Description")
        with st.expander("Number of Stocks Owned VS NOT Owned", expanded=False):
            df_own = st.session_state.read_parquet[st.session_state.read_parquet['target'] == 1]
            df_market = st.session_state.read_parquet[st.session_state.read_parquet['target'] == 0]
            portfolio = pd.DataFrame({'Portfolio':['Number of Stocks Owned','Number of Stocks NOT Owned'],
                                      'Number of Stocks':[len(df_own),len(df_market)]})
            Chart = (alt.Chart(portfolio).mark_bar().encode(x='Portfolio', y='Number of Stocks').properties(
                width=300, height=500))

            col1, col2= st.columns([2,2])
            with col1:
                st.write(portfolio)
            with col2:
                st.altair_chart(Chart)

        with st.expander("Your current holding position ", expanded=False):
            st.write(df_own)

        st.write("")
        section_title("B. Individual Stock Lookup")
        with st.expander("Explore individual stocks", expanded=False):
            stock_index = st.session_state.read_parquet.reset_index()['entity_id']
            choose_stock = st.selectbox('Select the Stock You are interested: ', stock_index)
            st.write('Features of The Stock: ', choose_stock)
            st.table(st.session_state.read_parquet.loc[choose_stock])

        st.write("")
        section_title("C. Sort Stocks By Features")
        all_feature = st.session_state.read_parquet.columns
        choose_feature = st.multiselect('Select One or Multiple Feature(s) You Are interested: ',list(all_feature))
        if choose_feature != []:
            col1,col2 = st.columns(2)
            with col1:
                n_stocks = st.number_input("Number of Stocks You Want to Explore:", min_value=1, max_value=1240, value=10, step=5)
            with st.expander("Top Stocks From Your Choice of Feature (Sorted In Descending Order)", expanded=False):
                df_by_feature_top10 = st.session_state.read_parquet.sort_values(choose_feature,ascending=False).head(int(n_stocks))
                # original_title = '<p style=" color:Black; font-size: 18px;' \
                #                  '">Top stocks sorted based on chosen features in Descending Order: </p>'
                # st.markdown(original_title, unsafe_allow_html=True)
                st.write(df_by_feature_top10[choose_feature])
            with st.expander("Bottom Stocks From Your Choice of Feature (Sorted In Descending Order)", expanded=False):
                df_by_feature_bottom10 = st.session_state.read_parquet.sort_values(choose_feature, ascending=True).head(int(n_stocks))
                # original_title = '<p style="color:Black; font-size: 18px;' \
                #                  '">Bottom stocks sorted based on chosen features in Descending Order: </p>'
                # st.markdown(original_title, unsafe_allow_html=True)
                st.write(df_by_feature_bottom10[choose_feature])







