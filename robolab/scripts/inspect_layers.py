from pxr import Usd
stage = Usd.Stage.Open("scenes/RobotLab.usda", load=Usd.Stage.LoadAll)
for layer in stage.GetLayerStack():
    print(layer.identifier)

robot_prim = stage.GetPrimAtPath("/Lab/Robot_Station_1/RobotInstance")
#print(robot_prim.GetReferences())
