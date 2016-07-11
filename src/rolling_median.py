"""Read input file and write to output file."""
import sys
import json
from median_degree import VenmoPayments


def process_venmo_payments(finName='./venmo_input/venmo-trans.txt',
                           foutName='./venmo_output/output.txt'):
    """Process payment data, and write to file streaming median degree."""
    with open(finName, 'r') as fin:
        with open(foutName, 'w') as fout:
            paymentDict = {}
            jsonString = fin.readline()
            while jsonString:
                paymentDict = json.loads(jsonString)
                jsonString = fin.readline()
                try:
                    paymentDict['actor']
                    paymentDict['target']
                    paymentDict['created_time']
                    break
                except KeyError:
                    pass

            venmoGraph = VenmoPayments(paymentDict)
            fout.write('%.2f' % venmoGraph.medianDegree)

            while jsonString:
                paymentDict = json.loads(jsonString)
                jsonString = fin.readline()
                try:
                    paymentDict['actor']
                    paymentDict['target']
                    paymentDict['created_time']
                    break
                except KeyError:
                    continue

                venmoGraph.add_payment(paymentDict)
                fout.write('\n%.2f' % venmoGraph.medianDegree)


if __name__ == '__main__':
    process_venmo_payments(*sys.argv)
