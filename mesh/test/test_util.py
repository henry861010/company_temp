from pympler import asizeof
import tracemalloc
tracemalloc.start()

def memory_unit(x):
    if x / 1024 / 1024 / 1024 >= 1:
        return f"{x / 1024 / 1024:.2f} GB"
    elif x / 1024 / 1024 >= 1:
        return f"{x / 1024 / 1024 :.2f} MB"
    else:
        return f"{x / 1024:.2f} KB"

def show_memory_CDB(obj: 'CDB' = None, pre_s: str = ""):
    current, peak = tracemalloc.get_traced_memory()
    print(f'{pre_s}[Memory Usage]')
    print(f'{pre_s}     total usage: {memory_unit(peak)}')
    if obj:
        print(f'{pre_s}     element_2D: {memory_unit(asizeof.asizeof(obj.element_2D))}')
        print(f'{pre_s}     element_3D: {memory_unit(asizeof.asizeof(obj.element_3D))}')
        print(f'{pre_s}     element_to_nodes: {memory_unit(asizeof.asizeof(obj.element_to_nodes))}')
        print(f'{pre_s}     nodes: {memory_unit(asizeof.asizeof(obj.nodes))}')
        print(f'{pre_s}     node_map: {memory_unit(asizeof.asizeof(obj.node_map))}')