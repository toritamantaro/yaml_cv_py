YAMLによる履歴書作成スクリプト Python
===

[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

このスクリプトは、[kaityo256](https://github.com/kaityo256)様がRuby言語で開発された
[yaml_cv](https://github.com/kaityo256/yaml_cv)をPython言語に移植したものです。

[yaml_cv](https://github.com/kaityo256/yaml_cv)の使用方法については、kaityo256様が[丁寧に分かりやすく解説](https://github.com/kaityo256/yaml_cv)して下さっております。  
本スクリプトも基本的に同様の仕様になるよう作成したつもりです。  

### 移植元プログラム
YAMLによる履歴書作成スクリプト  
https://github.com/kaityo256/yaml_cv  
Copyright (c) 2018 H. Watanabe  

---

## 必要なライブラリ等
* [PyYAML](http://pyyaml.org/)
* [reportlab](http://www.reportlab.com/)

Windows10_Python3.6.5にて動作確認しました。  

## 使い方

以下のように、`-i`に続けてデータファイル、`-s`に続けてスタイルファイル、`-o`に続けて出力ファイルを指定します。  
省略した場合のデフォルトはそれぞれ`data.yaml`、`style.yaml`、`output.pdf`です。  

```
$ python make_cv.py -h
usage: make_cv.py [-h] [-i INPUT] [-s STYLE] [-o OUTPUT]

optional arguments:
  -h, --help  show this help message and exit
  -i INPUT    set input file path. e.g. hoge.yaml
  -s STYLE    set style file path. e.g. hoge.yaml or hoge.txt
  -o OUTPUT   set output file path. e.g. hoge.pdf
```

YAML形式のデータファイル(例:data.yaml)とスタイルファイル(カンマ区切りのテキスト形式かYAML形式 例:style.txt)を用意し、スクリプトを以下のように実行します。

```
$ python make_cv.py -i data.yaml -s style.txt -o output.pdf
```

出力結果

![output_01.png](sample/output_01.png)
![output_02.png](sample/output_02.png)


## 補足
本件はPython初心者＋Ruby未経験というド素人が自身の勉強の為に行ったものです。  
大変拙い移植になっていると思いますがご了承ください。

## Special thanks
Original author : [kaityo256](https://github.com/kaityo256)

本スクリプトの公開をご快諾下さりました[kaityo256](https://github.com/kaityo256)様には、この場を借りて深く御礼申し上げます。
