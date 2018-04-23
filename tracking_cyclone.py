# -*- coding:utf-8 -*-
'''
2018/04/23 Kentaro Hase コードを一つのスクリプトにまとめる為に作成
'''
# トラッキングを行う開始年・終了年
syear = 2006
eyear = 2007

# Libraries
from sys import argv, stdout
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor
from os import path, remove, makedirs
from copy import copy as cp
from pygrib import open as pgo
from datetime import datetime, timedelta
from scipy.stats import norm
from pandas import DataFrame
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

# Cookie処理
cj = MozillaCookieJar()
account = urlencode({'email':argv[1], 'password':argv[2], 'action':'login'}).encode('utf-8')
opener = build_opener(HTTPCookieProcessor(cj))
login = opener.open("https://rda.ucar.edu/cgi-bin/login", account)
cj.clear_session_cookies()
cj.save("auth.rda.ucar.edu", True, True)

# ダウンロードを行う関数
def grib_download(year):
    if year < 2014:
        _f = ['anl_surf125.002_prmsl.{0}010100_{0}123118'.format(year)]
    elif ((year % 4 == 0) & (year % 100 != 0)) | (year % 400 == 0):
        _f = ['anl_surf125.002_prmsl.{0}020100_{0}022918'.format(year),
             'anl_surf125.002_prmsl.{0}030100_{0}033118'.format(year),
             'anl_surf125.002_prmsl.{0}040100_{0}043018'.format(year),
             'anl_surf125.002_prmsl.{0}050100_{0}053118'.format(year),
             'anl_surf125.002_prmsl.{0}060100_{0}063018'.format(year)]
    else:
        _f = ['anl_surf125.002_prmsl.{0}020100_{0}022818'.format(year),
             'anl_surf125.002_prmsl.{0}030100_{0}033118'.format(year),
             'anl_surf125.002_prmsl.{0}040100_{0}043018'.format(year),
             'anl_surf125.002_prmsl.{0}050100_{0}053118'.format(year),
             'anl_surf125.002_prmsl.{0}060100_{0}063018'.format(year)]
    for i in _f:
        if path.exists(i):
            continue
        else:
            URL = 'http://rda.ucar.edu/data/ds628.0/anl_surf125/{0}/{1}'.format(year, i)
            stdout.write('Downloading {0} ...\n'.format(i))
            stdout.flush()
            infile = opener.open(URL)
            outfile = open(i, 'wb')
            outfile.write(infile.read())
            outfile.close()

# Download
sy = ((syear - 1) // 10 - 3) * 10 + 1    # 使用する気候値の最初の年
if eyear % 10:
    ey = (eyear // 10 - 1) * 10    # 使用する気候値の最後の年
else:
    ey = (eyear // 10) * 10        # 使用する気候値の最後の年

while sy <= ey:
    grib_download(sy)   # 気候値を算出する為のファイルをダウンロード
    sy += int(1)

time = cp(syear)
while time <= eyear:
    grib_download(time) # 抽出したい年のファイルをダウンロード
    time += int(1)

if path.exists("auth.rda.ucar.edu"):
    remove("auth.rda.ucar.edu")
else:
    pass

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

# tracking
time = datetime(syear, 3, 1) - timedelta(hours=30)
endt = datetime(eyear, 6, 1, 6)
dt = timedelta(hours=6)
t = int(0)
num = int(1)

while time <= endt:
    JST = time + timedelta(hours=9)
    JST_1 = JST - dt

    # 該当時刻の低気圧
    lon = cloc['lon'][cloc['JST'] == JST]
    lat = cloc['lat'][cloc['JST'] == JST]
    slp = cloc['slp'][cloc['JST'] == JST]
    
    # 6時間前の低気圧
    lon_1 = cloc['lon'][cloc['JST'] == JST_1]
    lat_1 = cloc['lat'][cloc['JST'] == JST_1]
    slp_1 = cloc['slp'][cloc['JST'] == JST_1]

    for i in range(len(slp)):
        # 6時間前に低気圧がある場合
        if len(slp_1) > 0:
            c_dis = cal_dis(lon[i], lat[i], lon_1, lat_1) * 1.0e-03
            loc_1 = np.where((c_dis == np.min(c_dis)) & (c_dis <= 500.)) # 最も距離が小さく，500km以内
            # 500km以内の低気圧がない場合            
            if loc_1[0].shape[0] == 0:
                b = np.array([(lon[i], lat[i], slp[i], JST, 6., 0., 0., num, 6.)], dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]'), ('life', 'i2'), ('dslp', 'f4'), ('v', 'f4'), ('num', 'i4'), ('max_life', 'i2')])
                num += int(1)
            # 500km以内の低気圧が複数ある場合
            elif loc_1[0].shape[0] > 1:
                b_lon = lon_1[loc_1]
                b_lat = lat_1[loc_1]
                b_slp = slp_1[loc_1]
                b_loc = np.where(b_lon == np.min(b_lon))
                # 西の方あるいは南の方にある低気圧の方を選択
                if len(b_lat[b_loc]) > 1:
                    b_loc = np.where((b_lon == np.min(b_lon)) & (b_lat == np.min(b_lat)))
                else:
                    pass
                b_lon2 = b_lon[b_loc]
                b_lat2 = b_lat[b_loc]
                b_slp2 = b_slp[b_loc]
                dslp = slp[i] - b_slp2
                b_loc2 = np.where((c['lon'] == b_lon2) & (c['lat'] == b_lat2) & (c['JST'] == JST_1))
                b_life = c['life'][b_loc2]
                b_num = c['num'][b_loc2]
                life = b_life + int(6)
                v = np.min(c_dis) / 6.
                b = np.array([(lon[i], lat[i], slp[i], JST, life, dslp, v, b_num, life)], dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]'), ('life', 'i2'), ('dslp', 'f4'), ('v', 'f4'), ('num', 'i4'), ('max_life', 'i2')])
                del life, dslp, v, b_loc, b_lon, b_lon2, b_lat, b_lat2, b_slp, b_slp2, b_life, b_num
            # 500km以内の低気圧が1つだけある場合
            else:
                b_loc = np.where((c['lon'] == lon_1[loc_1]) & (c['lat'] == lat_1[loc_1]) & (c['JST'] == JST_1))
                life = c['life'][b_loc] + int(6)
                dslp = slp[i] - c['slp'][b_loc]
                v = np.min(c_dis) / 6.
                b = np.array([(lon[i], lat[i], slp[i], JST, life, dslp, v, c['num'][b_loc], life)], dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]'), ('life', 'i2'), ('dslp', 'f4'), ('v', 'f4'), ('num', 'i4'), ('max_life', 'i2')])
                del life, dslp, v
            del loc_1

        # 6時間前に低気圧がない場合    
        else:
            b = np.array([(lon[i], lat[i], slp[i], JST, 6., 0., 0., num, 6.)], dtype=[('lon', 'f4'), ('lat', 'f4'), ('slp', 'f4'), ('JST', 'datetime64[h]'), ('life', 'i2'), ('dslp', 'f4'), ('v', 'f4'), ('num', 'i4'), ('max_life', 'i2')])
            num += int(1)

        if 'c_now' in locals():
            c_now = np.append(c_now, b, axis=0)
        else:
            c_now = np.copy(b)
        del b

    # 同時刻に同じナンバーの低気圧が複数あるとき，vが最小でない低気圧を, vが同じならより西にある低気圧を新たな低気圧であると変更する
    if 'c_now' in locals():    
        num_min = c_now['num'].min()
        num_max = c_now['num'].max()
        while num_min <= num_max:
            num_loc = np.where(c_now['num'] == num_min)
            # 同じナンバーの低気圧が複数あるとき，vが最小でない低気圧を新たな低気圧であると変更する
            if len(c_now['v'][num_loc]) > 1:
                v_min = np.min(c_now['v'][num_loc])
                c_same = np.where((c_now['num'] == num_min) & (c_now['v'] == v_min))
                c_notsame = np.where((c_now['num'] == num_min) & (c_now['v'] > v_min))
                c_now['life'][c_notsame] = 6.
                c_now['dslp'][c_notsame] = 0.
                c_now['v'][c_notsame] = 0.
                c_now['num'][c_notsame] = num
                c_now['max_life'][c_notsame] = 6.
                num += int(1)
                # vが同じ低気圧が複数あるとき，西にある低気圧を新たな低気圧であると変更する
                if len(c_now['v'][c_same]) > 1:
                    lon_max = np.max(c_now['lon'][c_same])
                    c_notsame2 = np.where((c_now['num'] == num_min) & (c_now['v'] == v_min) & (c_now['lon'] < lon_max))
                    c_now['life'][c_notsame2] = 6.
                    c_now['dslp'][c_notsame2] = 0.
                    c_now['v'][c_notsame2] = 0.
                    c_now['azi'][c_notsame2] = np.nan
                    c_now['num'][c_notsame2] = num
                    c_now['max_life'][c_notsame2] = 6.
                    num += int(1)
                    del lon_max, c_notsame2
                else:
                    pass
                del v_min, c_same, c_notsame            
            else:
                pass
            del num_loc
            num_min += int(1)
        del num_min, num_max
    
        # cに記録
        if 'c' in locals():
            c = np.append(c, c_now, axis=0)
        else:
            c = np.copy(c_now)
        print(c_now)
        del c_now
    
    else:
        pass
            
    # 次の時刻へ
    if time == datetime(y, 5, 31, 18):
        t = int(0)
        time = datetime(y + 1, 3, 1) - timedelta(hours=12)
        del JST, lon, lat, slp, JST_1, lon_1, lat_1, slp_1
    else:
        t += int(1)
        del JST, lon, lat, slp, JST_1, lon_1, lat_1, slp_1
        time += dt

# 低気圧の寿命（同じナンバーの低気圧の中で最も大きいlifeの値を低気圧の寿命とする）
for i in range(np.max(c['num'])):
    same_num = np.where(c['num'] == i + 1)
    try:
        c['max_life'][same_num] = np.max(c['life'][same_num])
    except:
        print('Something error in cyclone {0}'.format(i))

# csvファイルとして保存
df = DataFrame({'経度(deg)' : c['lon'],
                '緯度(deg)' : c['lat'],
                '海面更正気圧(hPa)' : c['slp'],
                '日本時刻' : c['JST'],
                '低気圧発生からの時間(h)' : c['life'],
                '気圧変動量(hPa/h)' : c['dslp'],
                '低気圧の移動速度(km/h)' : c['v'],
                '低気圧番号' : c['num'],
                '低気圧の寿命(h)' : c['max_life']})
df = df[df['低気圧の寿命(h)'] >= 24]    # 24時間以上持続したものを低気圧として抽出
df = df.ix[:, ['低気圧番号', '日本時刻', '経度(deg)', '緯度(deg)', '海面更正気圧(hPa)', '低気圧発生からの時間(h)', '気圧変動量(hPa/h)', '低気圧の移動速度(km/h)', '低気圧の寿命(h)']]   # 行のソート
df = df.sort_values(by=['低気圧番号'])  # 列のソート
df = df.set_index('低気圧番号')
df.to_csv('./tracking-cyclone.csv')
print("Finish making ./tracking-cyclone.csv")

# Basemap
slon, elon, slat, elat = 120, 155, 20, 55
nlon, nlat = 29, 29
lon = np.linspace(slon, elon, nlon)
lat = np.linspace(slat, elat, nlat)

mp = Basemap(projection='cyl', llcrnrlon=slon, urcrnrlon=elon, llcrnrlat=slat, urcrnrlat=elat, resolution='i')
X, Y = np.meshgrid(lon, lat)
x, y = mp(X, Y)
xlon, ylat = x[0, :], y[:, 0]

# matplotlibで低気圧トラックを描画
num_min = df['num'].min()
num_max = df['num'].max()
if path.exists('track'):
    pass
else:
    makedirs('track')

while num_min <= num_max:
    print('num =', num_min)
    if df['num'][df['num'] == num_min].count() == 0:
        pass
    else:
        c_lon, c_lat = mp(np.array(df['lon'][df['num'] == num_min]), np.array(df['lat'][df['num'] == num_min]))
        c_start = df['JST'][df['num'] == num_min].min()
        c_end = df['JST'][df['num'] == num_min].max()
        fonts ={'family' : 'Times New Roman', 'size' : 25}
        plt.rc('font', **fonts)
        fig = plt.figure(figsize=(12, 12))

        ax = fig.add_subplot(1, 1, 1)
        plot = ax.plot(c_lon, c_lat, marker='o', color='k', linewidth=3)
        mp.drawcoastlines()
        mp.drawmeridians(np.arange(0., 361., 5.), labels=[True, False, False, True], linewidth=0.01)
        mp.drawparallels(np.arange(-90., 91., 5.), labels=[True, False, False, True], linewidth=0.01)

        ax.set_title('{0:04d}/{1:02d}/{2:02d} {3:02d}:00 - {4:02d}/{5:02d} {6:02d}:00 JST'.format(c_start.year, c_start.month, c_start.day, c_start.hour, c_end.month, c_end.day, c_end.hour), fontsize=30)
        
        plt.savefig('./track/track-{0:04d}.png'.format(num_min))
        plt.close('all')
        
    num_min += int(1)

print('Finish.')
