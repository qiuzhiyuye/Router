class Coordinate:
    def __init__(self, x, y, layer):
        self.x = x
        self.y = y
        self.layer = layer

    def __str__(self):
        return f"({self.x}, {self.y}, {self.layer})"

def output_route_file(output_path, rt_map):
    with open(output_path, 'w') as file:
        file.write(str(len(rt_map)) + '\n')
        for net_id, paths in rt_map.items():
            file.write(str(net_id) + '\n')
            prev_coord = None
            if paths != None:
                for  x, y,layer in paths:
                    current_coord = Coordinate(x, y, layer)
                    if prev_coord!=None and prev_coord.layer != current_coord.layer and prev_coord.x == current_coord.x and prev_coord.y == current_coord.y:
                        file.write('3 ' + str(prev_coord.x) + ' ' + str(prev_coord.y) + '\n')  
                    file.write(str(current_coord.layer) + ' ' + str(current_coord.x) + ' ' + str(current_coord.y) + '\n')
                    prev_coord = current_coord
            file.write('0\n')# over