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

# 気候値データから基準値を作成する関数
def cal_lcl90(year):
    print('Making lower confidence limit data...')
    _sy =  ((year - 1) // 10 - 3) * 10 + 1
    _ey = _sy + 29
    _sUTC = datetime(_sy, 3, 1) - timedelta(hours=30)
    _eUTC = datetime(_ey, 6, 1, 6) 
    _dt = timedelta(hours=6)

    while _sUTC <= _eUTC:
        _y, _m = _sUTC.year, _sUTC.month
        _dh = _sUTC - (datetime(_y, 3, 1) - timedelta(hours=30))
        _t = int(_dh.total_seconds() / 21600)
        if '_v' in locals():
            pass
        else:
            _v = np.zeros(1, dtype=[('year', 'i2'),
                                ('slp', 'f4', (375, 37, 45))])
            _v['year'] = _y
        
        # Data load(Mean Sea Level Pressure[Pa])
        if _y < 2014:
            _grb = pgo("./anl_surf125.002_prmsl.{0:04d}010100_{0:04d}123118".format(_y))
            _diff_h = _sUTC - datetime(_y, 1, 1)
            _T = int(_diff_h.total_seconds() / 21600)
        elif _m == 2:
            if ((_y % 4 == 0) & (_y % 100 != 0)) | (_y % 400 == 0):
                _grb = pgo("./anl_surf125.002_prmsl.{0:04d}020100_{0:04d}022918".format(_y))
            else:
                _grb = pgo("./anl_surf125.002_prmsl.{0:04d}020100_{0:04d}022818".format(_y))
                _diff_h = _sUTC - datetime(_y, 2, 1)
                _T = int(_diff_h.total_seconds() / 21600)
        elif _m == 3:
            _grb = pgo("./anl_surf125.002_prmsl.{0:04d}030100_{0:04d}033118".format(_y))
            _diff_h = _sUTC - datetime(_y, 3, 1)
            _T = int(_diff_h.total_seconds() / 21600)
        elif _m == 4:
            _grb = pgo("./anl_surf125.002_prmsl.{0:04d}040100_{0:04d}043018".format(_y))
            _diff_h = _sUTC - datetime(_y, 4, 1)
            _T = int(_diff_h.total_seconds() / 21600)
        elif _m == 5:
            _grb = pgo("./anl_surf125.002_prmsl.{0:04d}050100_{0:04d}053118".format(_y))
            _diff_h = _sUTC - datetime(_y, 5, 1)
            _T = int(_diff_h.total_seconds() / 21600)
        elif _m == 6:
            _grb = pgo("./anl_surf125.002_prmsl.{0:04d}060100_{0:04d}063018".format(_y))
            _diff_h = _sUTC - datetime(_y, 6, 1)
            _T = int(_diff_h.total_seconds() / 21600)

        _d = _grb.select()[_T]
        _slpd, _, _ = _d.data(lat1=15, lat2=60, lon1=110, lon2=165)
        _v['slp'][0][_t, :, :] = _slpd * 1.0e-02

        if _sUTC == datetime(_sUTC.year, 6, 1, 6):
            if '_sd' in locals():
                _sd = np.append(_sd, _v, axis=0)
            else:
                _sd = np.copy(_v)
            del _slpd, _v
            _sUTC = datetime(_sUTC.year + 1, 3, 1) - timedelta(hours=30)
        else:
            del _slpd
            _sUTC += _dt
    
    _mean = np.mean(_sd['slp'], axis=0)
    _std = np.std(_sd['slp'], axis=0)
    _lcl_90 = norm.interval(alpha=0.90, loc=_mean, scale=_std)[0]
    del _mean, _std
    return _lcl_90

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
            lcl90 = np.load(f)['lcl_90']
        else:
            lcl90 = cal_lcl90(y)
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
        relon = lon.reshape(-1)
        relat = lat.reshape(-1)
        reslp = slpd.reshape(-1) * 1.0e-02

        loc_lon = relon[kyori == 0]
        loc_lat = relat[kyori == 0]
        loc_slp = reslp[kyori == 0]

        slp_300 = reslp[kyori <= 300]
        lon_300 = relon[kyori <= 300]
        lat_300 = relat[kyori <= 300]
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
                loc = np.where((v['lon'] == loc_lon) & (v['lat'] == loc_lat))
                if len(v[loc]) == 0:
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
        print(v)
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
