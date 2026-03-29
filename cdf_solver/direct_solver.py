import numpy as np
from scipy.sparse import crs_matrix, lil_matrix
from scipy.sparse.linalg import spsolve
import matplotlib.pyplot as plt

def solve_pcb_thermal_direct():
    # --- 1. 幾何與網格定義 ---
    nx, ny, nz = 30, 30, 5  # 小規模網格，共 5 層
    dx = dy = 1.0e-3       # 1mm
    dz = 0.2e-3            # 0.2mm (PCB 層厚)
    n_total = nx * ny * nz

    # --- 2. 材料性質 (k 值) ---
    k_cu = 380.0
    k_fr4 = 0.3
    
    # 初始化 3D k 矩陣
    k_grid = np.ones((nz, ny, nx)) * k_fr4
    k_grid[0, :, :] = k_cu  # 底層全銅 (GND)
    k_grid[2, 10:20, :] = k_cu  # 中間層有一條走線
    
    # 焦耳熱發熱量 S_u (僅在有銅的地方)
    source_q = np.zeros((nz, ny, nx))
    source_q[2, 10:20, 10:20] = 1.0e7  # 局部發熱源 (W/m^3)

    # 邊界條件
    T_ambient = 300.0
    h_conv = 15.0  # 頂部對流係數
    T_bottom_fixed = 530.0

    # --- 3. 組裝稀疏矩陣 A 與 向量 b ---
    # 使用 lil_matrix 方便組裝，最後轉為 csr 格式求解
    A = lil_matrix((n_total, n_total))
    b = np.zeros(n_total)

    # 索引轉換函數 (z, y, x) -> flat index
    def get_idx(z, y, x):
        return z * (ny * nx) + y * nx + x

    for z in range(nz):
        for y in range(ny):
            for x in range(nx):
                p = get_idx(z, y, x)
                
                # --- A. 處理底部固定溫度邊界 (Dirichlet) ---
                if z == 0:
                    A[p, p] = 1.0
                    b[p] = T_bottom_fixed
                    continue

                # --- B. 計算各個方向的傳導係數 a_nb ---
                # 使用 Harmonic Mean (調和平均) 處理不同材料介面
                coeff_nb = {}
                
                # 定義方向與鄰居偏移
                directions = [
                    ('E', 0, 0, 1, dx), ('W', 0, 0, -1, dx),
                    ('N', 0, 1, 0, dy), ('S', 0, -1, 0, dy),
                    ('T', 1, 0, 0, dz), ('B', -1, 0, 0, dz)
                ]

                a_p_sum = 0
                for name, dz_off, dy_off, dx_off, dist in directions:
                    nz_n, ny_n, nx_n = z + dz_off, y + dy_off, x + dx_off
                    
                    # 檢查是否超出邊界
                    if 0 <= nz_n < nz and 0 <= ny_n < ny and 0 <= nx_n < nx:
                        # 內部傳導
                        nb_idx = get_idx(nz_n, ny_n, nx_n)
                        # k_eff = Harmonic Mean
                        k1, k2 = k_grid[z, y, x], k_grid[nz_n, ny_n, nx_n]
                        k_eff = 2 * k1 * k2 / (k1 + k2)
                        
                        # 傳導係數 a_nb = k * Area / dist
                        area = (dx * dy * dz) / dist
                        a_nb = k_eff * area / dist # 這裡簡化表示
                        
                        A[p, nb_idx] = -a_nb
                        a_p_sum += a_nb
                    elif name == 'T':
                        # 頂部對流邊界 (Newton's Cooling)
                        area = dx * dy
                        a_conv = h_conv * area
                        a_p_sum += a_conv
                        b[p] += a_conv * T_ambient
                
                # --- C. 填入主對角線 a_p 與源項 S_u ---
                A[p, p] = a_p_sum
                # 能量源項 S_u = 單位體積發熱 * 體積
                b[p] += source_q[z, y, x] * (dx * dy * dz)

    # --- 4. 求解 Ax = b ---
    print("正在直接求解矩陣...")
    A_csr = A.tocsr()
    T_flat = spsolve(A_csr, b)
    T_3d = T_flat.reshape((nz, ny, nx))

    # --- 5. 結果可視化 ---
    plt.figure(figsize=(8, 6))
    plt.title("PCB Top Layer Temperature (Steady State)")
    plt.imshow(T_3d[-1, :, :], cmap='inferno', origin='lower')
    plt.colorbar(label='Temperature (K)')
    plt.show()

solve_pcb_thermal_direct()