class Coordinate:
    def __init__(self, x, y, layer):
        self.x = x
        self.y = y
        self.layer = layer

    def __str__(self):
        return f"({self.x}, {self.y}, {self.layer})"
def calculate_total_cost(rt_map, bend_penalty, via_penalty, layer_grids):
    total_cost = 0
    for net_id, path in rt_map.items():
        for point_id, point in enumerate(path):
            x = point[0]
            y = point[1]
            layer = point[2]
            if layer ==3:#通孔
                total_cost += via_penalty
            if layer == 1 or layer == 2:
                total_cost += layer_grids[layer - 1][x][y]
            if point_id > 1:  # Check for bends
                #上上个点
                prev_prev_layer = path[point_id - 2][2]
                prev_prev_x = path[point_id - 2][0]
                prev_prev_y = path[point_id - 2][1]
                #上个点
                prev_layer = path[point_id - 1][2]
                prev_x = path[point_id - 1][0]
                prev_y = path[point_id - 1][1]
                #同层
                if prev_prev_layer == layer and prev_layer == layer:
                    if(prev_prev_x != x and y != prev_prev_y):#转弯
                        total_cost += bend_penalty

    print("Evaluate all the paths, Total costs:",total_cost)


def evaluate(rt_map,bend_penalty, via_penalty, layer_grids):
    #Todo:可以增加许多别的评测指标，
    calculate_total_cost(rt_map, bend_penalty, via_penalty, layer_grids)
