import pandas as pd
import numpy as np
import time
import os

dpc_file = 'dpc.csv'
posp_file = 'posp.csv'

# POSP起始圈数 即第一次交火的圈数 
start_line = 57  
# 轨道计数
orbit_dpc = 12
orbit_posp = '0x00 0C'
# csv文件格式
# seps = '\t'  # 制表符为 '\t'   逗号  ','
seps = ','

now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

# 导入文件
pd_dpc = pd.read_csv(dpc_file, header=0, sep=seps)  # encoding='GB2312'
pd_posp =  pd.read_csv(posp_file, header=0, sep=seps)  # encoding='GB2312'

# dpc时间标签计算(输出)
dpc_time = pd_dpc.loc[:, ['运行轨序号', '帧计数', 'GPS秒脉冲整秒时间码', '秒脉冲内自守时计数', '一圈内图像序号']]

# 挑选数据 选偶数帧
dpc_time = dpc_time[(dpc_time['一圈内图像序号'] % 2 ) == 0 ]

dpc_time['DPC时间标签'] = dpc_time['GPS秒脉冲整秒时间码'] + dpc_time['秒脉冲内自守时计数'] / 1000000

# 重新索引 方便组合
dpc_time.index = np.arange(len(dpc_time['DPC时间标签']))

# dpc_time.to_csv('time_dpc-'+now+'.csv', index=False, encoding='GB2312')


# posp时间标签计算(输出)
posp_time = pd_posp.loc[start_line:, ['轨道计数', '圈计数', 'GPS整秒时刻.190', 'GPS本地计时.190']]

posp_time['POSP时间标签'] = posp_time['GPS整秒时刻.190'] + posp_time['GPS本地计时.190'] / 1000000
posp_time['筛选编号'] = np.arange(len(posp_time['圈计数'])) % 15

# 挑选数据 对15取余数 选前7个
posp_time = posp_time[posp_time['筛选编号'].isin([0,1,2,3,4,5,6])]

# 重新索引 方便组合
posp_time.index = np.arange(len(posp_time['POSP时间标签']))

# posp_time.to_csv('time_posp-'+now+'.csv', index=False, encoding='GB2312')


# 两部分数据组合 输出
timpstamp = pd.concat([dpc_time, posp_time], axis=1)

fout = 'pcf_timestamp-'+now+'.csv'
timpstamp.to_csv(fout, index=False, encoding='GB2312')
os.system('start'+ ' ' + fout)


print('end')