# -*- coding:utf-8 -*-
'''
2018/04/24 Kentaro Hase
低気圧のトラッキングと，その結果を描画するスクリプトとして作成。
抽出した低気圧のデータ'cyclone.npz'を必要とします
トラッキングのデータは'./tracking-cyclone.csv'に格納します。
また，描画ファイルはtrackディレクトリ下に格納します。
2018/04/25 Kentaro Hase 不具合を修正し更新
'''
# トラッキングを行う開始年・終了年
syear = 2006
eyear = 2017

# Libraries
from datetime import datetime, timedelta
from os import path, makedirs
from pandas import DataFrame
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
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

# 低気圧を抽出したデータ
f = 'cyclone.npz'
if path.exists(f):
    cloc = np.load(f)
else:
    print('identification-cyclone.pyを先に実行してください。')
    sys.exit()  # スクリプトの終了

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
        # print(c_now)  # 解析状況を確認したい方はこの行のコメントアウトを解除してください。
        del c_now
    
    else:
        pass
            
    # 次の時刻へ
    if time == datetime(time.year, 5, 31, 18):
        t = int(0)
        time = datetime(time.year + 1, 3, 1) - timedelta(hours=12)
        del JST, lon, lat, slp, JST_1, lon_1, lat_1, slp_1
    else:
        t += int(1)
        del JST, lon, lat, slp, JST_1, lon_1, lat_1, slp_1
        time += dt

# 低気圧の寿命（同じナンバーの低気圧の中で最も大きいlifeの値を低気圧の寿命とする）
for i in range(np.max(c['num'])):
    same_num = np.where(c['num'] == i + 1)
    if len(c['max_life'][same_num]) > 1:
        c['max_life'][same_num] = np.max(c['life'][same_num])
    else:
        continue

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
df_save = df.ix[:, ['低気圧番号', '日本時刻', '経度(deg)', '緯度(deg)', '海面更正気圧(hPa)', '低気圧発生からの時間(h)', '気圧変動量(hPa/h)', '低気圧の移動速度(km/h)', '低気圧の寿命(h)']]   # 行のソート
df_save = df_save.sort_values(by=['低気圧番号'])  # 列のソート
df_save = df_save.set_index('低気圧番号')
df_save.to_csv('./tracking-cyclone.csv')
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
num_min = df['低気圧番号'].min()
num_max = df['低気圧番号'].max()
if path.exists('track'):
    pass
else:
    makedirs('track')

while num_min <= num_max:
    if df['低気圧番号'][df['低気圧番号'] == num_min].count() == 0:
        pass
    else:
        # print('num =', num_min)   # 解析状況を確認したい方はこの行のコメントアウトを解除してください。
        c_lon, c_lat = mp(np.array(df['経度(deg)'][df['低気圧番号'] == num_min]), np.array(df['緯度(deg)'][df['低気圧番号'] == num_min]))
        c_start = df['日本時刻'][df['低気圧番号'] == num_min].min()
        c_end = df['日本時刻'][df['低気圧番号'] == num_min].max()
        fonts ={'family' : 'Times New Roman', 'size' : 25}
        plt.rc('font', **fonts)
        fig = plt.figure(figsize=(12, 12))

        ax = fig.add_subplot(1, 1, 1)
        plot = ax.plot(c_lon, c_lat, marker='o', color='k', linewidth=3)
        mp.drawcoastlines()
        mp.drawmeridians(np.arange(0., 361., 5.), labels=[True, False, False, True], linewidth=0.01)
        mp.drawparallels(np.arange(-90., 91., 5.), labels=[True, False, False, True], linewidth=0.01)

        ax.set_title('{0:04d}/{1:02d}/{2:02d} {3:02d}:00 - {4:02d}/{5:02d} {6:02d}:00 JST'.format(c_start.year, c_start.month, c_start.day, c_start.hour, c_end.month, c_end.day, c_end.hour), fontsize=30)
        
        plt.savefig('./track/track-{0:05d}.png'.format(num_min))
        plt.close('all')
        
    num_min += int(1)

print('Finish.')
