import numpy as np
from DetailedCompare.HR_o_matic import HR_A_Tron
ResNotSet = ValueError("Resume not set. Please set resmue at /set_resume/")

hr = HR_A_Tron()

#Todo: handle communication with a sql database.
class Applicant:
    def __init__(self, email : str, first=None, last=None, res=None):
        self.email = email
        self.first = first
        self.last = last
        self.res = res
        self.res_enc = None
        self.reslines = None
        self.reslines_enc = None
        self.negative_keywords = set({})
        self.positive_keywords = set({})

    def get_name(self):
        return self.first, self.last
    
    def get_negative_keywords(self):
        return self.negative_keywords
    
    def get_positive_keywords(self):
        return self.positive_keywords
    
    def add_positive_keyword(self, word):
        self.positive_keywords.update(word)

    def add_negative_keyword(self, word):
        self.negative_keywords.update(word)

#TODO: should res be its own class inheriting applicant? i.e:
#class Resume(Applicant):
    #def __init__(self, first, last, res):
#       super().__init__(first, last)
#        self.res = res
    
    def set_res(self, res:str):
        self.res = res
        #Reset values to null - repopulate when needed.
        self.res_enc = None
        self.reslines = None
        self.reslines_enc = None

    def get_res(self):
        if self.res is not None:
            return self.res
        else:
            raise ResNotSet    

    def get_res_enc(self):
        if self.res is None:
            raise ResNotSet
        elif self.res_enc is not None:
            return self.res_enc
        else:
            self.res_enc = hr.get_encoding(self.res)
            return self.res_enc
    
    def get_reslines(self):
        if self.res is None:
            raise ResNotSet
        else:
            reslines = hr.get_features(self.get_res())
            return reslines
    
    def get_reslines_enc(self):
        reslines = self.get_reslines()
        self.reslines = np.apply_along_axis(hr.model.encode, 0, reslines)
        return self.reslines