import re

filter_regex = r'[^\u4E00-\u9FA5]'


def dfs(u, graph, n, sent, segs, seg_list):
    if u == n:
        seg_list.append(list(segs))
        return
    for v in range(u + 1, n + 1):
        if graph[u][v] == 1:
            segs.append(sent[u:v])
            dfs(v, graph, n, sent, segs, seg_list)
            segs.pop()


class Segmentor():
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def seg(self, sent):
        filter_sent = re.sub(filter_regex, '', sent)
        sent_len = len(filter_sent)
        begin = 0
        segs = []
        while begin != sent_len:
            end = sent_len
            while end != begin:
                word = filter_sent[begin:end]
                if self.dictionary.exists(word):
                    segs.append(word)
                    begin = end
                    break
                end -= 1
        return segs

    def seg_all(self, sent):
        filter_sent = re.sub(filter_regex, '', sent)
        sent_len = len(filter_sent)
        graph = [[0 for j in range(sent_len + 1)] for i in range(sent_len + 1)]
        for i in range(sent_len):
            for j in range(i + 1, sent_len + 1):
                word = filter_sent[i:j]
                if self.dictionary.exists(word):
                    graph[i][j] = 1
        seg_list = []
        dfs(0, graph, sent_len, filter_sent, [], seg_list)
        return seg_list
