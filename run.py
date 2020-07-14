from Dictionary import Dictionary
from Segmentor import Segmentor
from NGram import NGram
from Translator import Translator

output_file = "data/dp_result"


def read_data(file):
    datasets = []
    with open(file, 'rt', encoding='utf-8') as fin:
        while True:
            line = fin.readline()
            if not line:
                break
            elems = line[:-1].split("\t")
            en = elems[1]
            cn = elems[2]
            datasets.append((cn, en))
    return datasets


def write_result(y_preds, datasets, file):
    with open(file, 'wt', encoding='utf-8') as fout:
        for y_pred, data in zip(y_preds, datasets):
            print(data[0], file=fout)
            print(data[1], file=fout)
            print(y_pred, file=fout)


if __name__ == '__main__':
    datasets = read_data('data/English-Chinese.txt')
    dictionary = Dictionary('data/ldc_cedict.utf8')
    seg = Segmentor(dictionary)
    ngram_model = NGram('lm/log_prob.dat')
    translator = Translator(seg, ngram_model, dictionary)
    print(translator.translate("好好学习",seg_type="all",trans_method="dp"))
    y_preds = []
    '''
    rnd = 0
    for x, y in datasets:
        y_pred = translator.translate(x,
                                      seg_type="all",
                                      trans_method="dp")
        y_preds.append(y_pred)
        rnd += 1
        print(rnd)
        if rnd == 200:
            break
    write_result(y_preds, datasets, output_file)
    '''
