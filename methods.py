import pandas as pd

def load_data(file):
    strategic_raw_data = pd.read_excel(file, header=0, dtpe=object)
    qgis_table = pd.read_excel(file, sheet_name=1, header=0, usecols=["AssANode","AssBNode", "ID"], index_col=None)
    return strategic_raw_data, qgis_table

def extract_routes(strategic_raw_data, qgis_table, ogv=None):
    # Obtain the relevant user class data, filter the unique route information
    ogv_index=min(strategic_raw_data[strategic_raw_data["UC"] == 9].index)
    if ogv:
        strategic_data=strategic_raw_data[ogv_index:]
    else:
        strategic_data=strategic_raw_data[:ogv_index]

    strategic_data=strategic_data[strategic_data.iloc[:,0] == "route"]
    strategic_data.drop_duplicates(keep="first", inplace=True)

    # Create a list with all the nodes
    nodes = strategic_data.to_string(header=False, index=False).split()
    nodes=list(filter(lambda x: "NaN" not in x, nodes))

    # create a nested list containing lists of nodes that make up each route. Use "route" string as separator.
    # Handle the extra characters
    nodes_grouped, count = [], -1 # todo change from -1
    for i in range(len(nodes)):
        if nodes[i] == "route":
            nodes_grouped.append([])
            count+=1
            continue
        if "+" in nodes[i]:
            nodes_grouped[count].append(float(nodes[i].replace("+","")))
        else:
            nodes_grouped[count].append(float(nodes[i]))

    # Adjust the final element in each list that have been formatted as % in excel
    for count, node_group in enumerate(nodes_grouped):
        if len(str(node_group[-1])) < len(str(node_group[0])): # Think of a more robust way, perhaps average the lengths of all but the last
            node_group[-1] = node_group[-1]*100
        nodes_grouped[count] = list(map(int,node_group))

    # In the same nested list format, populate with the node to node combinations that make up the links
    nodes_joined=[]
    for i in range(len(nodes_grouped)):
        nodes_joined.append([])
        for j in range(len(nodes_grouped[i])-1):
            nodes_joined[i].append(f"{nodes_grouped[i][j]}>{nodes_grouped[i][j+1]}")

    # Extract the ID for each node to node combination, representing a link.

    # Obtain the link numbers for each node to node combination. Each list is a route composed of links.
    routes=[]
    for i in range(len(nodes_joined)):
        routes.append([])
        for link in nodes_joined[i]:
            link_index = (qgis_table.index[qgis_table["AssBNode"] == link].tolist()[0])
            routes[i].append(qgis_table.at[link_index, "ID"])

    return routes

def export_results(results):
    # Export results as csv
    #Fix the save name issue
    routes_df = pd.DataFrame(results)
    routes_df.to_csv('uc1-8__unique_routes.csv', index=False, header=False)
