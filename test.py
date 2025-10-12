from mesher.region import Region


face1 = {
    "type": "BOX",
    "dim": [0,0,30,30]
}
region_obj1 = Region([face1])
region_obj1.set_box([10,10,20,20],setTo=2)

face2 = {
    "type": "BOX",
    "dim": [13,13,17,17]
}
region_ob2 = Region([face2])

region_obj1.set_by_region("AND", 2, region_ob2, 1, setTo=4)

region_obj1.show_graph()