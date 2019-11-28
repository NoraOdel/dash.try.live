from datetime import datetime, timedelta
import plotly.graph_objs as go
from static.run import main
from fix import fixer, meta_fixer
import argparse
import numpy as np

my_parser = argparse.ArgumentParser()
my_parser.add_argument('firstlast',
                       help='Choose time for rendering by typing "-firstlast" followed by '
                            '"yyyy-mm-dd hh:mm:ss", for both first = beginning and last = ending',
                       type=str,
                       nargs=4)

my_parser.add_argument('-ns',
                       help='Choose one or more NameServers to visualize by typing "-ns" followed by wanted'
                            ' nameservers like this: "letter".ns.se"4/6", default is "all4" which means '
                            'every nameserver for IPv4',
                       type=str,
                       nargs='*',
                       default='all')
my_parser.add_argument('-interval',
                       help='choose time difference for measurement results, default is 10 min',
                       type=int,
                       nargs=1,
                       default=[10])

args = my_parser.parse_args()
nameserver = args.ns
firstlast = args.firstlast
interval = args.interval
start = datetime.strptime(firstlast[0] + ' ' + firstlast[1], '%Y-%m-%d %H:%M:%S')
last = datetime.strptime(firstlast[2] + ' ' + firstlast[3], '%Y-%m-%d %H:%M:%S')

print('Interval: ' + str(interval[0]))
print('Initial start time: ' + str(start))
print('Process will stop when start is equal to: ' + str(last))
print('Rendering: ' + str(nameserver))


ms_id = {}
with open('msmIDs-20191119-to-20191126', 'r') as file:  # change in regards to which week is to be examined
    f = file.readlines()
    for item in f:
        item = item.rstrip().split(', ')
        if nameserver is 'all':
            ip = int(item[1][-1])
            ms_id[item[1]] = item[0]
        else:
            for numb in range(len(nameserver)):
                if nameserver[numb] == item[1]:
                    ms_id[item[1]] = item[0]
file.close()

y_dict = {}
x_dict = {}
for num in range(1, len(ms_id)+1):  # the amount of y keys in 'data' should be the same as the amount of keys in 'ms_id'
    x_dict['x' + str(num)] = []
    y_dict['y' + str(num)] = []


while start != last:  # depending on time and interval

    start = start + timedelta(minutes=interval[0])  # interval
    stop = start + timedelta(minutes=10)
    rtt_list = main(start, stop, ms_id)

    for y in y_dict:
        x = 'x' + y.strip('y')
        y_dict[y].append(np.mean(rtt_list[int(y.strip('y'))-1]))
        x_dict[x].append(str(start))

fig = go.Figure()
for y in y_dict:
    name = list(ms_id)[int(y.strip('y'))-1]
    x = 'x' + y.strip('y')
    if int(y.strip('y')) >= 11:
        line_ip = 'lines+markers'
    else:
        line_ip = 'lines'

    fig.add_trace(go.Scatter(x=x_dict[x], y=y_dict[y],
                             mode=line_ip,
                             name=name,
                             hoverinfo='text+y+name',
                             hovertemplate='RTT: %{y}'))

initial = datetime.strptime(firstlast[0], '%Y-%m-%d')
if str(initial).split(' ')[0] == str(last).split(' ')[0]:
    title_part = 'on ' + str(initial).split(' ')[0]
else:
    title_part = 'between ' + str(initial).split(' ')[0] + ' and ' + str(last).split(' ')[0]
fig.update_layout(title='Median RTT (in milliseconds) for .se NameServers ' + title_part,
                  yaxis=dict(
                      ticksuffix='ms'
                  ),
                  xaxis=dict(
                      tickmode='auto',
                      nticks=6,
                      dtick=1
                  ))
fig.show()

fixer()
meta_fixer()

