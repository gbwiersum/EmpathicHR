import streamlit as st
import warnings
import numpy as np
import re
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
np.random.seed(42069)
warnings.filterwarnings('ignore')
LEX_SIZE = 1500
LINE_SIZE = 10
BASE_MODEL = 'sentence-transformers/all-mpnet-base-v2'


@st.cache_resource
def get_model(modelname = "all-mpnet-base-v2"):
    model = SentenceTransformer(modelname)
    return model


if __name__=="__main__":
    model = get_model()

    detailed = st.form("Detailed Compare")
    detailed.subheader("Detailed Document Comparison")

    res = detailed.text_input("Resume", key="doc1")
    res_enc = model.encode(res)
    

    desc = detailed.text_input("Job Description", key="doc2")
    desc_enc = model.encode(desc)
    

    submit = detailed.form_submit_button("Compare Documents")

    if submit:

        def get_features(doc, line_size=10):
            doc = doc.replace("\n", " ")
            doclines = re.split(r"[!\?\.]", (doc.replace("\n", " ")))
            
            outlines = []
            for b in doclines:
                if len(b.split(" "))>=10:
                    outlines.append(b)
                else:
                    outlines[-1]+=" "+b
            
            doclines = outlines
            doc_tokens = np.apply_along_axis(model.encode, 0, doclines)
            return doclines, doc_tokens
        
        score = np.dot(res_enc, desc_enc)
        reslines, res_tokens = get_features(res)
        doclines, doc_tokens = get_features(desc)

        matrix = np.apply_along_axis(
            lambda x: np.apply_along_axis(
                lambda y: np.dot(x, y),
                1, doc_tokens),
            1, res_tokens)

        renamer = np.vectorize(lambda x: " ".join(x.split()[0:5]) + "...")
        reslines = renamer(reslines)
        doclines = renamer(doclines)

        f, ax = plt.subplots(nrows=3, ncols=1, figsize=(6, 24))

        ax[0].barh(y = reslines, width = matrix.sum(axis=1))
        ax[1].barh(y = doclines, width = matrix.sum(axis=0))

        ax[2].imshow(matrix, cmap="hot")
        ax[2].set_xticks(np.arange(len(doclines)), doclines)
        ax[2].set_yticks(np.arange(len(reslines)), reslines)
        plt.setp(ax[2].get_xticklabels(), rotation=45, ha="right",
                rotation_mode="anchor")

        st.subheader(f"Overall Score: {score}", )
        st.subheader("Line-Wise Breakdown")
        st.pyplot(f)


