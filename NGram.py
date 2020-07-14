class NGram():
    def __init__(self, file):
        self.biterm_prop = {}
        with open(file, 'rt', encoding='utf-8') as fin:
            while True:
                line = fin.readline()
                if not line:
                    break
                line = line[:-1]
                elems = line.split()
                prop = float(elems[-1])
                biterm = ' '.join(elems[:-1])
                self.biterm_prop[biterm] = prop

    def get_prop(self, biterm):
        if biterm in self.biterm_prop.keys():
            return self.biterm_prop[biterm]
        return -6