import numpy as np
from io import StringIO

def parse_gridfile(file_path):
    with open(file_path, 'r') as file:
        data = [line.strip() for line in file]
    X, Y, bend_penalty, via_penalty = map(int, data[0].split()[:4])
    #X 是X gridsize ~~cols
    #Y 是Y gridsize ~~rows

    # 处理网格数据
    grid_str = "\n".join(data[1:])
    array = np.genfromtxt(StringIO(grid_str))
    array = array.reshape((2*Y, X))
    layer1_grid, layer2_grid = np.vsplit(array, 2)

    # 信息
    print("Grid file parsed successfully.")
    print("bend_penalty:", bend_penalty, "\n", "via_penalty:", via_penalty)
    print("shape of layer1:", layer1_grid.shape)
    print("shape of layer2:", layer2_grid.shape)
    print("X:", X, "Y:", Y)
    # print("layer1 grid:\n", layer1_grid)
    # print("layer2 grid:\n", layer2_grid)

    print("layer1 grid.T:\n", layer1_grid.T)
    print("layer2 grid.T:\n", layer2_grid.T)
    layer_grids= np.array([layer1_grid.T, layer2_grid.T])
    return X,Y, bend_penalty, via_penalty, layer_grids

def parse_netlist(file_path):
    #每一行的格式为：net_id pin1_layer pin1_x pin1_y pin2_layer pin2_x pin2_y
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file]
    net_count = int(lines[0])
    nets = [
        {
            'net_id': int(parts[0]),
            'pin1': {'x': int(parts[2]), 'y': int(parts[3]), 'layer': int(parts[1])},
            'pin2': {'x': int(parts[5]), 'y': int(parts[6]), 'layer': int(parts[4])}
        }
        for parts in (line.split() for line in lines[1:net_count+1])
    ]

    #show
    # print("Number of nets:", net_count)
    # for net in nets:
    #     print(f"Net {net['net_id']}: Pin1 at ({net['pin1']['x']}, {net['pin1']['y']}, Layer {net['pin1']['layer']}), "
    #           f"Pin2 at ({net['pin2']['x']}, {net['pin2']['y']}, Layer {net['pin2']['layer']})")
    return nets,net_count