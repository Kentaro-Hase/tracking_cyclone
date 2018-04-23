# -*- coding:utf-8 -*-
'''
2018/04/24 Kentaro Hase
ダウンロードを行い基準値を作成するスクリプトとして作成。
基準値データ'yyyy-lcl90.npz'を作成し，['lcl90']にデータを格納する。
（yyyyは基準値作成に使用した最初の年の4桁）
'''
# トラッキングを行う開始年・終了年
syear = 2006
eyear = 2017

# Libraries
from sys import argv, stdout
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor
from os import path, remove
from datetime import datetime, timedelta
from pygrib import open as pgo
from scipy.stats import norm
from copy import copy as cp
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
        print(_sUTC)
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

# 基準値作成
while syear <= eyear:
    if 'lcl90' in locals():
        pass
    else:
        lcl90 = cal_lcl90(syear)

    if syear == eyear or syear % 10 == 0:
        sy = ((syear - 1) // 10 - 3) * 10 + 1 # 使用する気候値の最初の年
        np.savez_compressed('{0:04d}-lcl90.npz'.format(sy), lcl_90=lcl90)   # 'yyyy-lcl90.npz'を作成し，['lcl90']にデータを格納
        del sy, lcl90
    else:
        pass
    sy += int(1)
