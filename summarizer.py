#!/usr/bin/python
import nltk
import itertools
import sys
import getopt
import networkx as nx
import io

def dameraulevenshtein(seq1, seq2):
    """Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.
    """

    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]

def buildGraph(nodes):
    gr = nx.Graph()
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes,2))
    for pair in nodePairs:
        sentence1 = pair[0]
        sentence2 = pair[1]
        levDistance = dameraulevenshtein(sentence1, sentence2)
        gr.add_edge(sentence1,sentence2, weight = levDistance)
    return gr

def tokenize_sentence(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    graph = buildGraph(sentenceTokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    #most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    #return a 100 word summary
    summary = ' '.join(sentences)
    summaryWords = summary.split()
    summaryWords = summaryWords[0:101]
    summary = ' '.join(summaryWords)
    return summary

def main(argv):
    inputfile=''
    outputfile=''
    if len(sys.argv) < 2:
        print 'summarizer.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'summarizer.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'summarizer.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print 'Reading input file\n'
    rFile = io.open(inputfile,'r')
    text = rFile.read()
    summary = tokenize_sentence(text)

    print 'Saving Summary'
    sFile = io.open(outputfile,'w')
    sFile.write(summary)
    sFile.close()

if __name__ == '__main__':
    main(sys.argv[1:])
