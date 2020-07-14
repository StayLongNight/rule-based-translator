import math
import re
lm_count_file = 'lm/bigram_EN.dat'
prob_file = 'lm/log_prob.dat'


def read_bigram_count(file):
    bigram_cnt = {}
    not_word_regex = r'[^0-9a-zA-Z\'\" ]'
    with open(file, 'rt', encoding='utf-8') as fin:
        while True:
            line = fin.readline()
            if not line:
                break
            line = line[:-1]
            elems = [word.strip() for word in line.split()]
            cnt = int(elems[0])
            if cnt < 40:
                break
            str_expr = ' '.join(elems[1:])
            if re.search(not_word_regex, str_expr) is not None:
                continue
            bigram_cnt[str_expr] = cnt
    return bigram_cnt


def cal_log_prob(bigram_cnt):
    ucnt, bicnt = 0, 0
    bigram_prob = {}
    for bigram_term in bigram_cnt.keys():
        words = bigram_term.split()
        if len(words) == 1:
            ucnt += bigram_cnt[bigram_term]
        elif len(words) == 2:
            bicnt += bigram_cnt[bigram_term]
            if words[0] not in bigram_cnt.keys():
                continue
            if bigram_cnt[bigram_term] / bigram_cnt[words[0]] > 1:
                continue
            bigram_prob[bigram_term] = math.log10(bigram_cnt[bigram_term] /
                                                  bigram_cnt[words[0]])

    for bigram_term in bigram_cnt.keys():
        words = bigram_term.split()
        if len(words) == 1:
            bigram_prob[bigram_term] = math.log10(bigram_cnt[bigram_term] /
                                                  ucnt)
    return bigram_prob


def save_prob(bigram_prob, file):
    prob_list = [item for item in bigram_prob.items()]
    prob_list.sort(key=lambda x: x[1])
    with open(file, 'wt', encoding='utf-8') as fout:
        for item, prob in prob_list[::-1]:
            print(item, prob, sep='\t', file=fout)


bigram_cnt = read_bigram_count(lm_count_file)
bigram_prob = cal_log_prob(bigram_cnt)
save_prob(bigram_prob, prob_file)