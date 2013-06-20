'''
Created on Jun 19, 2013

@author: ksahlin
'''

import os

import networkx as nx

from BESST import Contig, Scaffold
import smith_waterman

def reverse_complement(string):
    #rev_nuc = {'A':'T', 'C':'G', 'G':'C', 'T':'A', 'N':'N', 'X':'X'}
    # Modified for Abyss output
    rev_nuc = {'A':'T', 'C':'G', 'G':'C', 'T':'A', 'a':'t', 'c':'g', 'g':'c', 't':'a', 'N':'N', 'X':'X', 'n':'n', 'Y':'R', 'R':'Y', 'K':'M', 'M':'K', 'S':'S', 'W':'W', 'B':'V', 'V':'B', 'H':'D', 'D':'H', 'y':'r', 'r':'y', 'k':'m', 'm':'k', 's':'s', 'w':'w', 'b':'v', 'v':'b', 'h':'d', 'd':'h'}

    rev_comp = ''.join([rev_nuc[nucl] for nucl in reversed(string)])
    return(rev_comp)

def k_mer_graph_to_scaffold_graph(graph):
    ''' We want to make new contigs of the haplotypic regions that we have solved.
        The regions that we have solved are the ones where a node has precisely 
        one neighbor in the overlapping k-mer graph.
    
    '''

    new_contigs = nx.Graph()

    for edge in graph.edges_iter():
        try:
            graph.edge[edge[0]][edge[1]]['m']
            node = edge[0]
            nbr = edge[1]
        except KeyError:
            continue
        ##
        # Modulo 2 operator to see what contig end we should map to
        # Beginning and forward of contig, or end and reverse compl. -> "Left" side of contig
        # Othervise right side

        new_node1 = (node[0], 'L') if (node[1] + node[2]) % 2 == 0 else (node[0], 'R')
        new_node2 = (nbr[0], 'L') if (nbr[1] + nbr[2]) % 2 == 0 else (nbr[0], 'R')
        new_contigs.add_edge(new_node1, new_node2)
        other_side1 = (node[0], 'R') if (node[1] + node[2]) % 2 == 0 else (node[0], 'L')
        other_side2 = (nbr[0], 'R') if (nbr[1] + nbr[2]) % 2 == 0 else (nbr[0], 'L')
        new_contigs.add_edge(new_node1 , other_side1)
        new_contigs.add_edge(new_node2 , other_side2)

    print len(new_contigs.nodes())
    return(new_contigs)

def get_joined_sequence(contigs, sub_graph, start, end, k_mer_size):
    sequence = ''
    path = nx.algorithms.shortest_path(sub_graph, start, end)
    path_len = len(path)
    print 'Nr contigs in path:', path_len / 2.0

    index_to_remove = []
    for i, node in enumerate(path):
        if i % 2 == 0:
            try:
                contigs[node[0]]
            except KeyError:
                print 'Contig already removed. Number ' + str(i) + ' in path of length' + str(len(path))
                if i == 0 or i == len(path) - 2:# end contig. Just regular haplotype!
                    print 'End contig. Just regular haplotype! continue merging'
                    index_to_remove.append(i)
                    index_to_remove.append(i + 1)
                else:
                    return()
    for index in sorted(index_to_remove, reverse=True):
        del path[index]
    for i, node in enumerate(path):
        if i % 2 == 1 and i < path_len - 2:
            ctg1 = contigs[node[0]] if node[1] == 'R' else reverse_complement(contigs[node[0]])
            seq1 = ctg1[:k_mer_size - 1]
            if i == 1:
                sequence += ctg1

            ctg2 = contigs[path[i + 1][0]] if path[i + 1][1] == 'L' else reverse_complement(contigs[path[i + 1][0]])
            seq2 = ctg2[:k_mer_size - 1]
            score, max_i, max_j, traceback_matrix = smith_waterman.SW(seq1, seq2, 0, 0)
            neg_gap = min(max_i, max_j)
            sequence += ctg2[neg_gap:]
            # Remove the contigs that are included in a new contig so
            # that we don't print it out several times
            del contigs[node[0]]

    return(sequence)

def print_out_contigs(contigs, new_contigs, output_dir, k_mer_size):
    contigs_out = open(os.path.join(output_dir, 'BESST_contigs.fa'), 'w')

    contig_index = 0

    for component in nx.connected_component_subgraphs(new_contigs):
        contig_index += 1
        accession = '>BESST_ctg' + str(contig_index)

        for node in component:
            if len(new_contigs.neighbors(node)) == 1:
                start = node
                break
        for node in component:
            if len(new_contigs.neighbors(node)) == 1 and node != start:
                end = node
                break
        ctg_seq = get_joined_sequence(contigs, component, start, end, k_mer_size)
        if ctg_seq:
            print >> contigs_out, accession + '\n' + ctg_seq




    # Print out remaining contigs (the ones that has not been 
    # removed as haplotypes or merged into bigger contigs)
    print len(contigs)
    cntru = 0
    for acc, sequence in contigs.items():
        cntru += 1
        print >> contigs_out, '>' + acc + '\n' + sequence
        print cntru

    return()

def generate_fasta(graph, contigs, output_dir, k_mer_size):

    haplotypes = open(os.path.join(output_dir, 'haplotypes.fa'), 'w')
    nodes_to_remove = set()
    haplotype_count = 0
    for node in graph:
        if graph.node[node]['r']:
            nodes_to_remove.add(node)
            print 'remove'

    graph.remove_nodes_from(nodes_to_remove)
    for node in nodes_to_remove:
        # remove the nodes from the contig dictionary as well
        # so that we do not print them out among the new contigs.
        try:
            print >> haplotypes, '>' + node[0].strip() + '\n' + contigs[node[0]]
            del contigs[node[0]]
            haplotype_count += 1
        except KeyError:
            pass

    print 'Number of haplotypes removed:', haplotype_count

    new_contigs = k_mer_graph_to_scaffold_graph(graph)
    print_out_contigs(contigs, new_contigs, output_dir, k_mer_size)

    #print len(nx.connected_components(graph))

    #for component in nx.connected_components(graph):
    #    pass

#        try:
#            graph.edge[edge[0]][edge[1]]['m']
#            print 'merge'
#        except KeyError:
#            pass

    return()
