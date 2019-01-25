from fcd.fcd import fcdet, fast_ccm
from sys import argv
from glob import glob
from itertools import product
from lingpy import *
from lingpy.evaluate.acd import *
import tqdm

if 'training' in argv:
    ngrams = [3, 4, 5]
    excludes = ['V_+', 'V_+T']
    ngram_gaps = [True, False]
    allngrams = [True, False]
    cuts = [1]
    models = ['sca', 'dolgo', 'asjp']
    gaps = [True, False]
    best = 0.0
    for ngram, exclude, ngram_gap, cut, model, gap, allngram in product(
            ngrams, excludes, ngram_gaps, cuts, models, gaps, allngrams):
        table = []
        for f in glob('data/training/*.csv'):
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
                    ref='autocog'
                    )
            p, r, fs = bcubes(wl, 'cogid', 'autocog', pprint=False)

            table += [[f[:-4], round(p, 2), round(r, 2), round(fs, 4)]]
        
        fs =  round(sum([line[3] for line in table]) / len(table), 4)
        if fs > best:
            best = fs
            star = '*'
        else:
            star = ' '

        print('{0:5} | {1} | {2:6} | {3:6} | {4:6} | {5:6} | {6:6} | {7:.2f} | {8:.2f} | {9:.4f} {10}'.format(
            exclude,
            ngram,
            str(ngram_gap),
            cut,
            model,
            str(gap),
            str(allngram),
            round(sum([line[1] for line in table]) / len(table), 2),
            round(sum([line[2] for line in table]) / len(table), 2),
            round(sum([line[3] for line in table]) / len(table), 4),
            star,
            ))
