from xes_reader import XESReader

reader = XESReader("running-example-just-two-cases.xes")

reader.read_xes()

# print(reader.traces)

for key, events_list in reader.traces.items():
    print(key)
    for event in events_list:
        print(event)


for index in range(len(reader.tasks)):
    print(index, ": ", reader.tasks[index])



