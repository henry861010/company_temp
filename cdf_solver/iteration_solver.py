import numpy as np
import matplotlib.pyplot as plt

def solve_pcb_thermal_iteration():
    # --- 1. 網格與幾何定義 ---
    nx, ny, nz = 50, 50, 6
    dx = dy = 1.0e-3  # 1mm
    dz = 0.25e-3      # 0.25mm
    
    # --- 2. 材料性質 (k 值) ---
    k_cu = 380.0
    k_fr4 = 0.3
    k_grid = np.ones((nz, ny, nx)) * k_fr4
    
    # 設置不同層的走線 (不同層不同 k)
    k_grid[0, :, :] = k_cu          # Bottom: GND Plane
    k_grid[2, 20:30, :] = k_cu      # Middle: 一條橫向走線
    k_grid[5, 20:30, 20:30] = k_cu  # Top: 元件焊盤
    
    # 設置發熱源 S_u (Watts per element)
    # 注意：這裡直接存儲功率 S_u，而不是功率密度
    S_u = np.zeros((nz, ny, nx))
    S_u[5, 22:28, 22:28] = 0.5  # 假設頂部晶片發熱 0.5W

    # 邊界條件
    T_ambient = 300.0
    h_conv = 20.0  # 對流係數
    T_bottom_fixed = 530.0

    # --- 3. 預計算係數矩陣 (因為 k 是 Constant，只需算一次) ---
    # 計算各方向的傳導率 a_nb (使用調和平均)
    def get_a_nb(k1, k2, area, dist):
        k_eff = 2 * k1 * k2 / (k1 + k2)
        return k_eff * area / dist

    # 初始化各方向的 a_nb 矩陣
    ae = np.zeros_like(k_grid); aw = np.zeros_like(k_grid)
    an = np.zeros_like(k_grid); as_ = np.zeros_like(k_grid)
    at = np.zeros_like(k_grid); ab = np.zeros_like(k_grid)

    # 以 X 方向 (East/West) 為例計算
    ae[:, :, :-1] = get_a_nb(k_grid[:, :, :-1], k_grid[:, :, 1:], dy*dz, dx)
    aw[:, :, 1:] = ae[:, :, :-1]
    
    # Y 方向 (North/South)
    an[:, :-1, :] = get_a_nb(k_grid[:, :-1, :], k_grid[:, 1:, :], dx*dz, dy)
    as_[:, 1:, :] = an[:, :-1, :]
    
    # Z 方向 (Top/Bottom)
    at[:-1, :, :] = get_a_nb(k_grid[:-1, :, :], k_grid[1:, :, :], dx*dy, dz)
    ab[1:, :, :] = at[:-1, :, :]

    # 計算對角線 a_P
    # 頂層加上對流項 h*A
    a_conv = h_conv * (dx * dy)
    a_p = ae + aw + an + as_ + at + ab
    a_p[-1, :, :] += a_conv # 頂層散熱
    
    # 修改 S_u 包含環境溫度項 (針對對流邊界)
    S_u[-1, :, :] += a_conv * T_ambient

    # --- 4. 迭代求解 ---
    T = np.ones((nz, ny, nx)) * T_ambient
    T[0, :, :] = T_bottom_fixed  # 底部固定
    
    max_iter = 5000
    tol = 1e-4
    
    print("開始迭代...")
    for i in range(max_iter):
        T_old = T.copy()
        
        # 核心更新公式：T_p = (sum(a_nb * T_nb) + S_u) / a_p
        # 使用切片進行全場加速計算 (避開邊界)
        T_nb_sum = (
            ae * np.roll(T, -1, axis=2) + aw * np.roll(T, 1, axis=2) +
            an * np.roll(T, -1, axis=1) + as_ * np.roll(T, 1, axis=1) +
            at * np.roll(T, -1, axis=0) + ab * np.roll(T, 1, axis=0)
        )
        
        # 更新內部節點
        T = (T_nb_sum + S_u) / a_p
        
        # 強制執行 Dirichlet 邊界 (底部固定)
        T[0, :, :] = T_bottom_fixed
        
        # 檢查收斂 (L-inf norm)
        error = np.max(np.abs(T - T_old))
        if error < tol:
            print(f"收斂！迭代次數: {i}, 誤差: {error:.6e}")
            break
        
        if i % 500 == 0:
            print(f"Iteration {i}, Error: {error:.6e}")

    return T

# 執行並繪圖
T_final = solve_pcb_thermal_iteration()
plt.imshow(T_final[-1, :, :], cmap='magma', origin='lower')
plt.title("Top Layer Temperature Distribution (Iteration Method)")
plt.colorbar()
plt.show()