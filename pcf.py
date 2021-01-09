import pandas as pd
import numpy as np
import time
import os

# ---参数设置部分-----
dpc_file = 'dpc.csv'
posp_file = 'posp.csv'

# POSP起始圈数 即第一次交火的圈数 
start_line = 50
# 轨道计数
orbit_dpc = 3
# orbit_posp = orbit_dpc

# POSP轨道 用dpc计数转hex后获得
orbit_posp = f'0x00 {orbit_dpc:X}' if orbit_dpc>15 else f'0x00 0{orbit_dpc:X}'
# orbit_posp = '0x00 0D'

# ---参数设置部分结束-----

now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

## 导入文件
## DPC UTF-8 CSV格式
pd_dpc = pd.read_csv(dpc_file, header=0, sep=',')  # encoding='GB2312'
## DPC GB2312格式 解包软件直接导出
# pd_posp =  pd.read_csv(posp_file, header=0, sep='\t')  # encoding='GB2312'

## POSP UTF-8 CSV格式
pd_posp = pd.read_csv(posp_file, header=0, sep=',')  # encoding='GB2312'
## POSP GB2312格式 解包软件直接导出
# pd_posp =  pd.read_csv(posp_file, header=0, sep='\t' ,encoding='GB2312')  # encoding='GB2312'


# --------DPC数据计算--------
# 切片取出用于计算的数据
dpc_time = pd_dpc.loc[:, ['运行轨序号', '帧计数', 'GPS秒脉冲整秒时间码', '秒脉冲内自守时计数', '一圈内图像序号']]

# 挑选数据 选轨道号 选偶数帧
dpc_time = dpc_time[dpc_time['运行轨序号']  == orbit_dpc ]
dpc_time = dpc_time[(dpc_time['一圈内图像序号'] % 2 ) == 0 ]

# 时间码计算
dpc_time['DPC时间标签'] = dpc_time['GPS秒脉冲整秒时间码'] + dpc_time['秒脉冲内自守时计数'] / 1000000

# 重新索引 方便组合
dpc_time.index = np.arange(len(dpc_time['DPC时间标签']))

# dpc_time.to_csv('time_dpc-'+now+'.csv', index=False, encoding='GB2312')

# --------POSP数据计算--------
# 切片取出用于计算的数据
posp_time = pd_posp.loc[:, ['轨道计数', '圈计数', '当前工作模式', 'GPS整秒时刻.190', 'GPS本地计时.190']]

# 挑选数据 选轨道号 选行数
posp_time = posp_time[posp_time['轨道计数']  == orbit_posp]
posp_time = posp_time.iloc[start_line: , :]

# 对15取余数 选前7个
posp_time['筛选编号'] = np.arange(len(posp_time['圈计数'])) % 15
posp_time = posp_time[posp_time['筛选编号'].isin([0,1,2,3,4,5,6])]

# 时间码计算
posp_time['POSP时间标签'] = posp_time['GPS整秒时刻.190'] + posp_time['GPS本地计时.190'] / 1000000

# 重新索引 方便组合
posp_time.index = np.arange(len(posp_time['POSP时间标签']))

# posp_time.to_csv('time_posp-'+now+'.csv', index=False, encoding='GB2312')


# 两部分数据组合 
timpstamp = pd.concat([dpc_time, posp_time], axis=1)


#计算时间差
timpstamp['观测时间差'] = timpstamp['DPC时间标签'] - timpstamp['POSP时间标签']
timpstamp = timpstamp.dropna(how='any')
# 输出
fout = 'pcf_timestamp-'+now+'.csv'
timpstamp.to_csv(fout, index=False, encoding='GB2312')
os.system('start'+ ' ' + fout)


print('end')