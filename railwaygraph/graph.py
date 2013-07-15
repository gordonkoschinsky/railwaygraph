import copy


# TODO
# - Think about separating the switch positions to the layout module
#
# - Now, we know where each vertex has to be placed in the network diagram.
# The next step is to build wx widgets that represent the elements
#
#

import logging
import loggingextensions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("railway_graph.graph")


class VertexError(Exception):
    pass

class Vertex(object):
    """A vertex part of a "double vertex"
    """
    def __init__(self, name, element, pos_x, pos_y):
        """
        name: a descriptive name of the vertex
        element: the track element this vertex is part of
        pos_x, pos_y: The relative position of the vertex inside the element

        """
        self.name = name
        self.attributes = {}
        self.edges = []
        self.partner = None # the "partner" vertex
        self.element = element # the track element (switch, track etc) this vertex belongs to

        self.pos_x = pos_x # the relative position inside the track element
        self.pos_y = pos_y

    def addEdge(self, vertex):
        if vertex not in self.edges:
            logger.debugdeep("add edge {}-{}".format(self.name, vertex.name))
            self.edges.append(vertex)

    def connectedVertices(self):
        """returns all connected vertices
        """
        return self.edges

    def isEndVertex(self):
        """
        returns True if the vertex is an end vertex of the graph,
        i.e. it has no edges but a partner
        """
        if len(self.connectedVertices()) == 0 and self.partner:
            return True
        return False

    def __repr__(self):
        return "<Vertex {}>".format(self.name)


class Graph(object):
    """
    Graph class that supports double vertices for use in railway network
    computation, like described by Markus Montigel 1992

    Usage: While it's possible to add vertices with AddVertex() and edges with
    addEdge(), the most likely use case is the addition of whole track elements
    instances (subclasses of TrackElement) with the addElementGraph() method.
    Connect the elements out vertices (i.e., pair vertices to "double vertices")
    with connectVertices(), and finalize the graph with
    doubleAllSingleVertices().

    After that, the path finding method can be used.
    """
    def __init__(self):
        self.vertices = {}
        self.elements = {}

    def addVertex(self, vertex):
        if vertex in self.vertices:
            raise VertexError("Vertex {} already in Graph".format(vertex))

        self.vertices[vertex.name] = vertex
        self.elements[vertex.element.id] = vertex.element

        vertex.graph = self
        return vertex

    def addEdge(self, vertex_a, vertex_b):
        vertex_a.addEdge(vertex_b)
        vertex_b.addEdge(vertex_a)

    def addVerticesFrom(self, subgraph):
        for vertex in subgraph.vertices.itervalues():
            self.addVertex(vertex)

    def vertexByName(self, name):
        if name in self.vertices:
            return self.vertices[name]
        else:
            raise IndexError

    def elementById(self, id):
        if id in self.elements:
            return self.elements[id]
        else:
            raise IndexError

    def addElementGraph(self, element):
        """Add all vertices of the track element into
        this graph
        """
        self.addVerticesFrom(element.graph)

    def connectVertices(self, vertex_a, vertex_b):
        """Connect two vertices a and b to be a double vertex
        """
        if vertex_a.name not in self.vertices or vertex_b.name not in self.vertices:
            raise VertexError("Warning: At least one of the vertices {} and {} is not in the graph".format(vertex_a, vertex_b))
        if vertex_a.partner is not None or vertex_b.partner is not None:
            raise VertexError("Warning: At least one of the vertices {} and {} is already a double vertex".format(vertex_a, vertex_b))

        vertex_a.partner = vertex_b
        vertex_b.partner = vertex_a

    def doubleAllSingleVertices(self):
        """
        Find all vertices that are not mapped to a corresponding sibling, create
        an artifical sibling vertices an tie them together

        Note: Call after all track connecting work is done, because after this
        method has been called, all vertices will be double and no further connections
        can be made.
        """
        for vertex in self.vertices.values():
            if not vertex.partner:
                self.connectVertices(vertex, self.addVertex(Vertex("{}_*".format(vertex.name), vertex.element, vertex.pos_x, vertex.pos_y)))

    def getAllElements(self):
        """returns a dict of all TrackElement instances in the graph
        """
        return self.elements.values()

    def copy(self):
        """ Returns a deep copy of the graph
        """
        return copy.deepcopy(self)

    def findPath(self, startVertex, endVertex):
        def findPathR(p, v_end):
            v_last = p[-1]
            logger.trace("------------------")
            logger.trace(v_last.name)
            if v_last.attributes["mark"] == "NotOK" \
                            or v_last.partner.attributes["mark"] != "Unknown":
                return
            if v_last==v_end:
                v_last.attributes["mark"] = "OK"
                solutions.append(p)
                logger.trace("found solution: {}".format(map(lambda x: x.name,p)))
                return
            if v_last.attributes["mark"] == "Unknown":
                v_last.attributes["mark"] = "NotOK"
                found_path = False
                logger.trace("connected to the partner {} of {} are:".format(v_last.partner.name, v_last.name))
                for v_connected in v_last.partner.connectedVertices():
                    logger.trace(v_connected.name)
                    findPathR(p + [v_connected], v_end)
                    if v_connected.attributes["mark"] == "OK":
                        found_path = True
                if found_path:
                    v_last.attributes["mark"] = "OK"
            else:
                for v_connected in v_last.partner.connectedVertices():
                    logger.trace(v_connected.name)
                    findPathR(p + [v_connected], v_end)


        G = self.copy()

        for vertex in G.vertices.itervalues():
            vertex.attributes["mark"] = "Unknown"

        solutions = []
        findPathR([G.vertexByName(startVertex)], G.vertexByName(endVertex))
        return solutions


class TrackElement(object):
    """A generic track element. An element represents a set of vertices
    connected by edges.
    """
    def __init__(self, id):
        self.id = id
        self.type = "generic"
        self.vertices = {}

        # SUBGRAPH
        self.graph = Graph()


    def getDefaultVertex(self):
        """return a Vertex instance that can be used by layout algorithmns as
        the first Vertex of the track element to be layouted.
        By convention, the outmost upper left vertex, called "A"
        """
        return self.vertices['a']

    def __repr__(self):
        return "<{} {}>".format(self.type, self.id)


class Track(TrackElement):
    """A simple track, consisting of two vertices connect by an edge.
    """
    def __init__(self, id):
        TrackElement.__init__(self, id)
        self.type = "track"
        self.vertices['a'] = Vertex("{}_A".format(self.id), self, 0, 0)
        self.vertices['b'] = Vertex("{}_B".format(self.id), self, 1, 0)

        # SUBGRAPH
        self.graph.addVertex(self.vertices['a'])
        self.graph.addVertex(self.vertices['b'])
        self.graph.addEdge(self.vertices['a'], self.vertices['b'])

class Switch(TrackElement):
    """A switch track element, consisting of three vertices of which two are
    connected to the third one.
    """
    def __init__(self, id, orientation):
        """
        orientation: how the legs of the switch are oriented. Describes the
        position of the connecting vertex on the railway diagramm:
        ul = upper left
        ur = upper right
        ll = lower left
        lr = lower right
        """
        TrackElement.__init__(self, id)
        vertex_pos = {}
        vertex_pos['a'] = (0,0)
        if orientation == "ul":
            vertex_pos['b'] = (1,0)
            vertex_pos['c'] = (1,1)
            self.type = "switch_ul"
        elif orientation == "ur":
            vertex_pos['b'] = (-1,0)
            vertex_pos['c'] = (-1,1)
            self.type = "switch_ur"
        elif orientation == "ll":
            vertex_pos['b'] = (1,0)
            vertex_pos['c'] = (1,-1)
            self.type = "switch_ll"
        elif orientation == "lr":
            vertex_pos['b'] = (-1,0)
            vertex_pos['c'] = (-1,-1)
            self.type = "switch_lr"

        self.vertices['a'] = Vertex("{}_A".format(self.id), self, *vertex_pos['a'])
        self.vertices['b'] = Vertex("{}_B".format(self.id), self, *vertex_pos['b'])
        self.vertices['c'] = Vertex("{}_C".format(self.id), self, *vertex_pos['c'])

        # SUBGRAPH
        self.graph.addVertex(self.vertices['a'])
        self.graph.addVertex(self.vertices['b'])
        self.graph.addVertex(self.vertices['c'])
        self.graph.addEdge(self.vertices['a'], self.vertices['b'])
        self.graph.addEdge(self.vertices['a'], self.vertices['c'])
