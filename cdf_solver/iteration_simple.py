import numpy as np
import matplotlib.pyplot as plt

def simulate_pcb_thermal():
    # --- 1. 設定幾何與網格密度 ---
    # 假設 PCB 大小為 50mm x 50mm，總厚度約 1.6mm
    nx, ny, nz = 50, 50, 6  # 平面 50x50 網格，共 6 層
    dx = dy = 0.001         # 1mm
    dz = 0.00026            # 每層約 0.26mm (總厚度 ~1.6mm)

    # --- 2. 材料性質 (k 值) ---
    k_cu = 380.0    # 銅 (W/m·K)
    k_fr4 = 0.3     # FR4 基材 (W/m·K)

    # 初始化 3D k 矩陣 (預設全部為 FR4)
    k_grid = np.ones((nz, ny, nx)) * k_fr4

    # 模擬「不同層不同走線」:
    # 第 0 層 (Bottom): 全銅平面 (Ground Plane)
    k_grid[0, :, :] = k_cu
    
    # 第 2 層 (Internal): 假設中間有一條寬度為 5mm 的粗走線
    k_grid[2, 20:25, :] = k_cu
    
    # 第 5 層 (Top): 假設中心有一個發熱元件的焊盤 (10x10 mm)
    k_grid[5, 20:30, 20:30] = k_cu

    # --- 3. 邊界條件設定 ---
    T_ambient = 300.0       # 環境溫度 (K)
    T_bottom_heat = 530.0   # 底部熱源固定溫度 (K)
    h_conv = 15.0           # 表面對流係數 (W/m²·K)

    # --- 4. 初始化溫度場 ---
    T = np.ones((nz, ny, nx)) * T_ambient
    T[0, :, :] = T_bottom_heat  # 固定底部邊界條件 (Dirichlet)

    # --- 5. 核心計算：疊代求解 (使用各向異性調和平均) ---
    max_iter = 1000
    tolerance = 1e-4
    
    print(f"開始模擬... 網格大小: {nx}x{ny}x{nz}")

    for i in range(max_iter):
        T_old = T.copy()

        # 遍歷內點 (z從1到nz-1, x/y避開邊緣)
        for z in range(1, nz):
            # 取得鄰居索引
            zm, zp = z-1, min(z+1, nz-1)
            
            # 對於每個內部節點 (y, x)
            # 這裡簡化為向量化運算提高速度 (只針對 y, x 平面)
            for y in range(1, ny-1):
                for x in range(1, nx-1):
                    
                    # 計算 6 個方向的調和平均 k (Harmonic Mean)
                    # 這是為了確保界面熱通量連續 Q = k_eff * dT
                    ke = 2*k_grid[z,y,x]*k_grid[z,y,x+1] / (k_grid[z,y,x]+k_grid[z,y,x+1])
                    kw = 2*k_grid[z,y,x]*k_grid[z,y,x-1] / (k_grid[z,y,x]+k_grid[z,y,x-1])
                    kn = 2*k_grid[z,y,x]*k_grid[z,y+1,x] / (k_grid[z,y,x]+k_grid[z,y+1,x])
                    ks = 2*k_grid[z,y,x]*k_grid[z,y-1,x] / (k_grid[z,y,x]+k_grid[z,y-1,x])
                    kd = 2*k_grid[z,y,x]*k_grid[z-1,y,x] / (k_grid[z,y,x]+k_grid[z-1,y,x])
                    
                    if z == nz-1:
                        # --- 頂部邊界：套用牛頓冷卻定律 (Robin Boundary) ---
                        # 傳導進來的熱 = 散失到空氣的熱
                        # k*(T_p - T_down)/dz = h*(T_ambient - T_p)
                        # 解出 T_p:
                        cond_term = kd * T[z-1, y, x] / dz
                        conv_term = h_conv * T_ambient
                        T[z, y, x] = (cond_term + conv_term) / (kd/dz + h_conv)
                    else:
                        # --- 中間層：Poisson 方程離散化 ---
                        ku = 2*k_grid[z,y,x]*k_grid[z+1,y,x] / (k_grid[z,y,x]+k_grid[z+1,y,x])
                        
                        # 基於熱阻權重的平衡公式 (1/R * dT = 0)
                        denom = (ke+kw)/dx**2 + (kn+ks)/dy**2 + (ku+kd)/dz**2
                        num = (ke*T[z,y,x+1] + kw*T[z,y,x-1])/dx**2 + \
                              (kn*T[z,y+1,x] + ks*T[z,y-1,x])/dy**2 + \
                              (ku*T[z+1,y,x] + kd*T[z-1,y,x])/dz**2
                        T[z, y, x] = num / denom

        # 檢查收斂
        diff = np.abs(T - T_old).max()
        if diff < tolerance:
            print(f"收斂於第 {i} 次疊代. 殘差: {diff:.6e}")
            break
            
    return T, k_grid

# --- 6. 執行模擬與可視化 ---
T_result, k_map = simulate_pcb_thermal()

# 繪製頂層溫度分佈
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.title("Top Layer Temperature (K)")
plt.imshow(T_result[-1, :, :], cmap='hot', origin='lower')
plt.colorbar(label='Temperature (K)')

plt.subplot(1, 2, 2)
plt.title("PCB Copper Layout (Top Layer)")
plt.imshow(k_map[-1, :, :], cmap='binary', origin='lower')
plt.colorbar(label='Conductivity k')

plt.tight_layout()
plt.show()