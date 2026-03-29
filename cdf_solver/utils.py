def get_k_grid(nx, ny, nz, dx, dy, dz):
    k_cu = 380.0
    k_fr4 = 0.3
    
    k_grid = np.ones((nz, ny, nx)) * k_fr4
    
    k_grid[0, :, :] = k_cu  # 底層全銅 (GND)
    k_grid[2, 10:20, :] = k_cu  # 中間層有一條走線
    
    return k_grid

def get_q_grid():
    source_q = np.zeros((nz, ny, nx))
    source_q[2, 10:20, 10:20] = 1.0e7  # 局部發熱源 (W/m^3)
    
    return source_q

