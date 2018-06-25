# -*- coding: utf-8 -*-

import csv
import re
import argparse
import codecs

import yaml


class TextConverter(object):
    def store_in_dct(self, lst, dct):
        '''
        :param lst: e.g. [ ... , 'line_width=1.5']
        :param dct:　格納先の辞書型
        '''
        for str in lst:
            if re.match(r'^.*=.*', str):  # 「=」が含まれる場合
                spl = str.split('=')
                dct[spl[0]] = spl[1]

    def string(self, lst):
        '''
        :param lst: e.g. ['string', '5mm', '170mm', '$commuting_time', 'font_size=12']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['x'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['value'] = lst.pop(0)
        self.store_in_dct(lst, dct)
        return dct

    def box(self, lst):
        '''
        :param lst: e.g. ['box', '0.5mm', '17mm', '175.5mm', '119mm', 'line_width=1.5']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['x'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['width'] = lst.pop(0)
        dct['height'] = lst.pop(0)
        self.store_in_dct(lst, dct)
        return dct

    def line(self, lst):
        '''
        1本線描画
        :param lst: e.g. ['line', '100mm', '214mm', '0mm', '-14mm', 'line_style=dashed']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['x'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['dx'] = lst.pop(0)
        dct['dy'] = lst.pop(0)
        self.store_in_dct(lst, dct)
        return dct

    def lines(self, lst):
        '''
        ポリライン描画
        :param lst: e.g.
        ['lines', '6', '0.5mm', '238mm', '139mm', '0mm', '0mm', '-38mm', '36.5mm', '0mm', '0mm',
        '-52mm', '-175.5mm', '0mm', 'line_width=1.5', 'close=true']
        lst[0]:'lines'
        lst[1]:線の本数
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        num_of_line = int(lst.pop(0))
        points = []
        for i in range(num_of_line):
            points.append({'x': lst.pop(0), 'y': lst.pop(0)})
        dct['points'] = points
        self.store_in_dct(lst, dct)
        return dct

    def multi_lines(self, lst):
        '''
        複数の平行線
        :param lst: e.g. ['multi_lines', '0.5mm', '24mm', '175.5mm', '0', '16', '0', '7mm']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['x'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['dx'] = lst.pop(0)
        dct['dy'] = lst.pop(0)
        dct['num'] = lst.pop(0)
        dct['sx'] = lst.pop(0)
        dct['sy'] = lst.pop(0)
        return dct

    def new_page(self, lst):
        '''
        :param lst: e.g. ['new_page']
        '''
        return {'type': 'new_page'}

    def education_experience(self, lst):
        '''
        :param lst: e.g.
        ['education_experience', '124mm', '5mm', '25mm', '35mm', '7mm', '95mm', '155mm', 'font_size=12']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['year_x'] = lst.pop(0)
        dct['month_x'] = lst.pop(0)
        dct['value_x'] = lst.pop(0)
        dct['dy'] = lst.pop(0)
        dct['caption_x'] = lst.pop(0)
        dct['ijo_x'] = lst.pop(0)
        self.store_in_dct(lst, dct)
        return dct

    def license_certification(self, lst):
        '''
        :param lst: e.g.
        ['license_certification', '227mm', '5mm', '25mm', '35mm', '-7mm', '$licences', 'font_size=12']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['year_x'] = lst.pop(0)
        dct['month_x'] = lst.pop(0)
        dct['value_x'] = lst.pop(0)
        dct['dy'] = lst.pop(0)
        dct['value'] = lst.pop(0)
        self.store_in_dct(lst, dct)
        return dct

    def textbox(self, lst):
        '''
        :param lst: e.g. ['textbox', '2mm', '148mm', '173mm', '30mm', '$hobby', 'font_size=13']
        '''
        dct = {}
        dct['type'] = lst.pop(0)
        dct['x'] = lst.pop(0)
        dct['y'] = lst.pop(0)
        dct['width'] = lst.pop(0)
        dct['height'] = lst.pop(0)
        dct['value'] = lst.pop(0)
        self.store_in_dct(lst, dct)
        return dct

    def convert(self, file_name):
        lst = []
        if not re.search(r'\.(TXT|CSV)$', file_name.upper()):
            print("ファイル名の拡張子は「*.txt」もしくは「*.csv」にしてください。"
                  "現在のファイル名：{0}".format(file_name))
            return lst

        with open(file_name, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)  # 1行づつリストで格納
            _ = next(reader)  # ヘッダーを読み飛ばす

            for row in reader:
                # .e.g. row = ['box', '0', '120mm', '177mm', '40mm', 'line_width=2']
                if not row:
                    continue
                if re.match(r'^\s*#', row[0]):  # 文字の先頭が「#」の場合
                    continue
                try:
                    dct = getattr(self, row[0])(row)
                    if dct:
                        lst.append(dct)
                except AttributeError as e:
                    print(e.args)
        return lst


class Txt2Yaml(TextConverter):
    def generate(self, input_file, output_file):
        data = []
        data = self.convert(input_file)

        if not re.search(r'\.(YAML|YML)$', output_file.upper()):
            print("ファイル名の拡張子は「*.yaml」もしくは「*.yml」にしてください。"
                  "現在のファイル名：{0}".format(output_file))
            return

        with codecs.open(output_file, 'w', 'utf-8') as yaml_file:
            yaml.dump(data, yaml_file, encoding='utf-8', allow_unicode=True, default_flow_style=False)


def parse_option():
    dc = 'This script is ...'
    parser = argparse.ArgumentParser(description=dc)
    parser.add_argument('-i', action='store', type=str, dest='input',
                        default='style.txt',
                        help='set input file path.  e.g. hoge.txt')
    parser.add_argument('-o', action='store', type=str, dest='output',
                        default='style.yaml',
                        help='set output file path.  e.g. hoge.yaml')
    return parser.parse_args()


def main():
    args = parse_option()
    input_file = args.input
    output_file = args.output

    maker = Txt2Yaml()
    maker.generate(input_file, output_file)


if __name__ == '__main__':
    main()
