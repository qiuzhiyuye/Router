from parser import *
from evaluate import *
from output import *
import numpy as np
import time

class Result:
    #cost map: net_id -> cost
    #rt_map: net_id -> path
    def __init__(self, value=np.inf, rt_map=None, cost_map=None):
        self.value = value
        self.rt_map = rt_map
        self.cost_map = cost_map
class Coordinate:
    def __init__(self, x, y, layer):
        self.x = x
        self.y = y
        self.layer = layer

    def __str__(self):
        return f"({self.x}, {self.y}, {self.layer})"

def backtrack_path(S, T, parents):
    path = []
    current = T
    while current != S:
        path.append(current)
        current = parents[current]
    path.append(S)
    path.reverse()
    return path

def cost_cal(layer_grid, cell,prev_point,prev_prev_point,bend_penalty,via_penalty):  
    #价值函数
    x, y, layer = cell
    if layer_grid[x][y] == -1:
        cost = np.inf
    else:
        cost = layer_grid[x][y]

    #Todo:针对 转弯和 跨层，应该添加对应的代价 （over)
    last_x,last_y,last_layer = prev_point
    if layer != last_layer:
        cost += via_penalty
    elif prev_prev_point != None:
        prev_x, prev_y, prev_layer = prev_prev_point
        if (prev_x != x and prev_y != y):  
            cost += bend_penalty
    return cost

def find_path(Y, X, layer_grids, S, T, bend_penalty, via_penalty):
    #find path 可以用别的算法实现，可替换部分
    open_set = {}
    closed_set = set()
    parent_map = {}
    total_cost = {}

    start = (S['x'], S['y'], S['layer'])
    goal = (T['x'], T['y'], T['layer'])

    open_set[start] = 0
    total_cost[start] = 1  

    while open_set:
        #堆，取最小
        current = min(open_set.items(), key=lambda item: int(item[1]))[0]

        if current == goal:
            path = backtrack_path(start, goal, parent_map)
            return path, total_cost[current]

        neighbors = []
        x, y, current_layer = current
        # 上方
        if y > 0:
            if (current_layer == 1 and layer_grids[0][x][y - 1] != -1) or (current_layer == 2 and layer_grids[1][x][y - 1] != -1):
                neighbors.append({'x': x, 'y': y - 1, 'layer': current_layer})
        # 右方
        if x < X - 1:
            if (current_layer == 1 and layer_grids[0][x + 1][y] != -1) or (current_layer == 2 and layer_grids[1][x + 1][y] != -1):
                neighbors.append({'x': x + 1, 'y': y, 'layer': current_layer})
        # 下方
        if y < Y - 1:
            if (current_layer == 1 and layer_grids[0][x][y + 1] != -1) or (current_layer == 2 and layer_grids[1][x][y + 1] != -1):
                neighbors.append({'x': x, 'y': y + 1, 'layer': current_layer})
        # 左方
        if x > 0:
            if (current_layer == 1 and layer_grids[0][x - 1][y] != -1) or (current_layer == 2 and layer_grids[1][x - 1][y] != -1):
                neighbors.append({'x': x - 1, 'y': y, 'layer': current_layer})
        # 跨层
        other_layer = 2 if current_layer == 1 else 1
        if (current_layer == 1 and layer_grids[1][x][y] != -1) or (current_layer == 2 and layer_grids[0][x][y] != -1):
            neighbors.append({'x': x, 'y': y, 'layer': other_layer})

        for nb in neighbors:
            nb_tuple = (nb['x'], nb['y'], nb['layer'])

            if nb_tuple not in closed_set:
                prev_point = (current[0], current[1], current[2])
                if current in parent_map:
                    prev_prev_point = (parent_map[current][0], parent_map[current][1], parent_map[current][2])
                else:
                    prev_prev_point = None
                step_cost = cost_cal(layer_grids[nb_tuple[2]-1], nb_tuple, prev_point,prev_prev_point, bend_penalty, via_penalty)
                new_cost = total_cost[current] + step_cost
                if new_cost != np.inf:
                    if nb_tuple not in open_set or total_cost[nb_tuple] > new_cost:
                        total_cost[nb_tuple] = new_cost
                        parent_map[nb_tuple] = current

                        est_cost = new_cost

                        open_set[nb_tuple] = est_cost

        closed_set.add(current)
        del open_set[current]
    return None, None

def RT(Y, X, layer_grids, nets,bend_penalty,via_penalty,iteration):
    current_iteration = 1

    max_iteration = iteration*5

    fail_find_path_net = []
    fail_find_path_net_cnt = []

    best_result_flag = False
    #初始化为极大值
    best_result = Result()

    # Todo:rt 顺序排序,可能影响最后结果 (小数据上好像大差不差)
    #一种是随机
    nets.sort(key=lambda s: np.random.rand())
    #或者按照net两端距离排序，同时距离又可以分为两种方案
    # 1. 按照两端点的欧氏距离排序
    # nets.sort(key=lambda s: ((s["pin1"]['x']-s["pin2"]['x'])**2+(s["pin1"]['y']-s["pin2"]['y'])**2))
    # 2. 按照两端点的欧氏距离和层数差的平方和排序
    # 这种方式可以更好地处理跨层的情况
    # nets.sort(key=lambda s: ((s["pin1"]['x']-s["pin2"]['x'])**2+(s["pin1"]['y']-s["pin2"]['y'])**2)+(s["pin1"]['layer']-s["pin2"]['layer'])**2)
    # 3.按照曼哈顿距离排序
    nets.sort(key=lambda s: abs(s["pin1"]['x']-s["pin2"]['x'])+abs(s["pin1"]['y']-s["pin2"]['y'])+(s["pin1"]['layer']-s["pin2"]['layer']))


    # while current_iteration_fail_find_path_nets == [] or  best_result_flag ==False or current_iteration < iteration:
    while current_iteration <= iteration:
        
        current_iteration_fail_find_path_nets = []

        print('Iteration:'+str(current_iteration))

        # if current_iteration > max_iteration:
        #     print('too many iteration ! there may be some error in the routing! need add iteration')
        #     print('current_iteration_fail_find_path_nets.size=',len(current_iteration_fail_find_path_nets))
        #     print("best_result_flag:",best_result_flag)
        #     break


        #route 失败的net，重新rt
        for net in fail_find_path_net:
            nets.insert(0, net)
        fail_find_path_net = []

        current_iteration_fail_find_path_nets = []
        rt_map = {}
        cost_map = {}
        current_iteration +=1
        cnt = 0

        layer_current=[layer_grids[0].copy(),layer_grids[1].copy()]
        #先标记所有pin的点的位置为-1，提前设置障碍点
        for net in nets:
            net_id = net['net_id']
            pins=[net['pin1'],net['pin2']]

            layer_current[pins[0]['layer']-1][pins[0]['x']][pins[0]['y']] = -1
            layer_current[pins[1]['layer']-1][pins[1]['x']][pins[1]['y']] = -1

        for net in nets:
            net_id = net['net_id']
            pins=[net['pin1'],net['pin2']]
            layer_current[pins[0]['layer']-1][pins[0]['x']][pins[0]['y']] = 1
            layer_current[pins[1]['layer']-1][pins[1]['x']][pins[1]['y']] = 1
            cnt += 1
            print('Routing net id:',net_id)

            path,costs = find_path(Y, X, layer_current, pins[0], pins[1],bend_penalty,via_penalty)

            if path != None:       
                for point in path:
                    x, y, layer = point
                    layer_current[layer-1][x][y] = -1
                rt_map[net_id] = path
                cost_map[net_id] = costs
            else:
                cnt -= 1
                print(net_id,"didn't find path,may be some error and need try again")
                #回退状态
                current_iteration_fail_find_path_nets.append(net)
                rt_map[net_id] = None
                cost_map[net_id] = None
                layer_current[pins[0]['layer']-1][pins[0]['x']][pins[0]['y']] = -1
                layer_current[pins[1]['layer']-1][pins[1]['x']][pins[1]['y']] = -1

        fail_find_path_net += current_iteration_fail_find_path_nets
        fail_find_path_net_cnt.append(len(current_iteration_fail_find_path_nets))

        #判断是否是个合法route结果
        if current_iteration_fail_find_path_nets == [] and rt_map:
            best_result_flag = True
            if best_result.value > sum(cost_map.values()):
                best_result.value = sum(cost_map.values())
                best_result.rt_map = rt_map
                best_result.cost_map = cost_map

            # print('Iteration:',current_iteration,'successfully finished,only point cost:',best_result.value)
        else:
            best_result_flag = False       
    return best_result

def solve(design_name):
    output_path = '../output/' + design_name + '.router'
    input_nl_path = '../benchmark/' + design_name + '.nl'
    input_grid_path = '../benchmark/' + design_name + '.grid'

    nets, net_count = parse_netlist(input_nl_path)
    X, Y, bend_penalty, via_penalty, layer_grids = parse_gridfile(input_grid_path)

    layer1_grid, layer2_grid = layer_grids[0], layer_grids[1]

    #Todo:调迭代轮次
    design_iteration_map={
        "bench1": 2,
        "bench2": 2,
        "bench3": 2,
        "bench4": 2,
        "bench5": 5,
        "fract2": 10,
        "industry1": 10,
        "primary1": 10
    }
    iteration = design_iteration_map.get(design_name, 2)
    best_result=RT(Y, X, layer_grids, nets,bend_penalty,via_penalty,iteration)

    old_rt_map = best_result.rt_map.copy()
    #按 net_id 排序
    best_result.rt_map = {k: v for k, v in sorted(best_result.rt_map.items(), key=lambda item: item[0])}

    # print("rt_map:", rt_map)
    # print("cost_map:", cost_map)

    if(old_rt_map != best_result.rt_map):
        print("Routing table has been sorted by net_id.")
    else :
        print("Routing table is already sorted by net_id.")

    #只有点上的成本
    # only_point_cost = sum(best_result.cost_map.values())
    # print(f"only point cost for {design_name}: {only_point_cost}")

    total_cost=sum(best_result.cost_map.values())
    print(f"Total cost for {design_name}: {total_cost}")

    output_route_file(output_path, best_result.rt_map)
    #计算全部成本
    # evaluate(output_path,design_name)
    # print(type(best_result.rt_map))

    evaluate(best_result.rt_map, bend_penalty, via_penalty, layer_grids)


if __name__ == "__main__":
    design_names = ["bench1", "bench2", "bench3", "bench4", "bench5", "fract2", "industry1", "primary1"]
    big_design_names = ["bench5", "fract2", "industry1", "primary1"]
    # for design_name in design_names:
    for design_name in ["bench2"]:
    # for design_name in big_design_names:
        print(f"Running {design_name}...")
        start_time = time.time()
        solve(design_name)
        end_time = time.time()
        print(f"Finished {design_name} in {end_time - start_time:.2f} seconds.\n")