# -*- coding: UTF-8 -*-
# Author      : WangYi
# Date        : 2021/01/11
# Description : dpc图像帧连续判定 
#               放入 SAT_NET 目录外 自动进入该目录找数据并判断
#               结果显示并写入日志文件


import pandas as pd
import numpy as np
import time
import os
import glob
from pathlib import Path

now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

# 日志记录
def log(filename, context):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(context)
        f.write('\n')
        print(context)


# 帧完整性检查
def frame_check(filename, fout):
    log(fout, f'文件名: {filename}')
    pd_csv =  pd.read_csv(filename, header=0, sep='\t', encoding='GB2312')  # encoding='GB2312'

    # 首帧指示
    a = pd_csv.loc[0, '运行轨序号']
    b = pd_csv.loc[0, '帧计数']
    c = pd_csv.loc[0, '工作流程表序号']
    d = pd_csv.loc[0, '源码.4']
    # context = f'首帧第{a}轨, 第{b}帧'
    log(fout, f'*首帧第{a}轨, 第{b}帧, {c}, GPS整秒时间{d}')
    # 帧连续判断
    for i in np.arange(1, len(pd_csv.index)):
        foo = pd_csv.loc[i, '帧计数'] - pd_csv.loc[i-1, '帧计数']
        if foo == 1 : # 帧连续 
            pass
        else:
            a = pd_csv.loc[i, '运行轨序号']
            b = pd_csv.loc[i, '帧计数']
            c = pd_csv.loc[i-1, '运行轨序号']
            d = pd_csv.loc[i-1, '帧计数']
            e = pd_csv.loc[i, '工作流程表序号']
            f = pd_csv.loc[i, '源码.4']
            log(fout, f'--帧不连续 当前第{a}轨第{b}帧, {e}, GPS整秒时间{f}, 之前第{c}轨第{d}帧')
    # 末帧提示
    a = pd_csv.loc[len(pd_csv.index)-1, '运行轨序号']
    b = pd_csv.loc[len(pd_csv.index)-1, '帧计数']
    c = pd_csv.loc[len(pd_csv.index)-1, '工作流程表序号']
    d = pd_csv.loc[len(pd_csv.index)-1, '源码.4']
    log(fout, f'*末帧第{a}轨, 第{b}帧, {c}, GPS整秒时间:{d}')
    


# 本底图像处理
def dkg_check(dkg_files, fout):
    if len(dkg_files) == 0 :
        log(fout, f'未找到本底图像')
    else:
        raw_data = np.fromfile(dkg_files[0], dtype=np.uint16)  # 读取一幅本底
        a, b = np.max(raw_data), np.min(raw_data)
        c, d = np.mean(raw_data), np.std(raw_data)
        log(fout, f'**** 单幅本底图像统计: 最大{a}, 最小{b}, 均值{round(c)}, 标准差{round(d)}')
        log(fout, '--------------------')

# filelist = glob.glob(f'DPC-DPC-INFO-2021*.xls')
current_dir = Path.cwd()
dirs = glob.glob(f'{current_dir}/SAT_NET_*')

out = f'DPC图像判断结果-{now}.txt'
# with open(out, 'a+', encoding='utf-8') as f:
#     pass



for dir in dirs:    
    fname = glob.glob(f'{dir}/DPC-DPC-INFO-2021*.xls')  # 辅助数据
    dkg_file = glob.glob(f'{dir}/RAW_ImageData/*_08.raw')  # 本底图像
    if len(fname) == 0:
        pass
    else:        
        frame_check(fname[0], out)
        dkg_check(dkg_file, out)
    
os.system('start'+ ' ' + out)    
