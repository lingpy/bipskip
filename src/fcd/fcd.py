from lingpy import *
import networkx as nx
from lingpy import basictypes as bt
from lingpy.sequence.sound_classes import get_all_ngrams
import igraph
from lingpy.convert.graph import networkx2igraph
from networkx.algorithms.bipartite import *
import tqdm

def to_ccm(tokens):
    cv = tokens2class(tokens, 'cv')
    cl = tokens2class(tokens, 'dolgo')
    dolgo = ''
    if cv[0] == 'V': 
        dolgo += 'H'
    else:
        dolgo += cl[0]
    for c, v in zip(cv[1:], cl[1:]):
        if c == 'C':
            dolgo += v
    if len(dolgo) == 1:
        dolgo += 'H'
    return dolgo[:2]


def fast_ccm(wordlist, ref='ccmid'):

    wl.add_entries('cog', 'tokens,concept', lambda x, y:
            x[y[1]]+'-'+to_ccm(x[y[0]]))
    wl.renumber('cog', ref, override=True)


def retrieve_all_ngrams(sequence, n):
    """Compute a couple of different grams of a sequence.
    potentially obsolete
    """
    out = set()
    for subs in get_all_ngrams(sequence):
        if len(subs) >= n+1:
            for i in range(n+1):
                out.add(''.join(subs[:i]+subs[i+1:n+1]))
        if len(subs) >= n:
            out.add(''.join(subs[:n]))
    return out


def get_ngrams(sequence, n, gaps=True, ngram_gaps=True):
    """Get all ngrams fulfilling the criterion and potentially add gaps"""
    out = set()
    for i, segment in enumerate(sequence):
        seq = ''.join(sequence[i:i+n])
        if len(seq) == n:
            out.add(seq)
            if ngram_gaps:
                for j in range(n):
                    out.add(seq[:j]+'-'+seq[j+1:])
                    out.add(seq[:j]+'-'+seq[j:-1])
    return sorted(out)


def add_gaps(sequence):
    sequence = bt.strings(sequence)
    out = [''.join(sequence)]
    for i in range(len(sequence)):
        # add a gap at any point
        out += [''.join(sequence[:i] + ['-'] + sequence[i:])]
        # gap any segment
        out += [''.join(sequence[:i] + ['-'] + sequence[i+1:])]
    return sorted(out, key=lambda x: str(x))


def make_graph(
        wordlist, 
        segments='tokens', 
        exclude='T_V+',
        ngrams=3,
        gaps=True,
        cut=2,
        ngram_gaps=True,
        model='sca',
        all_ngrams=True
        ):
    G = nx.Graph()
    for idx, language, word, concept in wordlist.iter_rows(
            'doculect',
            segments,
            'concept'
            ):
        # exclude chars from the string
        classes = [x for x, y in zip(
            tokens2class(word, model=model),
            tokens2class(word, model='cv')) if y not in
                exclude]

        # TODO think of controling for sound classes of less than n characters
        G.add_node(idx, ntype=1, language=language, concept=concept, word=word)
        class_string = ''.join(classes)
        if classes not in G:
            G.add_node(concept+'/'+class_string, ntype=2)
        G.add_edge(idx, concept+'/'+class_string)

        # this part needs to be refined, to make it more reasonable: compute a
        # certain amount of skip-grams etc., but not in this messy fashion
        forms = set()
        if gaps:
            for form in add_gaps(classes):
                forms.add(form)
                forms.add(form+'-') # control for small forms

        if all_ngrams:
            for form in retrieve_all_ngrams(classes, ngrams):
                forms.add(form)
                forms.add(form+'-')

        if ngrams:
            for form in get_ngrams(classes, ngrams, ngram_gaps=ngram_gaps): 
                forms.add(form)
                forms.add(form+'-')

        for form in forms:
            if concept+'/'+form not in G:
                G.add_node(concept+'/'+form, ntype=2)
            G.add_edge(idx, concept+'/'+form)
            
    if cut: 
        for node, data in list(G.nodes(data=True)):
            if data['ntype'] == 2:
                if len(G[node]) == cut:
                    G.remove_node(node)
    return G


def get_cognates(wordlist, graph, ref='fcdid', method='cc'):
    cogs = {}
    if method == 'cc':
        for i, comp in enumerate(nx.connected_components(graph)):
            nodes = [n for n in comp if graph.node[n]['ntype'] == 1]
            for node in nodes:
                cogs[node] = i+1
        wordlist.add_entries(ref, cogs, lambda x: x)
    else:
        projected = weighted_projected_graph(graph, {n for n in graph if
            graph.node[n]['ntype'] == 1}, ratio=True)
        #for concept in wordlist.rows:
        for concept, component in enumerate(nx.connected_components(projected)):
            #subgraph = nx.subgraph(projected, {n for n in wordlist.get_list(
            #    row=concept, flat=True)})
            subgraph = nx.subgraph(projected, component)
            if subgraph.edges:
                graph_new = networkx2igraph(subgraph)
                if method == 'infomap':
                    clust = graph_new.community_infomap(edge_weights='weight')
                elif method == 'multilevel':
                    clust = graph_new.community_multilevel(weights='weight')
                for i, comp in enumerate(clust):
                    for node in comp:
                        cogs[graph_new.vs[node]["Name"]] = str(i+1)+'-'+str(concept)
            else:
                for i, idx in enumerate(component): 
                    cogs[idx] = str(i+1)+str(concept)
                #for i, idx in enumerate(wordlist.get_list(row=concept, flat=True)):
                #    cogs[idx] = str(i+1)+'-'+str(concept)
        wordlist.add_entries('dummy', cogs, lambda x: x)
        wordlist.renumber('dummy', ref)


def fcdet(wordlist, 
        ref='fcdid',
        segments='tokens',
        exclude='T_V+',
        ngrams=3,
        gaps=True,
        cut=1,
        ngram_gaps=True,
        model='asjp',
        all_ngrams=True,
        method='cc'
        ):
    """Get cognates from this method"""
    graph = make_graph(
            wordlist, 
            segments=segments, 
            exclude=exclude,
            ngrams=ngrams,
            gaps=gaps,
            cut=cut,
            ngram_gaps=ngram_gaps,
            model=model,
            all_ngrams=all_ngrams)

    get_cognates(wordlist, graph, ref=ref, method=method)

