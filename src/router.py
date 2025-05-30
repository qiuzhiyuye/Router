from parser import *

def solve(design_name):
  output_path='../output/'+design_name+'.router'
  input_nl_path = '../benchmark/'+design_name+'.nl'
  input_grid_path  = '../benchmark/'+design_name+'.grid'
  #同样检测parse_grid和parse_grid_origin是否相同
  nets, net_count = parse_netlist(input_nl_path)
  X,Y, bend_penalty, via_penalty, layer1_grid, layer2_grid = parse_gridfile(input_grid_path)











if __name__ == "__main__":
  design_names=["bench1","bench2","bench3","bench4","bench5","fract2","industry1","primary1"]
  for design_name in ["bench1"]:
    print(f"Running {design_name}...")
    solve(design_name)

    print(f"Finished {design_name}.\n")