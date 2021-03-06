# -*- coding: utf-8 -*-
"""Additional methods used for features
"""

import nltk
import re


def tokenize(string):
    # Used when tokenizing words
    sentence_re = r'''(?x)      # set flag to allow verbose regexps
          (?:[A-Z])(?:\.[A-Z])+\.?  # abbreviations, e.g. U.S.A.
        | \w+(?:-\w+)*            # words with optional internal hyphens
        | \$?\d+(?:\.\d+)?%?      # currency and percentages, e.g. $12.40, 82%
        | \.\.\.                # ellipsis
        | [][.,;"'?():-_`]      # these are separate tokens
    '''
    return nltk.regexp_tokenize(string, sentence_re)


class Holder:
    """
    Holds a word or words for future pattern-finding
    """
    def __init__(self, text, index, is_kw=False, is_score=False):
        self.text = text
        self.pos = index
        self.is_score = is_score
        self.is_kw = is_kw


def fill_blanks(kws, sentence):
    new_kws = []
    for kw in kws:
        if kw not in sentence:
            words = kw.split()
            start_ix = sentence.index(words[0])
            end_ix = sentence.index(words[-1]) + len(words[-1])
            kw = sentence[start_ix:end_ix]
        new_kws.append(kw)
    return new_kws


def load(sentence, kws, score):
    """
    Fills list of Holder objects for finding patterns
    """
    kws = [kw.rstrip().lstrip() for kw in kws]
    kws = fill_blanks(kws, sentence)
    hs = []
    for kw in kws:
        try:
            hs.append(Holder(kw, sentence.index(kw), True))
        except ValueError:
            # print 'INDEX OF',re.sub('[\W_]+', ' ',kw),'IN',re.sub('[\W_]+', ' ', sentence)
            hs.append(Holder(kw, re.sub('[\W_]+', ' ', sentence).index(re.sub('[\W_]+', ' ', kw)), True))
    hs.append(Holder(score, sentence.index(score), False, True))
    hs.sort(key=lambda x: x.pos)
    pos = 0
    fillers = []

    for h in hs:
        if h.pos > pos:
            t = sentence[pos:h.pos]
            if any([x.isalpha() for x in t]):
                fillers.append(Holder(t, sentence.index(t)))
        pos = h.pos + len(h.text)
    hs += fillers
    hs.sort(key=lambda x: x.pos)
    return hs


def patterns(hs, subject):
    """
    Finds match-score patterns of type:
    A_score_B
    A_B_score
    where A or B is subject
    :param subject: subject
    :param hs: list of Holders
    :return: 0 if no pattern was found, 1 if subject is A, -1 if B
    """
    kw = [h.is_kw for h in hs]
    score = [h.is_score for h in hs]
    s_ix = score.index(True)
    try:
        if kw[s_ix - 1] and kw[s_ix + 1]:
            if hs[s_ix - 1].text in subject or subject in hs[s_ix - 1].text:
                return 1
            elif hs[s_ix + 1].text in subject or subject in hs[s_ix + 1].text:
                return -1
            return 0
    except IndexError:
        pass

    k = []
    for i in range(s_ix - 1, -1, -1):
        if not hs[i].is_kw:
            continue
        k.append(hs[i])

    if k[0].text in subject or subject in k[0].text:
        return -1
    elif k[1].text in subject or subject in k[1].text:
        return 1
    return 0


def patterns_string(sentence, subject, score, kws):
    for kw in kws:
        if subject in kw:
            subject = kw
    s_ix = sentence.index(score)
    su_ix = sentence.index(subject)
    if s_ix > su_ix:
        if s_ix <= su_ix + len(subject) + 2:
            return 1
    else:
        if su_ix <= s_ix + len(score) + 2:
            return -1
    return 0


if __name__ == '__main__':
#    sent = 'The buildup to Super Bowl XLIX may have been dominated by talk of deflated footballs but the denouement was anything but flat as the New England Patriots held off the Seattle Seahawks to win 28-24 in Phoenix.'
#    kws = ['New England Patriots', 'Super Bowl XLIX', 'Seattle Seahawks']
#    score = '28-24'
#    hs = load(sent, kws, score)
#    print patterns(hs, 'New England Patriots')
    print patterns_string('asdh kuk 3-2 buk asdaf', 'kuk', '3-2')
