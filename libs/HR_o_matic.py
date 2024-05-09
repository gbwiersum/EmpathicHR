# todo: if cuda is available, use cupy for dot products
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import warnings
import os
np.random.seed(42069)
warnings.filterwarnings('ignore')


def get_features(doc, line_size=10):
    # todo: replace pandas with numpy
    split = doc.split("\n")
    if len(split)<10:
        split = doc.split(".")
    doc = pd.Series(split)
    doc = doc.apply(lambda x: x.replace("  ", ""))
    doc = doc[(doc.apply(lambda x: len(x.split()) > line_size))]
    return doc


class HR_A_Tron:

    def __init__(self, model='all-mpnet-base-v2', chunk_size=0, lex_size=1500):
        self.model = SentenceTransformer(model)
        self.lex_size = lex_size
        if chunk_size == 0:
            self.chunk_size = self.model.get_sentence_embedding_dimension() // 2
        else:
            self.chunk_size = chunk_size
        self.res = None

    def set_model(self, model_name):
        self.model = SentenceTransformer(model_name)

    def get_encoding(self, indoc, chunk_size=380):
        text = indoc.split("\n")
        outdoc = [' '.join(text[i:i + chunk_size]) for i in range(0, len(text), chunk_size)]
        x = self.model.encode(outdoc[0])
        for line in outdoc[1::]:
            x = np.hstack((x, self.model.encode(line)))
        return x

    def score(self, description, res):
        if type(description) is str:
            a = self.model.encode(description)
            t = self.model.encode(res)
            score = np.dot(a,t)
        else:
            a = description.map(self.model.encode)
            t = self.model.encode(res)
            score = a.apply(lambda x: np.dot(x, t))
        return score

    def feature_analysis(self, res, doc):

        reslines = get_features(res)
        doclines = get_features(doc)

        res_tokens = np.apply_along_axis(self.model.encode, 0, reslines)
        doc_tokens = np.apply_along_axis(self.model.encode, 0, doclines)

        match_matrix = np.apply_along_axis(lambda x: np.apply_along_axis(lambda y: np.dot(x, y), 1, doc_tokens), 1,
                                           res_tokens)

        renamer = np.vectorize(lambda x: " ".join(x.split()[0:5]) + "...")
        reslines = renamer(reslines)
        doclines = renamer(doclines)

        match_matrix = pd.DataFrame(match_matrix, index=reslines, columns=doclines)
        return match_matrix

    def plot_compare(self, matrix):
        import matplotlib.pyplot as plt
        import seaborn as sns
        f, ax = plt.subplots(nrows=3, ncols=1, figsize=(6, 24))
        for axis in [0, 1]:
            dat = matrix.sum(axis=axis).sort_values(ascending=False)
            y = dat.index
            x = dat.values
            sns.barplot(x=x, y=y, ax=ax[axis])
            ax[axis].set(xlabel="Relative Match")
            sns.despine(left=True, bottom=True)

        sns.heatmap(matrix, cmap="jet", ax=ax[2])
        return f

        #plt.show()


