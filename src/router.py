from parser import *
import heapq
import numpy as np

def route_single_net(start, goal, grids, bend_penalty, via_penalty, X, Y, used_mask=None):
    # 状态: (x, y, layer, prev_dir)
    # 返回: 路径 [(x, y, layer), ...]
    directions = [ (0,1), (1,0), (0,-1), (-1,0) ]  # 上右下左

    heap = []
    heapq.heappush(heap, (0, start, None, []))  # (cost, (x,y,layer), prev_dir, path)
    visited = set()

    while heap:
        cost, (x, y, l), prev_dir, path = heapq.heappop(heap)
        if (x, y, l) == goal:
            return path + [(x, y, l)]
        if (x, y, l, prev_dir) in visited:
            continue
        visited.add((x, y, l, prev_dir))

        # 四邻域
        for i, (dx, dy) in enumerate(directions):
            nx, ny, nl = x+dx, y+dy, l
            if 0 <= nx < X and 0 <= ny < Y and grids[nl][ny][nx] >= 0:
                # 检查是否被占用
                if used_mask is not None and used_mask[nl][ny][nx]:
                    continue
                # 判断转弯
                turn = 0 if prev_dir is None or prev_dir == i else 1
                new_cost = cost + grids[nl][ny][nx] + (bend_penalty if turn else 0)
                heapq.heappush(heap, (new_cost, (nx, ny, nl), i, path + [(x, y, l)]))

        # 跨层（过孔）
        other_layer = 1 - l
        if grids[other_layer][y][x] >= 0:
            if used_mask is not None and used_mask[other_layer][y][x]:
                continue
            new_cost = cost + via_penalty + grids[other_layer][y][x]
            heapq.heappush(heap, (new_cost, (x, y, other_layer), prev_dir, path + [(x, y, l)]))

    return []  # 无解

def solve(design_name):
    output_path = '../output/' + design_name + '.router'
    input_nl_path = '../benchmark/' + design_name + '.nl'
    input_grid_path = '../benchmark/' + design_name + '.grid'

    nets, net_count = parse_netlist(input_nl_path)
    X, Y, bend_penalty, via_penalty, layer1_grid, layer2_grid = parse_gridfile(input_grid_path)
    grids = [layer1_grid, layer2_grid]  # 0: layer1, 1: layer2

    # 用于记录已布线点，防止冲突
    used_mask = np.zeros((2, Y, X), dtype=bool)
    results = []

    for net in nets:
        start = (net['pin1']['x'], net['pin1']['y'], net['pin1']['layer']-1)
        goal  = (net['pin2']['x'], net['pin2']['y'], net['pin2']['layer']-1)
        path = route_single_net(start, goal, grids, bend_penalty, via_penalty, X, Y, used_mask)
        results.append(path)
        # 标记已用路径，防止后续net冲突
        for x, y, l in path:
            used_mask[l][y][x] = True

    # 输出
    with open(output_path, 'w') as f:
        f.write(f"{len(results)}\n")
        for path in results:
            for x, y, l in path:
                f.write(f"{x} {y} {l+1}\n")
            f.write("0\n")

if __name__ == "__main__":
    design_names = ["bench1", "bench2", "bench3", "bench4", "bench5", "fract2", "industry1", "primary1"]
    for design_name in ["bench1"]:
        print(f"Running {design_name}...")
        solve(design_name)
        print(f"Finished {design_name}.\n")