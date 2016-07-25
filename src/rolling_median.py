"""Read input file and write to output file."""
import sys
import json
from median_degree import VenmoPayments


def process_venmo_payments(finName, foutName):
    """Process payment data, and write to file streaming median degree."""
    with open(finName, 'r') as fin, open(foutName, 'w') as fout:
        venmoGraph = VenmoPayments()

        jsonString = fin.readline()
        while jsonString:
            paymentDict = json.loads(jsonString)
            jsonString = fin.readline()

            try:
                paymentDict['actor']
                paymentDict['target']
                paymentDict['created_time']
            except KeyError:
                continue

            venmoGraph.add_payment(paymentDict)
            fout.write('%.2f' % venmoGraph.medianDegree)

            if jsonString:
                fout.write('\n')

if __name__ == '__main__':
    process_venmo_payments(sys.argv[1], sys.argv[2])
