from graph import Track, Switch, Graph

def simpleGraph():
    #
    #  1_A --- 1_B/3_A --- 3_B/3_B_*
    #                  \
    #                   \
    #                    3_C/2_A --- 2_B/2_B_*
    #
    track1 = Track(1)
    elements = [track1, Track(2), Switch(3, "ul")]

    G = Graph()

    for el in elements:
        G.addElementGraph(el)

    # connect the track elements
    G.connectVertices(G.vertexByName("1_B"), G.vertexByName("3_A"))
    G.connectVertices(G.vertexByName("3_C"), G.vertexByName("2_A"))

    # make the remaining single vertices to double vertices (all endpoints of the net)
    G.doubleAllSingleVertices()

    return G

def simpleExample():
    G = simpleGraph()

    G.findPath("1_A_*", "3_B")

def mediumGraph():
    #
    #  4_A_*/4_A --- 4_B/1_B --- 1_A/3_A --- 3_B/7_B -------------- 7_A/8_A --- 8_B/8_B_*
    #                          /         \                       /
    #                        /            \                    /
    #                   1_C                3_C             7_C
    #                  5_C                  6_C           2_C
    #                /                       \           /
    #              /                          \         /
    #  5_A_*/5_A --- 5_B/6_B ---------------- 6_A/2_A --- 2_B/2_B_*
    #

    track4 = Track(4)

    switch5 = Switch(5,"ll")

    switch6 = Switch(6,"lr")

    switch7 = Switch(7,"ur")

    elements = [Switch(1, "ur"), Switch(2,"ll"), Switch(3,"ul"), track4, switch5, switch6, switch7, Track(8)]

    G = Graph()

    for el in elements:
        G.addElementGraph(el)

    # connect the track elements
    G.connectVertices(G.vertexByName("4_B"), G.vertexByName("1_B"))
    G.connectVertices(G.vertexByName("1_C"), G.vertexByName("5_C"))
    G.connectVertices(G.vertexByName("1_A"), G.vertexByName("3_A"))
    G.connectVertices(G.vertexByName("5_B"), G.vertexByName("6_B"))
    G.connectVertices(G.vertexByName("3_B"), G.vertexByName("7_B"))
    G.connectVertices(G.vertexByName("3_C"), G.vertexByName("6_C"))
    G.connectVertices(G.vertexByName("6_A"), G.vertexByName("2_A"))
    G.connectVertices(G.vertexByName("2_C"), G.vertexByName("7_C"))
    G.connectVertices(G.vertexByName("7_A"), G.vertexByName("8_A"))


    # make the remaining single vertices to double vertices (all endpoints of the net)
    G.doubleAllSingleVertices()

    return G

def mediumExample():
    G = mediumGraph()

    print G.findPath("4_A_*", "8_B")
    print G.findPath("4_A_*", "5_B")
    print G.findPath("5_A_*", "5_B")

if __name__ == '__main__':
    #simpleExample()
    mediumExample()
