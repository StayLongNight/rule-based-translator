class Dictionary():
    def __init__(self, file):
        self.explain_dict = {}
        with open(file, 'rt', encoding='utf-8') as fin:
            while True:
                line = fin.readline()
                if not line:
                    break
                line = line[:-1]
                cn = line.split()[0]
                en_list = line.split('\t')[1].split('/')[1:-1]
                en_list = [
                    word.lower() for word in en_list if word.find("(") == -1
                ]
                self.explain_dict[cn] = en_list

    def explain(self, word):
        return self.explain_dict[word]

    def exists(self, word):
        if word in self.explain_dict.keys():
            return True
        return False