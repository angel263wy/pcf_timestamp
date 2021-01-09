import pandas as pd
import numpy as np
import time
import os

# ---参数设置部分-----
dpc_file = 'dpc.csv'
posp_file = 'posp.xls'

# 轨道计数
orbit_dpc = 13


# POSP轨道 用dpc计数转hex后获得
# orbit_posp = f'0x00 {orbit_dpc:X}' if orbit_dpc>15 else f'0x00 0{orbit_dpc:X}'
orbit_posp = orbit_dpc
# orbit_posp = '0x00 0D'

# ---参数设置部分结束-----

now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

## 导入文件
## DPC UTF-8 CSV格式
pd_dpc = pd.read_csv(dpc_file, header=0, sep=',')  # encoding='GB2312'
## DPC GB2312格式 解包软件直接导出
# pd_dpc =  pd.read_csv(dpc_file, header=0, sep='\t', encoding='GB2312')  # encoding='GB2312'

## POSP UTF-8 CSV格式
# pd_posp = pd.read_csv(posp_file, header=0, sep=',')  # encoding='GB2312'
## POSP GB2312格式 解包软件直接导出
pd_posp =  pd.read_csv(posp_file, header=0, sep='\t', encoding='GB2312')  # encoding='GB2312'


# --------DPC数据计算--------
# 切片取出用于计算的数据
print('--------DPC数据处理开始--------')
dpc_time = pd_dpc.loc[:, ['运行轨序号', '帧计数', 'GPS秒脉冲整秒时间码', '秒脉冲内自守时计数', '一圈内图像序号']]

# 挑选数据 选轨道号 选偶数帧
dpc_time = dpc_time[dpc_time['运行轨序号']  == orbit_dpc ]
# 重新索引 方便去回卷
dpc_time.index = np.arange(len(dpc_time['运行轨序号']))
# 去除回卷数据
''' 算法说明
i为当前帧计数指针 pt_index为上次帧计数指针 
如果两个指针帧计数之差为1 则连续 更新上次指针 
如果之差小于1 则表示有回卷 删除i行 pt不变 i继续增加 重新判断 
如果之差大于1 则表示有丢帧 提示后不处理
'''
pt_index = 0 # 索引指针  如果两个指针对应的数相等
for i in np.arange(1,len(dpc_time['帧计数'])):
    foo = dpc_time.loc[i, '帧计数'] - dpc_time.loc[pt_index, '帧计数']
    if foo == 1 : # 等于1 连续 更新指针
        pt_index = i
    else:  # 不等于1 有回卷 删行 不更新指针
        dpc_time.drop(i, axis=0, inplace=True)
        print(f'DPC有回卷 帧计数指针为{i} 连续指针为{pt_index}')        
print(f'--------DPC回卷处理完成 最后指针为{pt_index}--------')

dpc_time = dpc_time[(dpc_time['一圈内图像序号'] % 2 ) == 0 ]

# 时间码计算
dpc_time['DPC时间标签'] = dpc_time['GPS秒脉冲整秒时间码'] + dpc_time['秒脉冲内自守时计数'] / 1000000

# 重新索引 方便组合
dpc_time.index = np.arange(len(dpc_time['DPC时间标签']))

# dpc_time.to_csv('time_dpc-'+now+'.csv', index=False, encoding='GB2312')
print('--------DPC数据处理完成 POSP数据处理开始--------')

# --------POSP数据计算--------
# 切片取出用于计算的数据
posp_time = pd_posp.loc[:, ['轨道计数', '圈计数', '当前工作模式', 'GPS整秒时刻.190', 'GPS本地计时.190']]

# 挑选数据 选轨道号 选行数
posp_time = posp_time[posp_time['轨道计数']  == orbit_posp]
# posp_time = posp_time.iloc[start_line: , :]

# 重新索引 以便去除回卷数据 并且自动对齐整秒部分
posp_time.index = np.arange(len(posp_time['轨道计数']))

# 去除回卷数据
''' 算法说明
i为当前圈计数指针 pt_index为上次圈计数指针 
如果两个指针圈计数之差为1 则连续 更新上次指针 
如果之差小于1 则表示有回卷 删除i行 pt不变 i继续增加 重新判断 
如果之差大于1 则表示有丢帧 提示后不处理
'''
pt_index = 0 # 索引指针  如果两个指针对应的数相等
for i in np.arange(1,len(posp_time['圈计数'])):
    foo = posp_time.loc[i, '圈计数'] - posp_time.loc[pt_index, '圈计数']
    if foo == 1 : # 等于1 连续 更新指针
        pt_index = i
    else:
        posp_time.drop(i, axis=0, inplace=True)
        print(f'POSP有回卷 圈计数指针为{i} 连续指针为{pt_index}')
    # elif foo < 1:  # 小于1 有回卷 删行 不更新指针
    #     posp_time.drop(i, axis=0, inplace=True)
    #     print(f'POSP有回卷 圈计数指针为{i} 连续指针为{pt_index}')
    # else:
    #     print(f'POSP帧不连续 不连续指针{i}')
print(f'--------POSP回卷处理完成  最后指针为{pt_index}--------')        


# 如果整秒部分不一致 删除POSP首行数据重新判断 如果一致则退出循环
for i in np.arange(len(posp_time['圈计数'])):
    if dpc_time.loc[0, 'GPS秒脉冲整秒时间码'] != posp_time.loc[i, 'GPS整秒时刻.190']:
        posp_time.drop(i, axis=0, inplace=True)
    else:
        break

# 对15取余数 选前7个
posp_time['筛选编号'] = np.arange(len(posp_time['圈计数'])) % 15
posp_time = posp_time[posp_time['筛选编号'].isin([0,1,2,3,4,5,6])]

# 时间码计算
posp_time['POSP时间标签'] = posp_time['GPS整秒时刻.190'] + posp_time['GPS本地计时.190'] / 1000000

# 重新索引 方便组合
posp_time.index = np.arange(len(posp_time['POSP时间标签']))

# posp_time.to_csv('time_posp-'+now+'.csv', index=False, encoding='GB2312')
print('--------POSP数据处理完成--------')

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