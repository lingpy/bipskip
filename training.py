from bipskip.bipskip import fcdet, fast_ccm, make_skips
from sys import argv
from glob import glob
from itertools import product
from lingpy import *
from lingpy.evaluate.acd import *
import tqdm
from tabulate import tabulate
from lingpy.convert.strings import write_nexus

ngrams = [3, 4, 5, 2, 6]
excludes = ['_+', '_+T', 'V_+T', 'V_+']
ngram_gaps = [True, False]
allngrams = [True, False]
cuts = [0.2, 0.4][::-1]
models = [['sca'], ['asjp'], ['sca', 'asjp'], ['sca', 'dolgo'], ['asjp',
    'dolgo'], ['asjp', 'dolgo', 'sca'] ][::-1]
prosodys = [False]
gaps = [True, False]
best = 0.0
methods = [
        'infomap', #'multilevel', 
        'cc']

if 'sea' in argv:
    files = [x for x in glob('data/training/*.csv') if 'SIN' in x or 'BAI' in
            x]
    f = open('training-sea.txt', 'w').close()
    myfile = open('training-sea.txt', 'a')
else: #'sea' in argv:
    files = [x for x in glob('data/training/*.csv') if not 'SIN' in x and not 'BAI' in
            x]
    f = open('training-non-sea.txt', 'w').close()
    myfile = open('training-non-sea.txt', 'a')

print(files)


for ngram, exclude, ngram_gap, cut, model, gap, allngram, prosody, method in product(
        ngrams, excludes, ngram_gaps, cuts, models, gaps, allngrams, prosodys,
        methods):
    table = []

    for f in files: #glob('data/*.csv'):
        wl = Wordlist(f)
        if not 'tokens' in wl.header:
            wl.add_entries('tokens', 'ipa', ipa2tokens)

        fcdet(
                wl, 
                exclude=exclude,
                ngrams=ngram,
                ngram_gaps=ngram_gap,
                cut=cut,
                model=model,
                gaps=gap,
                all_ngrams=allngram,
                ref='autocog',
                method=method,
                prosody=prosody
                )
        p, r, fs = bcubes(wl, 'cogid', 'autocog', pprint=False)

        table += [[f[:-4], round(p, 2), round(r, 2), round(fs, 4)]]
    
    fs =  round(sum([line[3] for line in table]) / len(table), 4)
    if fs > best:
        best = fs
        star = '*'
    else:
        star = ' '

    text = '{0:5} |ng {1} |ngg {2:6} | {3:6} | {4:6} |g {5:6} |a {6:6} |p {7:6} | {8:.2f} | {9:.2f} | {10:.4f} | {11:10} {12}'.format(
        exclude,
        ngram,
        str(ngram_gap),
        cut,
        '/'.join(model),
        str(gap),
        str(allngram),
        str(prosody),
        round(sum([line[1] for line in table]) / len(table), 2),
        round(sum([line[2] for line in table]) / len(table), 2),
        round(sum([line[3] for line in table]) / len(table), 4),
        method,
        star,
        )
    print(text)
    myfile.write('\t'.join([x.strip() for x in text.split('|')])+'\n')
myfile.close()


