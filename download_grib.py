# -*- coding:utf-8 -*-
'''
2018/04/24 Kentaro Hase
ダウンロードを行い基準値を作成するスクリプトとして作成。
基準値データ'yyyy-lcl90.npz'を作成し，['lcl90']にデータを格納する。
（yyyyは基準値作成に使用した最初の年の4桁）
2018/04/25 Kentaro Hase 不具合を修正し更新
2018/05/07 Kentaro Hase 基準値作成における平均・標準偏差の計算方法を変更
2018/05/08 Kentaro Hase 不具合を修正し更新
2018/05/09 Kentaro Hase 標準偏差を標本標準偏差から母標準偏差に変更（気候値を母集団とみるため）
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
if eyear % 10 == 0:
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

# 基準値作成
while syear <= eyear:
    if 'lcl_90' in locals():
        pass
    else:
        print('Making lower confidence limit data...')
        sy = ((syear - 1) // 10 - 3) * 10 + 1
        ey = sy + 29
        sUTC = datetime(sy, 3, 1) - timedelta(hours=30)
        eUTC = datetime(ey, 6, 1, 6) 
        dt = timedelta(hours=6)
        T = int(0)

        slp_size = np.zeros((375, 29, 29))  # 標本サイズ
        slp_sum = np.zeros((375, 29, 29))   # 標本和
        slp_sum2 = np.zeros((375, 29, 29))  # 標本の2乗和

        while sUTC <= eUTC:
            print(sUTC, 'T =', T)
            y, m = sUTC.year, sUTC.month
            dh = sUTC - (datetime(y, 3, 1) - timedelta(hours=30))
            t = int(dh.total_seconds() / 21600)
            if 'v' in locals():
                pass
            else:
                v = np.zeros(1, dtype=[('year', 'i2'),
                                    ('slp', 'f4', (375, 29, 29))])
                v['year'] = y
            
            # Data load(Mean Sea Level Pressure[Pa])
            if y < 2014:
                grb = pgo("./anl_surf125.002_prmsl.{0:04d}010100_{0:04d}123118".format(y))
                diff_h = sUTC - datetime(y, 1, 1)
                t = int(diff_h.total_seconds() / 21600)
            elif m == 2:
                if ((y % 4 == 0) & (y % 100 != 0)) | (y % 400 == 0):
                    grb = pgo("./anl_surf125.002_prmsl.{0:04d}020100_{0:04d}022918".format(y))
                else:
                    grb = pgo("./anl_surf125.002_prmsl.{0:04d}020100_{0:04d}022818".format(y))
                    diff_h = sUTC - datetime(y, 2, 1)
                    t = int(diff_h.total_seconds() / 21600)
            elif m == 3:
                grb = pgo("./anl_surf125.002_prmsl.{0:04d}030100_{0:04d}033118".format(y))
                diff_h = sUTC - datetime(y, 3, 1)
                t = int(diff_h.total_seconds() / 21600)
            elif m == 4:
                grb = pgo("./anl_surf125.002_prmsl.{0:04d}040100_{0:04d}043018".format(y))
                diff_h = sUTC - datetime(y, 4, 1)
                t = int(diff_h.total_seconds() / 21600)
            elif m == 5:
                grb = pgo("./anl_surf125.002_prmsl.{0:04d}050100_{0:04d}053118".format(y))
                diff_h = sUTC - datetime(y, 5, 1)
                t = int(diff_h.total_seconds() / 21600)
            elif m == 6:
                grb = pgo("./anl_surf125.002_prmsl.{0:04d}060100_{0:04d}063018".format(y))
                diff_h = sUTC - datetime(y, 6, 1)
                t = int(diff_h.total_seconds() / 21600)

            d = grb.select()[t]
            slpd, _, _ = d.data(lat1=20, lat2=55, lon1=120, lon2=155)
            slp_size[T, :, :] += np.ones((29, 29))
            slp_sum[T, :, :] += slpd * 1.0e-02
            slp_sum2[T, :, :] += (slpd * 1.0e-02) ** 2
            del slpd

            if sUTC == datetime(sUTC.year, 6, 1, 6):
                T = int(0)
                sUTC = datetime(sUTC.year + 1, 3, 1) - timedelta(hours=30)
            else:
                T += int(1)
                sUTC += dt
        
        slp_mean = slp_sum / slp_size   # 平均
        slp_std = ((slp_sum2 - slp_sum * slp_mean) / slp_size) ** 0.5  # 標準偏差
        lcl_90 = norm.interval(alpha=0.90, loc=slp_mean, scale=slp_std)[0]
        del slp_mean, slp_std

    if syear == eyear or syear % 10 == 0:
        sy = ((syear - 1) // 10 - 3) * 10 + 1 # 使用する気候値の最初の年
        np.savez_compressed('{0:04d}-lcl90.npz'.format(sy), lcl90=lcl_90)   # 'yyyy-lcl90.npz'を作成し，['lcl90']にデータを格納
        print('Finish making {0:04d}-lcl90.npz'.format(sy))
        del sy, lcl_90
    else:
        pass
    syear += int(1)
