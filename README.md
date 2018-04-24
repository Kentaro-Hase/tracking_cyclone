# my_codes
※現在デバックを行っております，問題点を見つけ次第更新致します。

## tracking_cyclone.py について
当スクリプトは気象庁55年長期再解析（JRA-55）（Ebita et al. 2011; Kobayashi et al. 2015）の海面更正気圧データを用いて低気圧の抽出およびトラッキングを行います。  
[NCAR](https://rda.ucar.edu/)の登録およびJRA-55の使用許可が事前に必要となります。  
当スクリプトを実行する際にはコマンドラインで以下のように入力して実行してください。  
$ python tracking_cyclone.py （NCARで登録したメールアドレス）　（NCARで登録したパスワード）  

また，当スクリプトはPython3を用いて実行しますが，標準モジュール以外に以下のモジュールを使用します。そのうち，pygribはWindows環境下でインストールすることができません。  
macOSあるいはLinux環境下でインストールしてください。  
numpy, pygrib, scipy, pandas, matplotlib, basemap

当スクリプトは，  
長谷健太郎・竹見哲也（2018）：日本域における春季の降水特定，日本気象学会2018年度春季大会  
で使用している低気圧の抽出・トラッキングの手法に基づいています。  
その為，春季に限定した低気圧の抽出・トラッキングとなっております。  
このアルゴリズムは[爆弾低気圧データベースのアルゴリズム](http://fujin.geo.kyushu-u.ac.jp/meteorol_bomb/algorithm/index.php)を参考に作成しました。  

入力として，スクリプトのsyear（開始年）とeyear（終了年）を適宜変更してください。  
適応する期間は1991年以降となります。  
出力ファイルはNCARからダウンロードしたGRIBファイル，'tracking-cyclone.csv'，trackディレクトリに格納される画像ファイルです。　　

## download-grib.py について
当スクリプトはtracking_cyclone.pyの中で，ダウンロードと低気圧判別に用いる基準値作成のみを行います。  
[NCAR](https://rda.ucar.edu/)の登録およびJRA-55の使用許可が事前に必要となります。  
当スクリプトを実行する際にはコマンドラインで以下のように入力して実行してください。  
$ python download-grib.py （NCARで登録したメールアドレス）　（NCARで登録したパスワード）  

また，当スクリプトはPython3を用いて実行しますが，標準モジュール以外に以下のモジュールを使用します。そのうち，pygribはWindows環境下でインストールすることができません。  
macOSあるいはLinux環境下でインストールしてください。  
numpy, pygrib, scipy

入力として，スクリプトのsyear（開始年）とeyear（終了年）を適宜変更してください。  
適応する期間は1991年以降となります。 
また，出力ファイルとして，'yyyy-lcl90.npz'を作成し，lcl90にデータを格納します。  
（yyyyは基準値作成に使用した最初の年の4桁）  

## identification-cyclone.py について
当スクリプトはtracking_cyclone.pyの中で，低気圧の抽出のみを行います。  
抽出したい年のGRIBファイルと，基準値作成の為のGRIBファイルまたは'yyyy-lcl90.npz'がスクリプトを実行するディレクトリに必要となります。
事前にdownload-grib.pyを実行してください。  
当スクリプトを実行する際にはコマンドラインで以下のように入力して実行してください。  
$ python identification-cyclone.py  

また，当スクリプトはPython3を用いて実行しますが，標準モジュール以外に以下のモジュールを使用します。そのうち，pygribはWindows環境下でインストールすることができません。  
macOSあるいはLinux環境下でインストールしてください。  
numpy, pygrib

入力として，スクリプトのsyear（開始年）とeyear（終了年）をdownload-grib.pyに合わせて適宜変更してください。  
適応する期間は1991年以降となります。 
また，出力ファイルとして，'cyclone.npz'を作成します。  
（変数はlon, lat, slp, JSTです。）  

## track-draw.py について
当スクリプトはtracking_cyclone.pyの中で，低気圧のトラッキングと描画のみを行います。  
'cyclone.npz'が必要となります。
事前にidentification-cyclone.pyを実行してください。
当スクリプトを実行する際にはコマンドラインで以下のように入力して実行してください。  
$ python track-draw.py  

また，当スクリプトはPython3を用いて実行しますが，標準モジュール以外に以下のモジュールを使用します。
numpy, pandas, matplotlib, basemap

入力として，スクリプトのsyear（開始年）とeyear（終了年）をdownload-grib.pyに合わせて適宜変更してください。  
適応する期間は1991年以降となります。 
また，出力ファイルとして，'tracking-cyclone.csv'，trackディレクトリに格納される画像ファイルを作成します。
