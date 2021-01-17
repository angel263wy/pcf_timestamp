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

def log(filename, context):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(context)
        f.write('\n')
        print(context)


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
    log(fout, '--------------------')

# filename = 'dpc1.xls'

# filelist = glob.glob(f'DPC-DPC-INFO-2021*.xls')
current_dir = Path.cwd()
dirs = glob.glob(f'{current_dir}/SAT_NET_*')

out = f'DPC帧连续判断结果-{now}.txt'
# with open(out, 'a+', encoding='utf-8') as f:
#     pass



for dir in dirs:
    fname = glob.glob(f'{dir}/DPC-DPC-INFO-2021*.xls')
    if len(fname) == 0:
        pass
    else:        
        frame_check(fname[0], out)
    
os.system('start'+ ' ' + out)    
