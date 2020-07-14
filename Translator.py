def get_prefix(sent):
    return [""], sent


class Phrase():
    def __init__(self, sent, ngram_model):
        words = sent.split()
        self.words = words
        self.head = words[0]
        self.tail = words[-1]
        self.prop = 0
        if sent != "" and len(words) > 1:
            for i in range(1, len(words)):
                self.prop += ngram_model.get_prop(words[i - 1] + " " +
                                                  words[i])


"""
    beam search 实现
"""


class BeamStatus():
    def __init__(self, prefix, words, unvisited, prop, left):
        self.prefix = prefix
        self.words = words
        self.unvisited = unvisited
        self.prop = prop
        self.left = left


def update_beams(beams, phrase_table, ngram_model):
    unvisited = beams[0].unvisited
    prefix = beams[0].prefix
    left = beams[0].left
    words = beams[0].words
    prop = beams[0].prop
    for i, flag in enumerate(unvisited):
        if flag:
            new_unvisited = list(unvisited)
            new_unvisited[i] = False
            for phrase in phrase_table[i]:
                new_prefix = phrase.tail
                new_prop = prop + ngram_model.get_prop(
                    prefix + " " + phrase.head) + phrase.prop
                new_left = left - 1
                new_words = words + phrase.words
                beams.append(
                    BeamStatus(new_prefix, new_words, new_unvisited, new_prop,
                               new_left))
    beams.pop(0)


def beam_search(prefix, word_trans_table, ngram_model, k=5):
    word_num = len(word_trans_table)
    unvisited = [True for i in range(word_num)]
    beams = [BeamStatus(prefix[-1], [], unvisited, 0, word_num)]

    for i in range(word_num):
        while beams[0].left == word_num - i:
            update_beams(beams, word_trans_table, ngram_model)
        beams.sort(key=lambda s: s.prop)
        beams = beams[-1:-1 - k:-1]
    if prefix[-1] == "":
        return beams[0].words, beams[0].prop
    else:
        return prefix + beams[0].words, beams[0].prop


"""
    dp 实现
"""


def dp(prefix, word_trans_table, ngram_model):
    word_num = len(word_trans_table)
    choice_num = 0

    for phrases in word_trans_table:
        if choice_num < len(phrases):
            choice_num = len(phrases)

    dp_arr = [[[-1e6 for k in range(choice_num)] for j in range(word_num)]
              for i in range(1 << word_num)]

    #递推dp
    for status in range(1 << word_num):
        for j in range(word_num):
            if ((1 << j)) & status > 0:
                last_status = status - (1 << j)
                for k, phrase_cur in enumerate(word_trans_table[j]):
                    if last_status == 0:
                        trans_prop = ngram_model.get_prop(
                            phrase_cur.head) + phrase_cur.prop
                        dp_arr[status][j][k] = max(dp_arr[status][j][k],
                                                   trans_prop)
                    else:
                        for l in range(word_num):
                            if ((1 << l)) & last_status > 0:
                                for m, phrase_last in enumerate(
                                        word_trans_table[l]):
                                    trans_prop = dp_arr[last_status][l][
                                        m] + ngram_model.get_prop(
                                            phrase_last.tail + " " +
                                            phrase_cur.head) + phrase_cur.prop
                                    dp_arr[status][j][k] = max(
                                        dp_arr[status][j][k], trans_prop)

    return decode_dp_trans(dp_arr, prefix, word_trans_table, ngram_model)


def decode_dp_trans(dp_arr, prefix, word_trans_table, ngram_model):
    buffer = []

    word_num = len(word_trans_table)
    cur_prop = -1e7
    cur_status = (1 << word_num) - 1
    last_status = -1
    cur_phrase = None

    #初始化最大概率
    for i in range(word_num):
        for j in range(len(word_trans_table[i])):
            if dp_arr[cur_status][i][j] > cur_prop:
                cur_prop = dp_arr[cur_status][i][j]
                cur_phrase = word_trans_table[i][j]
                last_status = cur_status - (1 << i)
    buffer += cur_phrase.words[::-1]

    max_prop = cur_prop
    while last_status != 0:
        for last_word in range(word_num):
            if last_status & (1 << last_word) > 0:
                for last_choice in range(len(word_trans_table[last_word])):
                    last_phrase = word_trans_table[last_word][last_choice]
                    if dp_arr[last_status][last_word][
                            last_choice] + ngram_model.get_prop(
                                last_phrase.tail + " " +
                                cur_phrase.head) + cur_phrase.prop == cur_prop:
                        cur_status = last_status
                        cur_phrase = last_phrase
                        cur_prop = dp_arr[last_status][last_word][last_choice]
                        last_status = cur_status - (1 << last_word)
                        buffer += cur_phrase.words[::-1]
    if prefix[-1] != "":
        buffer += prefix[::-1]
    return buffer[::-1], max_prop


def baseline(prefix, word_trans_table):
    buffer = []
    if prefix[-1] != "":
        buffer = prefix
    for phrases in word_trans_table:
        buffer += phrases[0].words
    return buffer


class Translator():
    def __init__(self, segmentor, ngram_model, dictionary):
        self.segmentor = segmentor
        self.ngram_model = ngram_model
        self.dictionary = dictionary

    def translate(self, sent, seg_type='quick', trans_method='baseline'):
        prefix, filter_sent = get_prefix(sent)
        if seg_type == 'quick':
            words = self.segmentor.seg(filter_sent)

            #获取词翻译表
            word_trans_table = []
            for i, word in enumerate(words):
                explains = self.dictionary.explain(word)
                phrases = [
                    Phrase(explain, self.ngram_model) for explain in explains
                ]
                word_trans_table.append(phrases)

            #选择方法翻译
            trans_sent = ''
            if trans_method == 'beam_search':
                trans_sent, prop = beam_search(prefix, word_trans_table,
                                               self.ngram_model)
            elif trans_method == 'dp':
                trans_sent, prop = dp(prefix, word_trans_table,
                                      self.ngram_model)
            elif trans_method == 'baseline':
                trans_sent = baseline(prefix, word_trans_table)

            return ' '.join(trans_sent)

        elif seg_type == 'all':
            seg_list = self.segmentor.seg_all(filter_sent)
            results = []
            for words in seg_list:
                #获取词翻译表
                word_trans_table = []
                for i, word in enumerate(words):
                    explains = self.dictionary.explain(word)
                    phrases = [
                        Phrase(explain, self.ngram_model)
                        for explain in explains
                    ]
                    word_trans_table.append(phrases)

                trans_sent = ''
                prop = -1e7
                if trans_method == 'beam_search':
                    trans_sent, prop = beam_search(prefix, word_trans_table,
                                                   self.ngram_model)
                elif trans_method == 'dp':
                    trans_sent, prop = dp(prefix, word_trans_table,
                                          self.ngram_model)
                results.append((' '.join(trans_sent), prop))
            results.sort(key=lambda x: x[1])
            for trans_sent, prop in results[::-1]:
                print(trans_sent, prop)
            return results[::-1][0][0]
