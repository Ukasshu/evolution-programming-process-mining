import re

class Compiler:
    def __init__(self, delimiter):
        self.delimiter = delimiter
        self.par_tasks = []

    def compile(self, string_to_compile):
        self.par_tasks = []
        tokens = string_to_compile.split(self.delimiter)

        program = []

        gateway_count = 0
        gateway_stack = []

        last_element = None

        additional_connections = []

        started = False
        ended = False

        for token in tokens:
            if token == "start" and not started:
                #start
                started = True
                program.append(".startEvent(\"start\")")
                last_element = "start"
                ###
            elif token.startswith("task("):
                #task
                match = re.search(r"\(([0-9]+)\)", token)
                task_num = match.group(1)
                program.append(".userTask(\"task" + task_num + "\")")
                last_element = "task" + task_num

                if any(list(map(lambda gat: gat["name"].startswith("par"), gateway_stack))):
                    self.par_tasks.append("task" + task_num)
                ###
            elif token == "loop":
                #loop
                curr_gat = {
                    "name": "gat" + str(gateway_count),
                    "type": "loop",
                }
                gateway_stack.append(curr_gat)
                program.append(".exclusiveGateway(\"" + curr_gat["name"] + "\")")
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "par":
                #par
                curr_gat = {
                    "name": "gat" + str(gateway_count),
                    "type": "par",
                    "end": False
                }
                gateway_stack.append(curr_gat)
                program.append(".parallelGateway(\"" + curr_gat["name"] + "\")")
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "ex":
                #ex
                curr_gat = {
                    "name": "gat" + str(gateway_count),
                    "type": "ex",
                    "end": False
                }
                gateway_stack.append(curr_gat)
                program.append(".exclusiveGateway(\"" + curr_gat["name"] + "\")")
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "exsplit":
                #exsplit
                curr_gat = {
                    "name": "gat" + str(gateway_count),
                    "type": "split"
                }
                gateway_stack.append(curr_gat)
                program.append(".exclusiveGateway(\"" + curr_gat["name"] +"\")")
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "next":
                #next
                last_gateway = gateway_stack[-1]
                if last_gateway["type"] == "split":
                    program.append(".moveToNode(\"" + last_gateway["name"] +"\")")
                elif last_gateway["type"] == "ex":
                    if not last_gateway["end"]:
                        program.append(".exclusiveGateway(\"e" + last_gateway["name"] + "\")")
                        last_gateway["end"] = True
                    else:
                        program.append(".connectTo(\"e" + last_gateway["name"] + "\")")
                    program.append(".moveToNode(\"" + last_gateway["name"] +"\")")
                elif last_gateway["type"] == "par":
                    if not last_gateway["end"]:
                        program.append(".parallelGateway(\"e" + last_gateway["name"] + "\")")
                        last_gateway["end"] = True
                    else:
                        program.append(".connectTo(\"e" + last_gateway["name"] + "\")")
                    program.append(".moveToNode(\"" + last_gateway["name"] +"\")")
                else:
                    raise Exception("Wrong token found")
                last_element = last_gateway["name"]
                ###
            elif token == "back":
                #back
                last_gateway = gateway_stack[-1]
                if last_gateway["type"] == "loop":
                    program.append(".connectTo(\"" + last_gateway["name"] +"\")")
                    program.append(".moveToNode(\"" + last_gateway["name"] + "\")")
                    gateway_stack.pop()
                    last_element = last_gateway["name"]
                elif last_gateway["type"] == "split":
                    gateway_stack.pop()
                    if len(gateway_stack) > 0:
                        last_element = gateway_stack[-1]["name"]
                    else:
                        last_element = None
                elif last_gateway["type"] in ["ex", "par"]:
                    program.append(".connectTo(\"e" + last_gateway["name"] +"\")")
                    program.append(".moveToNode(\"e" + last_gateway["name"] + "\")")
                    gateway_stack.pop()
                ###
            elif token.startswith("goto("):
                #goto
                match = re.search(r"\(([a-z0-9]+)\)", token)
                node_name = match.group(1)
                additional_connections.append({
                    "from": last_element,
                    "to": node_name
                })
                ###
            elif token == "end":
                if not ended:
                    program.append(".endEvent(\"end\")")
                    ended = True
                else:
                    additional_connections.append({
                        "from": last_element,
                        "to": "end"
                    })
            else:
                raise Exception("Unknown token")

        for conn in additional_connections:
            program.append(".moveToNode(\"" + conn["from"] + "\")")
            program.append(".connectTo(\"" + conn["to"] + "\")")

        program.append(".done();}}")

        return program
            