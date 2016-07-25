"""Manipulate Venmo JSON mesages and analyze the resultant graph object."""
import time
import calendar
import heapq


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
        try:
            self._neighbors[node]
        except KeyError:
            return

        if self._neighbors[node] > 1:
            self._neighbors[node] -= 1
        else:
            del self._neighbors[node]


class _Graph(object):
    """Manipulate set of vertices and calulate median vertix degree."""

    def __init__(self):
        """Instantiate vertex dict and descending degrees list."""
        self._vertices = {}
        self._degreesDesc = []

    @property
    def median(self):
        """Return median vertex degree."""
        if not self._vertices:
            return 0

        n = len(self._vertices)
        median = self._degreesDesc[n // 2]

        if not n % 2:
            median = round((median + self._degreesDesc[n//2 - 1]) / 2.0, 2)

        return median

    def _add_edge(self, actor, target):
        """Add vertices or increment edge weights."""
        nodes = (actor, target)
        for i in (0, 1):
            self._vertices.setdefault(nodes[i], _Vertex()).add_neighbor(
                nodes[(i + 1) % 2])

    def _remove_edge(self, actor, target):
        """Decrement edge weights and remove vertices if degree == 0."""
        nodes = (actor, target)
        for i in (0, 1):
            try:
                self._vertices[nodes[i]]
            except KeyError:
                continue

            self._vertices[nodes[i]].remove_neighbor(nodes[(i + 1) % 2])

            if self._vertices[nodes[i]].degree == 0:
                del self._vertices[nodes[i]]

    def _get_first_index(self, degree):
        """Get lowest index with value degree."""
        if degree < 1:
            raise ValueError('degree must be 1 or greater')
        lo = 0
        hi = len(self._degreesDesc)

        while lo < hi:
            mid = (lo + hi + 1) // 2
            if degree < self._degreesDesc[mid]:
                lo = mid
            else:
                hi = mid - 1

        if degree == self._degreesDesc[hi] and hi != -1:
            return hi
        else:
            return hi + 1

    def _get_last_index(self, degree):
        """Get highest index with value degree."""
        if degree < 1:
            raise ValueError('degree must be 1 or greater')
        length = len(self._degreesDesc)
        lo = 0
        hi = length

        while lo < hi:
            mid = (lo + hi) // 2
            if degree > self._degreesDesc[mid]:
                hi = mid
            else:
                lo = mid + 1
        return lo - 1

    def add_degrees(self, actor, target):
        """Add edges and update degree list."""
        nodes = (actor, target)
        degrees = {}
        for node in nodes:
            if node in self._vertices:
                degrees[node] = self._vertices[node].degree
            else:
                self._degreesDesc.append(1)

        self._add_edge(*nodes)

        for nodeDegreePair in degrees.items():
            if nodeDegreePair[1] != self._vertices[nodeDegreePair[0]].degree:
                self._degreesDesc[
                    self._get_first_index(nodeDegreePair[1])] += 1

    def remove_degrees(self, actor, target):
        """Remove edges and update degree list."""
        try:
            self._vertices[actor]
            self._vertices[target]
        except KeyError:
            return

        nodes = (actor, target)
        degrees = {node: self._vertices[node].degree for node in nodes}

        self._remove_edge(*nodes)

        for node in nodes:
            if node not in self._vertices:
                self._degreesDesc.pop()
            elif degrees[node] != self._vertices[node].degree:
                self._degreesDesc[self._get_last_index(degrees[node])] -= 1


class _Payment(object):
    """Store payment data."""

    __slots__ = ('createdTime', 'actor', 'target')

    def __init__(self, paymentDict):
        """Convert created time to Unix time and set values for nodes."""
        self.createdTime = calendar.timegm(
            time.strptime(paymentDict['created_time'], '%Y-%m-%dT%XZ'))
        self.actor = paymentDict['actor']
        self.target = paymentDict['target']


class VenmoPayments(object):
    """Process payments and analyze graph."""

    def __init__(self):
        """Inialize active payments and Venmo Graph."""
        self._maxTime = 0
        self._activeHeap = []
        self._activeDict = {}
        self._graph = _Graph()

    @property
    def medianDegree(self):
        """Return median vertex degree."""
        return self._graph.median

    def add_payment(self, paymentDict):
        """Update active payments with new payment data."""
        payment = _Payment(paymentDict)

        if self._maxTime - payment.createdTime >= 60:
            return
        elif payment.createdTime > self._maxTime:
            self._maxTime = payment.createdTime
            while (self._activeHeap and
                   self._maxTime - self._activeHeap[0] >= 60):
                removeTime = heapq.heappop(self._activeHeap)
                activeList = self._activeDict[removeTime]
                self._graph.remove_degrees(*activeList.pop())
                if not activeList:
                    del self._activeDict[removeTime]

        heapq.heappush(self._activeHeap, payment.createdTime)
        self._activeDict.setdefault(payment.createdTime, []).append(
            (payment.actor, payment.target))

        self._graph.add_degrees(payment.actor, payment.target)
