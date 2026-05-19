import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import scipy.interpolate as interp
from sklearn.linear_model import LinearRegression
import scipy.constants as const
# datas = pd.read_csv('Pomiary\\2026_05_07\\ITO_PEDOT_PSS_MAPbI3_PCBM_PDINO_Ag_Light_s3b_p1_p2_p2_p3_p4_p7_p8_p9_p10.dat',sep = '\t' )
datas = pd.read_csv('Pomiary\\2026_05_06\\ITO_PEDOT_PSS_MAPbI3_PCBM_PDINO_Ag_Light_s1_p1_p2_p3_p4_p7_p8_p9_p10.csv',sep = '\t' )
# datas = pd.read_csv('Pomiary\\2026_05_06\\ITO_PEDOT_PSS_MAPbI3_PCBM_PDINO_Ag_Light2_s1_p1_p2_p3_p4_p7_p8_p9_p10.csv',sep = '\t' )
datas_dark = pd.read_csv('Pomiary\\2026_05_06\\ITO_PEDOT_PSS_MAPbI3_PCBM_PDINO_Ag_dark_s1_p2_p3_p4_p7_p8_p9_p10.dat',sep = '\t' )
for i, col in enumerate(datas_dark.columns[1:]):
    datas_dark['ln_'+str(i)] = np.log(datas_dark[col])


print(datas.columns)
print(datas.head())
for i,col in enumerate(datas.columns[1:]):
    datas["power"+str(i)] = datas[col] * datas['voltage']
    plt.plot(datas_dark['voltage'], datas_dark[col], label=col)
    # plt.plot(datas_dark['voltage'], datas_dark['ln_'+str(i)], label=col+" dark", linestyle='--')
    model = LinearRegression()
    model.fit(datas_dark['voltage'][10:40].values.reshape(-1, 1), datas_dark['ln_'+str(i)][10:40].values.reshape(-1, 1))
    n = const.e/(const.k*(const.zero_Celsius+25)*model.coef_[0][0] )
    print(f'Ideality factor for {col}: {n:.4f}')
    print(f'Saturation current for {col}: {np.exp(model.intercept_[0]):.4e} A')
    print(f'Temperature for {col}: {const.zero_Celsius+25:.2f} K')
    I0 = np.exp(model.intercept_[0])
    plt.title('Current vs Voltage')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (mA)')
    plt.grid()
    plt.legend()
    xy = interp.interp1d(datas['voltage'][0:datas['voltage'].shape[0]//2], datas[col][0:datas['voltage'].shape[0]//2], kind='cubic')
    yx = interp.interp1d(datas[col][0:datas['voltage'].shape[0]//2], datas['voltage'][0:datas['voltage'].shape[0]//2], kind='cubic')
    I0 = xy(0)
    V0 = yx(0)
    print(f'Short Circuit Current for {col}: {I0:.4f} mA')
    print(f'Open Circuit Voltage for {col}: {V0:.4f} V')

    max_power = datas["power"+str(i)][0:datas['voltage'].shape[0]//2].min()
    max_power_index = datas["power"+str(i)][0:datas['voltage'].shape[0]//2].idxmin()
    max_power_voltage = datas['voltage'][max_power_index]
    max_power_current = datas[col][max_power_index]
    print(f'Max Power for {col}: {max_power:.4f} W at Voltage: {max_power_voltage:.4f} V and Current: {max_power_current:.4f} A')
    filfactor = max_power / (I0 * V0)
    print(f'Fill Factor for {col}: {filfactor:.4f}')
    etha = max_power / (100 * (0.2 * 0.2))*100
    print(f'Efficiency for {col}: {etha:.4f}')  
    # plt.scatter(max_power_voltage, max_power_current, color='red', label=f'Max Power: {max_power:.4f} W')
    print("--------------------------------------------------")
    # plt.scatter([V0,0], [0,I0], color='green')
    plt.show()


plt.figure(figsize=(10,6))
plt.plot( datas['voltage'], datas['series1'])
plt.plot( datas['voltage'], datas['series2'])
plt.plot( datas['voltage'], datas['series3'])
plt.plot( datas['voltage'], datas['series4'])
plt.plot( datas['voltage'], datas['series5'])
plt.plot( datas['voltage'], datas['series6'])
plt.plot( datas['voltage'], datas['series7'])
plt.plot( datas['voltage'], datas['series8'])
plt.plot( datas['voltage'], datas['series9'])
plt.title('Current vs Voltage')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
plt.grid()
plt.show()


