"""Manipulate Venmo JSON mesages and analyze the resultant graph object."""
import time
import calendar
from collections import deque


class _Vertex(object):
    """Track connected vertices and corresponding edge weights."""

    __slots__ = ('_neighbors')

    def __init__(self):
        """Instantiate vertex:weight dictionary."""
        self._neighbors = {}

    @property
    def degree(self):
        """Return degree of vertex object."""
        return len(self._neighbors)

    def add_neighbor(self, node):
        """Add edge or increment edge weight."""
        self._neighbors[node] = self._neighbors.get(node, 0) + 1

    def remove_neighbor(self, node):
        """Decrement edge weight and remove if weight == 0."""
        self._neighbors[node] -= 1

        if not self._neighbors[node]:
            del self._neighbors[node]


class _Graph(object):
    """Manipulate set of vertices and calulate median vertix degree."""

    __slots__ = ('_vertices', '_degreesDesc')

    def __init__(self, nodes):
        """Instantiate vertex dict and descending degrees list."""
        self._vertices = {}
        self._degreesDesc = []

        self.add_degrees(nodes)

    @property
    def median(self):
        """Return median vertex degree."""
        n = len(self._vertices)
        median = self._degreesDesc[n // 2]

        if not n % 2:
            median = round((median + self._degreesDesc[n//2 - 1]) / 2.0, 2)

        return median

    def _add_edge(self, nodes):
        """Add vertices or increment edge weights."""
        for i in (0, 1):
            self._vertices.setdefault(nodes[i], _Vertex()).add_neighbor(
                nodes[(i + 1) % 2])

    def _remove_edge(self, nodes):
        """Decrement edge weights and remove vertices if degree == 0."""
        for i in (0, 1):
            self._vertices[nodes[i]].remove_neighbor(nodes[(i + 1) % 2])

            if not self._vertices[nodes[i]].degree:
                del self._vertices[nodes[i]]

    def add_degrees(self, nodes):
        """Add edges and update degree list."""
        degrees = {}
        for node in nodes:
            if node in self._vertices:
                degrees[node] = self._vertices[node].degree
            else:
                self._degreesDesc.append(1)

        self._add_edge(nodes)

        for item in degrees.items():
            if item[1] != self._vertices[item[0]].degree:
                self._degreesDesc[self._degreesDesc.index(item[1])] += 1

    def remove_degrees(self, nodes):
        """Remove edges and update degree list."""
        degrees = {node: self._vertices[node].degree for node in nodes}

        self._remove_edge(nodes)

        for node in nodes:
            if node not in self._vertices:
                self._degreesDesc.pop()
            elif degrees[node] != self._vertices[node].degree:
                self._degreesDesc[
                    self._degreesDesc.index(degrees[node]) +
                    self._degreesDesc.count(degrees[node]) - 1] -= 1


class _Payment(object):
    """Store payment data."""

    __slots__ = ('createdTime', 'nodes')

    def __init__(self, paymentDict):
        """Convert created time to Unix time and set values for nodes."""
        self.createdTime = calendar.timegm(
            time.strptime(paymentDict['created_time'], '%Y-%m-%dT%XZ'))
        self.nodes = (paymentDict['actor'], paymentDict['target'])


class VenmoPayments(object):
    """Process payments and analyze graph."""

    __slots__ = ('_active', '_graph')

    def __init__(self, paymentDict):
        """Inialize active payments and Venmo Graph."""
        payment = _Payment(paymentDict)

        self._active = deque([payment])
        self._graph = _Graph(payment.nodes)

    @property
    def medianDegree(self):
        """Return median vertex degree."""
        return self._graph.median

    def add_payment(self, paymentDict):
        """Update active payments with new payment data."""
        payment = _Payment(paymentDict)
        if self._active[-1].createdTime - payment.createdTime >= 60:
            return

        self._graph.add_degrees(payment.nodes)

        if self._active[-1].createdTime <= payment.createdTime:
            self._active.append(payment)
            while payment.createdTime - self._active[0].createdTime >= 60:
                self._graph.remove_degrees(self._active.popleft().nodes)

        elif payment.createdTime <= self._active[0].createdTime:
            self._active.appendleft(payment)

        # sys.version_info >= (3, 5)
        elif hasattr(deque, 'insert'):
            i = 1
            while self.active[-i - 1].createdTime > payment.createdTime:
                i += 1

            self.active.insert(-i, payment)
        # sys.version_info < (3, 5)
        else:
            fresher = [self._active.pop()]
            nextActive = self._active.pop()
            while nextActive.createdTime > payment.createdTime:
                fresher.append(nextActive)
                nextActive = self._active.pop()

            self._active.extend(
                fresher.extend([payment, nextActive]).reverse())
