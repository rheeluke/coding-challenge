"""Test median_degree and rolling_median modules."""
import unittest
import median_degree
import rolling_median


class TestVertex(unittest.TestCase):
    """Test median_degree._Vertex methods."""

    def test_addRemove_neighbor(self):
        """Check vertex degree and edge weights."""
        vertex = median_degree._Vertex()
        self.assertEqual(vertex._neighbors, {})
        self.assertEqual(vertex.degree, 0)

        vertex.add_neighbor('a')
        self.assertEqual(vertex._neighbors, {'a': 1})
        self.assertEqual(vertex.degree, 1)

        vertex.add_neighbor('a')
        self.assertEqual(vertex._neighbors, {'a': 2})
        self.assertEqual(vertex.degree, 1)

        vertex.add_neighbor('b')
        self.assertEqual(vertex._neighbors, {'a': 2, 'b': 1})
        self.assertEqual(vertex.degree, 2)

        vertex.remove_neighbor('a')
        self.assertEqual(vertex._neighbors, {'a': 1, 'b': 1})

        vertex.remove_neighbor('b')
        self.assertEqual(vertex._neighbors, {'a': 1})

        vertex.remove_neighbor('a')
        self.assertEqual(vertex._neighbors, {})


class TestGraph(unittest.TestCase):
    """Test median_degree._Graph methods."""

    def test_addRemove_degrees(self):
        """Check vertex list, degrees list, and median degree."""
        graph = median_degree._Graph(('a', 'b'))
        self.assertIn('a', graph._vertices.keys())
        self.assertIn('b', graph._vertices.keys())
        self.assertEqual(graph._degreesDesc, [1, 1])
        self.assertEqual(graph.median, 1.0)

        graph.remove_degrees(('a', 'b'))
        self.assertEqual(graph._vertices, {})
        self.assertEqual(graph._degreesDesc, [])

        graph.add_degrees(('a', 'b'))
        graph.add_degrees(('a', 'b'))
        self.assertEqual(graph._degreesDesc, [1, 1])
        self.assertEqual(graph.median, 1.0)

        graph.add_degrees(('a', 'c'))
        self.assertEqual(graph._degreesDesc, [2, 1, 1])
        self.assertEqual(graph.median, 1)

        graph.remove_degrees(('a', 'b'))
        self.assertEqual(graph._degreesDesc, [2, 1, 1])
        self.assertEqual(graph.median, 1)

        graph.add_degrees(('a', 'b'))
        graph.remove_degrees(('a', 'c'))
        self.assertEqual(graph._degreesDesc, [1, 1])
        self.assertEqual(graph.median, 1.0)

        graph.add_degrees(('a', 'c'))
        graph.add_degrees(('b', 'd'))
        self.assertEqual(graph._degreesDesc, [2, 2, 1, 1])
        self.assertEqual(graph.median, 1.5)

        graph.add_degrees(('a', 'e'))
        graph.add_degrees(('a', 'f'))
        graph.add_degrees(('c', 'd'))
        graph.add_degrees(('a', 'd'))
        self.assertEqual(graph._degreesDesc, [5, 3, 2, 2, 1, 1])
        self.assertEqual(graph.median, 2.0)

        graph.remove_degrees(('a', 'f'))
        self.assertEqual(graph._degreesDesc, [4, 3, 2, 2, 1])
        self.assertEqual(graph.median, 2)


class TestPayment(unittest.TestCase):
    """Test median_degree._Payment methods."""

    def test_init(self):
        """Check created time integer, and nodes tupple."""
        payment = median_degree._Payment({
            "created_time": "2016-03-29T06:04:39Z",
            "target": "Joey_Ostreicher", "actor": "Gwen-Mennear"})
        self.assertEqual(payment.createdTime, 1459231479)
        self.assertEqual(payment.nodes, ('Gwen-Mennear', 'Joey_Ostreicher'))


class TestVenmoPayments(unittest.TestCase):
    """Test median_degree.VenmoPayment methods."""

    def test_add_payment(self):
        """Check length and times of active payments list, and medianDegree."""
        ab = {"created_time": "2016-03-29T06:04:39Z",
              "target": "b", "actor": "a"}
        payment = median_degree._Payment(ab)
        venmo = median_degree.VenmoPayments(ab)
        self.assertEqual(len(venmo._active), 1)
        self.assertEqual(
            [venmo._active[0].createdTime, venmo._active[0].nodes],
            [payment.createdTime, payment.nodes])
        self.assertEqual(venmo.medianDegree, 1.0)

        ab1 = ab
        ab1['created_time'] = '2016-03-28T06:04:39Z'
        venmo.add_payment(ab1)
        self.assertEqual(len(venmo._active), 1)
        self.assertEqual(venmo._active[0].createdTime, payment.createdTime)
        self.assertEqual(venmo.medianDegree, 1.0)

        ab1 = ab
        ab1['created_time'] = '2016-03-29T06:03:39Z'
        venmo.add_payment(ab1)
        self.assertEqual(len(venmo._active), 1)
        self.assertEqual(venmo._active[0].createdTime, payment.createdTime)
        self.assertEqual(venmo.medianDegree, 1.0)

        ab['created_time'] = '2016-03-29T06:05:39Z'
        venmo.add_payment(ab)
        payment = median_degree._Payment(ab)
        self.assertEqual(len(venmo._active), 1)
        self.assertEqual(venmo._active[0].createdTime, payment.createdTime)
        self.assertEqual(venmo.medianDegree, 1.0)

        ab['created_time'] = '2016-04-1T00:01:00Z'
        venmo.add_payment(ab)
        payment = median_degree._Payment(ab)
        self.assertEqual(len(venmo._active), 1)
        self.assertEqual(venmo._active[0].createdTime, payment.createdTime)
        self.assertEqual(venmo.medianDegree, 1.0)

        AB = [ab]
        P = [payment]
        AB.append(AB[0])
        AB[1]['created_time'] = '2016-04-1T00:01:30Z'
        venmo.add_payment(AB[1])
        P.append(median_degree._Payment(AB[1]))
        self.assertEqual(len(venmo._active), 2)
        VcT = [i.createdTime for i in venmo._active]
        PcT = [i.createdTime for i in P]
        self.assertEqual(VcT, PcT)
        self.assertEqual(venmo.medianDegree, 1.0)

        AB.insert(0, AB[0])
        AB[0]['created_time'] = '2016-04-1T00:00:31Z'
        venmo.add_payment(AB[0])
        P.insert(0, median_degree._Payment(AB[0]))
        self.assertEqual(len(venmo._active), 3)
        VcT = [i.createdTime for i in venmo._active]
        PcT = [i.createdTime for i in P]
        self.assertEqual(VcT, PcT)
        self.assertEqual(venmo.medianDegree, 1.0)

        del AB[0]
        AB.extend([AB[0], AB[0]])
        AB[-1]['created_time'] = '2016-04-1T00:01:59Z'
        AB[-2]['created_time'] = '2016-04-1T00:01:45Z'
        venmo.add_payment(AB[-1])
        venmo.add_payment(AB[-2])
        del P[0]
        P.extend([
            median_degree._Payment(AB[-2]), median_degree._Payment(AB[-1])])
        self.assertEqual(len(venmo._active), 4)
        VcT = [i.createdTime for i in venmo._active]
        PcT = [i.createdTime for i in P]
        self.assertEqual(VcT, PcT)
        self.assertEqual(venmo.medianDegree, 1.0)


class TestRollingMedian(unittest.TestCase):
    """Test generated file output."""

    def test_process_venmo_payments(self):
        """Check file output."""
        fin = ('../insight_testsuite/tests/test-2-venmo-trans'
               '/venmo_input/venmo-trans.txt')
        with open(fin, 'w') as finTest:
            finTest.write(
                '{"created_time": "2016-03-29T00:10:00Z",'
                '"target": "b", "actor": "a"}')

        fout = ('../insight_testsuite/tests/test-2-venmo-trans'
                '/venmo_output/output.txt')
        rolling_median.process_venmo_payments(fin, fout)

        with open(fout, 'r') as foutTest:
            line = foutTest.readline()
            self.assertEqual(line, '1.00')
            line = foutTest.readline()
            self.assertEqual(line, '')

        with open(fin, 'a') as finTest:
            finTest.write(
                '\n{"created_time": "2016-03-29T00:10:15Z",'
                '"target": "c", "actor": "a"}'
                '\n{"created_time": "2016-03-29T00:10:30Z",'
                '"target": "d", "actor": "b"}')

        rolling_median.process_venmo_payments(fin, fout)

        with open(fout, 'r') as foutTest:
            line = foutTest.readline()
            self.assertEqual(line, '1.00\n')
            line = foutTest.readline()
            self.assertEqual(line, '1.00\n')
            line = foutTest.readline()
            self.assertEqual(line, '1.50')
            line = foutTest.readline()
            self.assertEqual(line, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
