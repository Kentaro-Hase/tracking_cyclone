# -*- coding:utf-8 -*-
'''
2018/04/24 Kentaro Hase
低気圧の抽出を行うスクリプトとして作成。
抽出する低気圧の年のgribファイルを必要とします。
基準値データとして'yyyy-lcl90.npz'または基準値を作成する為のgribファイルを必要とします。
抽出した低気圧のデータは'cyclone.npz'に格納します。
'''
# トラッキングを行う開始年・終了年
syear = 2006
eyear = 2017

# Libraries
from pygrib import open as pgo
from datetime import datetime, timedelta
from scipy.stats import norm
from os import path
import numpy as np
import sys

# 距離を算出する関数
'''
（参考）森口繁一，宇田川銈久，一松信（1957）「岩波　数学公式Ⅱ」，岩波書店，p200-p202
地球を球と仮定し，球面三角法の余弦法則，正接法則を利用してA点（東経lon1(deg), 北緯lat1(deg)）から
B点（東経lon2(deg), 北緯lat2(deg)）に対する距離（m）を算出する関数です。
'''
def cal_dis(lon1, lat1, lon2, lat2):
    _R = 6378137.
    _a = 0.5 * np.pi - np.radians(lat2)
    _b = 0.5 * np.pi - np.radians(lat1)
    _C = np.radians(lon2 - lon1)

    _c = np.arccos(np.around(np.cos(_a) * np.cos(_b) + np.sin(_a) * np.sin(_b) * np.cos(_C), decimals=10))
    _l = _R * _c

    return _l

# 低気圧の抽出
time = datetime(syear, 3, 1) - timedelta(hours=30)
endt = datetime(eyear, 6, 1, 6)
dt = timedelta(hours=6)
t = int(0)

while time <= endt:
    JST = time + timedelta(hours=9)
    y, m = time.year, time.month

    # 基準値
    if 'lcl90' in locals():
        pass
    else:
        sy =  ((y - 1) // 10 - 3) * 10 + 1
        f = '{0:04d}-lcl90.npz'.format(sy)
        if path.exists(f):
            lcl90 = np.zeros((375, 37, 45))
            lcl90[:, 4:-4, 8:-8] = np.load(f)['lcl90']  # 緯度方向に南北5度ずつ，経度方向に東西10度ずつ広くとる
        else:
            print('download-grib.pyを先に実行してください。')
            sys.exit()  # スクリプトの終了
    lcl = lcl90[t].reshape(-1)
    
    # Data Load
    if y < 2014:
        grb = pgo("./anl_surf125.002_prmsl.{0:04d}010100_{0:04d}123118".format(y))
        diff_h = time - datetime(y, 1, 1)
        T = int(diff_h.total_seconds() / 21600)
    elif m == 2:
        if ((y % 4 == 0) & (y % 100 != 0)) | (y % 400 == 0):
            grb = pgo("./anl_surf125.002_prmsl.{0:04d}020100_{0:04d}022918".format(y))
        else:
            grb = pgo("./anl_surf125.002_prmsl.{0:04d}020100_{0:04d}022818".format(y))
            diff_h = time - datetime(y, 2, 1)
            T = int(diff_h.total_seconds() / 21600)
    elif m == 3:
        grb = pgo("./anl_surf125.002_prmsl.{0:04d}030100_{0:04d}033118".format(y))
        diff_h = time - datetime(y, 3, 1)
        T = int(diff_h.total_seconds() / 21600)
    elif m == 4:
        grb = pgo("./anl_surf125.002_prmsl.{0:04d}040100_{0:04d}043018".format(y))
        diff_h = time - datetime(y, 4, 1)
        T = int(diff_h.total_seconds() / 21600)
    elif m == 5:
        grb = pgo("./anl_surf125.002_prmsl.{0:04d}050100_{0:04d}053118".format(y))
        diff_h = time - datetime(y, 5, 1)
        T = int(diff_h.total_seconds() / 21600)
    elif m == 6:
        grb = pgo("./anl_surf125.002_prmsl.{0:04d}060100_{0:04d}063018".format(y))
        diff_h = time - datetime(y, 6, 1)
        T = int(diff_h.total_seconds() / 21600)
    
    d = grb.select()[T]
    if 'dis' in locals():
        slpd, _, _ = d.data(lat1=15, lat2=60, lon1=110, lon2=165)
    else:
        slpd, lat, lon = d.data(lat1=15, lat2=60, lon1=110, lon2=165)
        shape = slpd.shape
        lat = lat.reshape(-1)
        lon = lon.reshape(-1)
        dis = np.empty((int(lon.shape[0]), int(lon.shape[0])))
        for i in range(len(lat[:])):
            lon2 = np.ones(lon.shape) * lon[i]
            lat2 = np.ones(lat.shape) * lat[i]
            dis[i, :] = cal_dis(lon, lat, lon2, lat2) * 1.0e-03

    # 対象グリッドの気圧が周囲300km以内で最も小さく，かつ基準値よりも小さい場合，対象グリッドを低気圧の中心とする。
    for i in range(lat.reshape(-1).shape[0]):
        kyori = dis[i, :]
        reslp = slpd.reshape(-1) * 1.0e-02

        loc_lon = lon[kyori == 0]
        loc_lat = lat[kyori == 0]        
        loc_slp = reslp[kyori == 0]

        slp_300 = reslp[kyori <= 300]
        lon_300 = lon[kyori <= 300]
        lat_300 = lat[kyori <= 300]
        min_slp = np.min(slp_300)
        min_loc = np.where(slp_300 == min_slp)
        
        if loc_slp == min_slp and loc_slp < lcl[kyori == 0]:
            # 最低気圧が同じ地点が複数ある場合，緯度・経度で平均の座標を低気圧の中心とする。
            if len(min_loc[0]) > 1:
                min_lon = lon_300[min_loc]
                min_lat = lat_300[min_loc]
                loc_lon = np.mean(min_lon)
                loc_lat = np.mean(min_lat)
            else:
                pass
            
            if 'v' in locals():
                same_loc = np.where(v['slp'] == loc_slp)
                same_lat = v['lat'][same_loc]
                same_lon = v['lon'][same_loc]                
                # 同じ時刻，周囲300km以内に低気圧が既にある場合，今回の低気圧は記録しない。
                if len(same_lon) == 0:
                    v = np.append(v, np.array([(loc_lon, loc_lat, loc_slp, JST)],
                                               dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]')]), axis=0)
                else:
                    same_place = np.where((v['lon'] == loc_lon) & (v['lat'] == loc_lat))
                    same_dis = cal_dis(loc_lon, loc_lat, same_lon, same_lat)
                    if len(v['lon'][same_place]) > 0:
                        pass
                    elif same_dis.min() > 300:
                        v = np.append(v, np.array([(loc_lon, loc_lat, loc_slp, JST)],
                                                dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]')]), axis=0)
                    else:
                        pass
            else:
                v = np.array([(loc_lon, loc_lat, loc_slp, JST)],
                               dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]')])
                
        else:
            pass
        
    if 'v' in locals():
        # print(v)  # 解析状況を確認したい方はこの行のコメントアウトを解除してください。
        if 'cloc' in locals():
            cloc = np.append(cloc, v, axis=0)
        else:
            cloc = np.copy(v)
        del v
    else:
        pass
    
    # 次の時刻へ
    if time == datetime(y, 6, 1, 6):
        t = int(0)
        time = datetime(y + 1, 3, 1) - timedelta(hours=12)
        del JST, slpd
        if y % 10 == 0:
            del lcl90
        else:
            pass
    else:
        t += int(1)
        del JST, slpd
        time += dt

# 保存
np.savez_compressed('cyclone.npz', lon=cloc['lon'], lat=cloc['lat'], slp=cloc['slp'], JST=cloc['JST'])
print('Finish making cyclone.npz.')
