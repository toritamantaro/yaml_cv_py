# -*- coding: utf-8 -*-

from typing import Dict, Tuple, Any, Optional
import re
import string
import ast
import codecs
import argparse

import yaml
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont, TTFError
from reportlab.lib.pagesizes import A3, A4, B5  # 用紙サイズを読み込む
from reportlab.lib.pagesizes import landscape, portrait  # 横向き、縦向き
from reportlab.lib.units import inch, cm, mm, pica

from text2yaml import TextConverter

# Windowsで利用可能なフォントファイル
DEPENDENT_FONT_FILE = (
    ('msmincho', 'msmincho.ttc'),
    ('msgothic', 'msgothic.ttc'),
    ('yugothl', 'YuGothL.ttc'),
    ('meiryo', 'meiryo.ttc'),
)

DEFAULT_FONT_FACE = 'msmincho'
DEFAULT_FONT_SIZE = 12
DEFAULT_LINE_WIDTH = 0.5


class PdfMaker(object):
    def __init__(self, add_font: Optional[Tuple[str]]):
        self._input_data = None
        self._canvas = None  # reportlab.pdfgen.canvas
        self._fonts = []  # 登録したフォント名

        # ReprotLabで用意されている日本語フォントを登録する
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
        self._fonts = ['HeiseiKakuGo-W5', 'HeiseiMin-W3']
        self.check_font(DEPENDENT_FONT_FILE)
        if add_font:
            self.register_font(add_font)

    def check_font(self, font_file: Tuple[Tuple[str]]):
        '''
        任意のフォントファイルを登録する
        :param font_file:
        登録するフォント名・ファイル名を、(フォント名,ファイル名）というタプルにして渡す。
        e.g. (('msmincho', 'msmincho.ttc'), ... ,('msmincho', 'msmincho.ttc'))
        '''
        for t in font_file:
            if (not isinstance(t, Tuple)) or len(t) < 2:
                continue
            self.register_font(t)

    def register_font(self, font_info: Tuple[str]):
        try:
            pdfmetrics.registerFont(TTFont(font_info[0], font_info[1]))
        except TTFError:
            print("フォント名:'{0}'_フォントファイル:'{1}'の登録に失敗しました。".format(font_info[0], font_info[1]))
        else:
            self._fonts.append(font_info[0])

    def get_value(self, params: Dict) -> str:
        value = params.get('value', '')
        s_values = re.search(r'\$(.*)$', value)
        if s_values:
            key = s_values.group(1)
            val = self._input_data.get(key, '')
            # キーワード引数を使ったテンプレートによる置換
            t = string.Template(s_values.group(0))
            value = t.substitute(**{key: val})
        return value

    def get_font(self, params: Dict) -> Tuple[float, str]:
        font_size = float(params.get('font_size', DEFAULT_FONT_SIZE))
        font_face = params.get('font_face', DEFAULT_FONT_FACE)
        if font_face not in self._fonts:
            face = DEFAULT_FONT_FACE if (DEFAULT_FONT_FACE in self._fonts) else self._fonts[0]
            print("フォント名'{}'は指定できません。'{}'が適用されます。".format(font_face, face))
            font_face = face
        return float(font_size), font_face

    def put_string(self, x: float, y: float, char: str, font_size: float, font_face: str):
        if not char:
            return
        self._canvas.setFont(font_face, font_size)
        self._canvas.drawString(x, y, char)

    def put_textbox(self, x: float, y: float, char: str, font_size: float, font_face: str):
        if not char:
            return
        text_obj = self._canvas.beginText()
        text_obj.setTextOrigin(x, y)
        text_obj.setFont(font_face, font_size)
        text_obj.textLines(char)
        self._canvas.drawText(text_obj)

    def string(self, params: Dict):
        x = self.unit2dot(params.get('x'))
        y = self.unit2dot(params.get('y'))
        value = self.get_value(params)
        font_size, font_face = self.get_font(params)
        self.put_string(x, y, value, font_size, font_face)

    def box(self, params: Dict):
        self.line_style(params)
        x = self.unit2dot(params.get('x'))
        y = self.unit2dot(params.get('y'))
        w = self.unit2dot(params.get('width'))
        h = self.unit2dot(params.get('height'))
        self._canvas.rect(x, y, w, h)

    def line(self, params: Dict):
        self.line_style(params)
        x = self.unit2dot(params.get('x'))
        y = self.unit2dot(params.get('y'))
        dx = self.unit2dot(params.get('dx'))
        dy = self.unit2dot(params.get('dy'))
        self._canvas.line(x, y, x + dx, y + dy)

    def lines(self, params: Dict):
        self.line_style(params)
        points = params.get('points')
        x = self.unit2dot(points[0].get('x'))
        y = self.unit2dot(points[0].get('y'))
        close = params.get('close')
        path = self._canvas.beginPath()  # 描画用のパスを生成
        path.moveTo(x, y)
        for dct in points[1:]:
            dx = self.unit2dot(dct.get('x'))
            dy = self.unit2dot(dct.get('y'))
            x = x + dx
            y = y + dy
            # print(dx, ',', dy)
            path.lineTo(x, y)
        if close:
            path.close()
        self._canvas.drawPath(path)

    def multi_lines(self, params: Dict):
        self.line_style(params)
        x = self.unit2dot(params.get('x'))
        y = self.unit2dot(params.get('y'))
        dx = self.unit2dot(params.get('dx'))
        dy = self.unit2dot(params.get('dy'))
        sx = self.unit2dot(params.get('sx'))
        sy = self.unit2dot(params.get('sy'))
        num = int(params.get('num'))
        self._canvas.line(x, y, x + dx, y + dy)
        for i in range(num):
            self._canvas.line(x, y, x + dx, y + dy)
            x = x + sx
            y = y + sy

    def line_style(self, params: Dict):
        # 線のスタイル
        line_styles = {
            'dashed': [2, 2],  # 線と間隔の長さを任意に定義
            'chain': [2, 2, 10, 2],  # 線と間隔の長さを任意に定義
            'solid': [],  # 空のリスト -> 実線
        }
        style = params.get('line_style', '')
        style_lst = line_styles.get(style, [])  # 対応するキーがない場合は空のリストを渡す -> 実線
        self._canvas.setDash(style_lst)

        # 線の幅
        width = params.get('line_width')
        try:
            width = float(width)
        except:
            width = DEFAULT_LINE_WIDTH

        self._canvas.setLineWidth(width)

    def unit2dot(self, s: Any) -> float:
        '''
        「数値+単位」（文字列型）で指定された値をドットに変換する
        '''
        inch_val = re.search(r'\s*(-?[0-9\.]+)\s*inch', s)
        mm_val = re.search(r'\s*(-?[0-9\.]+)\s*mm', s)
        cm_val = re.search(r'\s*(-?[0-9\.]+)\s*cm', s)
        pica_val = re.search(r'\s*(-?[0-9\.]+)\s*pica', s)

        if mm_val:
            return float(mm_val.group(1)) * mm
        elif cm_val:
            return float(cm_val.group(1)) * cm
        elif inch_val:
            return float(inch_val.group(1)) * inch
        elif pica_val:
            return float(pica_val.group(1)) * pica
        else:
            # 単位が指定されていない場合
            try:
                return float(s)
            except TypeError:
                return None

    def new_page(self, params: Dict = None):
        self._canvas.showPage()  # これまでのページを確定

    def save(self):
        self._canvas.save()

    def education_experience(self, params: Dict):
        y = self.unit2dot(params.get('y'))
        year_x = self.unit2dot(params.get('year_x'))
        month_x = self.unit2dot(params.get('month_x'))
        value_x = self.unit2dot(params.get('value_x'))
        ijo_x = self.unit2dot(params.get('ijo_x'))
        dy = self.unit2dot(params.get('dy'))
        caption_x = self.unit2dot(params.get('caption_x'))
        font_size, font_face = self.get_font(params)
        # 学歴
        self.put_string(caption_x, y, '学歴', font_size, font_face)
        y = y - dy
        education = self._input_data.get('education', [])
        for d in education:
            year = str(d.get('year', ''))
            month = str(d.get('month', ''))
            self.put_string(year_x, y, year, font_size, font_face)
            x = month_x - (len(month) - 1) * font_size * 0.3
            self.put_string(x, y, month, font_size, font_face)
            self.put_string(value_x, y, str(d.get('value', '')), font_size, font_face)
            y = y - dy
        # 職歴
        self.put_string(caption_x, y, '職歴', font_size, font_face)
        y = y - dy
        experience = self._input_data.get('experience', [])
        for d in experience:
            year = str(d.get('year', ''))
            month = str(d.get('month', ''))
            self.put_string(year_x, y, year, font_size, font_face)
            x = month_x - (len(month) - 1) * font_size * 0.3
            self.put_string(x, y, month, font_size, font_face)
            self.put_string(value_x, y, str(d.get('value', '')), font_size, font_face)
            y = y - dy
        # 以上
        self.put_string(ijo_x, y, '以上', font_size, font_face)

    def license_certification(self, params: Dict):
        y = self.unit2dot(params.get('y'))
        year_x = self.unit2dot(params.get('year_x'))
        month_x = self.unit2dot(params.get('month_x'))
        value_x = self.unit2dot(params.get('value_x'))
        dy = self.unit2dot(params.get('dy'))
        value = self.get_value(params)
        font_size, font_face = self.get_font(params)
        try:
            data_dcts = ast.literal_eval(value)  # 文字列を辞書型に変換
        except ValueError:
            print('免許・資格情報の読み込みに失敗しました。')
            return
        for d in data_dcts:
            year = str(d.get('year', ''))
            month = str(d.get('month', ''))
            self.put_string(year_x, y, year, font_size, font_face)
            x = month_x - (len(month) - 1) * font_size * 0.3
            self.put_string(x, y, month, font_size, font_face)
            self.put_string(value_x, y, str(d.get('value', '')), font_size, font_face)
            y = y + dy

    def textbox(self, params: Dict):
        x = self.unit2dot(params.get('x'))
        y = self.unit2dot(params.get('y'))
        value = self.get_value(params)
        font_size, font_face = self.get_font(params)
        self.put_textbox(x, y, value, font_size, font_face)

    def generate(self, input_file: str, style_file: str, output_file: str):
        # 記述内容の読み込み
        if not re.search(r'\.(YAML|YML)$', input_file.upper()):
            print("ファイル名の拡張子は「*.yaml」もしくは「*.yml」にしてください。"
                  "現在のファイル名：{0}".format(input_file))
            return
        with codecs.open(input_file, 'r', 'utf-8') as yaml_file:
            self._input_data = yaml.load(yaml_file, Loader=yaml.SafeLoader)

        # PDFファイルの生成
        if not re.search(r'\.PDF$', output_file.upper()):
            print("ファイル名の拡張子は「*.pdf」にしてください。"
                  "現在のファイル名：{0}".format(output_file))
            return
        self._canvas = canvas.Canvas(
            "./{0}".format(output_file),
            # bottomup=False, # buutomup=Trueは左下が原点という意味。Falseのときは左上原点
            pagesize=B5,
            # pagesize=landscape(A3),  # 横向き（サイズも指定）
        )

        # 指定されたスタイルの読み込み
        data = []
        if re.search(r'\.(TXT|CSV)$', style_file.upper()):
            converter = TextConverter()
            data = converter.convert(style_file)
        elif re.search(r'\.(YAML|YML)$', style_file.upper()):
            with codecs.open(style_file, 'r', 'utf-8') as yaml_file:
                data = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        else:
            print("ファイル名：{0}の読み込みに失敗しました。".format(style_file))
            return

        # PDFファイルへの描画
        for dct in data:
            # e.g. dct = {'font_size': '9', 'type': 'string', 'value': '$name_kana', 'x': '30mm', 'y': '238mm'}
            try:
                getattr(self, dct.get('type'))(dct)
            except AttributeError as e:
                print(e.args)
        self.save()


def parse_option():
    dc = 'This script is ...'
    parser = argparse.ArgumentParser(description=dc)
    parser.add_argument('-i', action='store', type=str, dest='input',
                        default='data.yaml',
                        help='set input file path.  e.g. hoge.yaml')
    parser.add_argument('-s', action='store', type=str, dest='style',
                        default='style.yaml',
                        help='set style file path.  e.g. hoge.yaml or hoge.txt')
    parser.add_argument('-o', action='store', type=str, dest='output',
                        default='output.pdf',
                        help='set output file path.  e.g. hoge.pdf')
    parser.add_argument('-f', action='store', type=str, dest='font', nargs=2,
                        help='set font name and font file.  e.g. msgothic msgothic.ttc')
    return parser.parse_args()


def main():
    args = parse_option()
    input_file = args.input
    style_file = args.style
    output_file = args.output
    font_file_info = tuple(args.font) if args.font else None

    maker = PdfMaker(add_font=font_file_info)
    maker.generate(input_file, style_file, output_file)


if __name__ == '__main__':
    main()
