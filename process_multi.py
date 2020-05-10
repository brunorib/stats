import matplotlib.pyplot as plt
import csv
import argparse
import os

time_yz = []
time_b = []
y = []
z = []
b = []

request_time_threshlod_max=6000

parser = argparse.ArgumentParser(description='Process stats.')
parser.add_argument('--statsfile',
                    help='the stats file from our client-wasm test')
parser.add_argument('--info', 
                    help='info to be plotted')
args = parser.parse_args()

with open(args.statsfile,'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    with open("processed.csv","+w") as processed:
        new = csv.writer(processed, delimiter=',')
        first = False
        for row in plots:
            if row:
                if len(row) > 4:
                    if "/" in row[3]:
                        sp = row[3].split("/")
                        new.writerow([row[0], row[1], row[2], sp[0]])
                        new.writerow(["/"+sp[1], row[4], row[5], row[6]])
                elif len(row) == 4:
                    new.writerow(row)

with open("processed.csv",'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    first = False
    index = 0
    for row in plots:
        if not row:
            continue

        if not first:
            start = int(row[3])
            first = True

        if len(row) == 4:
            if args.info == "retrieve" or args.info == "thres":
                if row[0] == '/commitments':
                    z.append(int(row[1]))
                    time_yz.append(index)
                    index += 1
                if row[0].startswith('/answers'):
                    y.append(int(row[1]))
                
            if args.info == "consume":
                if row[0] == '/balances/token':
                    b.append(int(row[1]))
                    time_b.append(index)
                    index+=1

            end = int(row[3])




os.remove("processed.csv")
if args.info == "thres":
    elapsed = (end-start)/1000
    print("Total time of test in seconds: %s"%(elapsed))
    n = len(time_yz)
    print("Total number of retrievals: %s"%(n))
    print("Retrievals/s: %s"%(n/elapsed))
    
    len_zy = len(z)+len(y)
    request_times = sum(z) + sum(y)
    print("Mean request time: %s"%(request_times/len_zy))

    thresholds = []
    percentages = []
    for thres in range(request_time_threshlod_max):
        greater = sum(i > thres for i in z)
        greater += sum(i > thres for i in y)
        thresholds.append(thres)
        percentages.append(greater/len_zy)
    plt.plot('time', 'percentage', data={'time': thresholds, 'percentage': percentages}, marker='', color='red')
    plt.title('Percentage of requests that take longer than')
    plt.xlabel('time (ms)', fontsize=14)
    plt.ylabel('percentage', fontsize=16)

if args.info == "retrieve":
    plt.plot('time', 'reply_answer', data={'time': time_yz, 'reply_answer': y}, marker='', color='red')
    plt.plot('time', 'do_commit', data={'time': time_yz, 'do_commit': z}, marker='', color='blue')
    plt.title('Response time over multiple user requests')
    plt.xlabel('request number', fontsize=14)
    plt.ylabel('response time (ms)', fontsize=16)
if args.info == "consume":
    plt.plot('time', 'consume_token', data={'time': time_b, 'consume_token': b}, marker='', color='green')
    plt.title('Response time over multiple user requests')
    plt.xlabel('request number', fontsize=14)
    plt.ylabel('response time (ms)', fontsize=16)
plt.legend()
plt.show()