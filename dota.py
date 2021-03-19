# -*- coding: UTF-8 -*-
import requests
from lxml import etree
import random, time
import xlrd
import xlwt
import redis
import csv
# -*- coding: UTF-8 -*-
import requests
from lxml import etree
import random, time
import xlrd
import xlwt
from operator import add
from datetime import datetime


def add_two_list(list_a, list_b):
    print(list_a, list_b)
    list_result = [x + float(y.strip('%')) for x, y in zip(list_a, list_b)]
    return list_result


# 浏览器头文件
head = {}
head[
    'User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'
# comb_data = data.sheets()[1]
urltest = 'http://dotamax.com/hero/rate'
r = requests.get(urltest, headers=head).text
# print(r)
s = etree.HTML(r)
hero_list_chn = s.xpath("//span[@class='hero-name-list']/text()")
hero_list_en = s.xpath("//img[@class='hero-img-list']/@src")
hero_list = []
heroes_dict_en = {}
heroes_dict = {}
heroes_name_index = {}
for en_hero in hero_list_en:
    en_hero_name = (en_hero.split('/')[-1]).replace('_hphover.png', '')
    hero_list.append(en_hero_name)

for idx, chn_hero in enumerate(hero_list_chn):
    heroes_dict_en[hero_list[idx]] = chn_hero
    heroes_dict[chn_hero] = hero_list[idx]

# 浏览器头文件
head = {}
head[
    'User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'

i = 0
name_anti = []
rate_anti = []
# 打开一个n局的数据表，作用是：当本次爬取的特定数据缺失时，使用n局数据进行填充
# n局同样缺失的胜率，克制和配合指数设置为0.0%
data = xlrd.open_workbook('Dota_n.xlsx')
anti_data = data.sheets()[0]
comb_data = data.sheets()[1]

redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)

total_hero_len = len(hero_list)

# 爬取各英雄作为对手时的胜率
for hero in hero_list:
    url0 = 'http://www.dotamax.com/hero/detail/match_up_anti/T'
    # /
    ##########################################
    # 本次爬取的是国内h局天梯最近一个月的数据，
    # 可以通过修改【两个】for循环中的url0值来爬取其他数据
    # url0中参数的含义：
    # server（服务器）= cn(国内) world(国外) all(所有)
    # ladder（类型）=y(天梯) n（普通）
    # skill（等级)=n h vh
    # time（时间范围）=month  week  v707(7.07版本之后的数据)
    # match_up_comb（队友） match_up_anti（对手）
    # T --英雄的名字，下一行程序会将进行替换
    ##########################################
    url = url0.replace('T', hero, 1)
    response = redis_cli.get('anti_' + hero)
    if not response:
        response = requests.get(url, headers=head).text
        redis_cli.set('anti_' + hero, response, 86400)

    s = etree.HTML(response)
    name_anti.append(s.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/table/tbody/tr/td[1]/span/text()'))
    name_anti[i].append(heroes_dict_en[hero])
    rate_anti.append(s.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/table/tbody/tr/td[2]/div[1]/text()'))
    rate_anti[i].append('0.00%')
    i = i + 1
    print(i, '/{}'.format(total_hero_len), hero)
    # time.sleep(random.uniform(0.1, 0.5))

# 将数据格式化并排序
list_n = 0
while list_n < total_hero_len:
    i = 0
    j = 0
    # 把英雄名字变为英文
    for heroname_cn in name_anti[list_n]:
        name_anti[list_n][j] = heroes_dict[heroname_cn]
        j = j + 1
    # 把英雄的名字和胜率按照标准顺序排序
    hero_n = 0
    while hero_n < total_hero_len:
        if name_anti[list_n][i] == hero_list[hero_n]:
            name_anti[list_n][i] = name_anti[list_n][hero_n]
            name_anti[list_n][hero_n] = hero_list[hero_n]
            temp = rate_anti[list_n][i]
            rate_anti[list_n][i] = rate_anti[list_n][hero_n]
            rate_anti[list_n][hero_n] = temp
            hero_n = hero_n + 1
            i = hero_n
        else:
            i = i + 1
            if i == len(name_anti[list_n]):
                print(list_n, hero_n, hero_list[list_n], hero_list[hero_n])
                name_anti[list_n].insert(hero_n, hero_list[hero_n])
                rate_anti[list_n].insert(hero_n, anti_data.cell(hero_n + 1, list_n + 1).value)
                hero_n = hero_n + 1
                i = hero_n
    print(list_n + 1, '/{}'.format(total_hero_len), hero_list[list_n], len(name_anti[list_n]))
    list_n = list_n + 1

# 爬取各英雄作为队友时的胜率
i = 0
name_comb = []
rate_comb = []
for hero in hero_list:
    url0 = 'http://www.dotamax.com/hero/detail/match_up_comb/T'
    ##########################################
    # 本次爬取的是国内h局天梯最近一个月的数据，
    # 可以通过修改【两个】for循环中的url0值来爬取其他数据
    ##########################################
    url = url0.replace('T', hero, 1)
    response = redis_cli.get('comb_' + hero)
    if not response:
        response = requests.get(url, headers=head).text
        redis_cli.set('comb_' + hero, response, 86400)
    # r = requests.get(url, headers=head).text
    s = etree.HTML(response)
    name_comb.append(s.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/table/tbody/tr/td[1]/span/text()'))
    name_comb[i].append(heroes_dict_en[hero])
    rate_comb.append(s.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/table/tbody/tr/td[2]/div[1]/text()'))
    rate_comb[i].append('0.00%')
    i = i + 1
    print(i, '/{}'.format(total_hero_len), hero)
    # time.sleep(random.uniform(0.1, 0.5))

# 将数据格式化并排序
list_n = 0
while list_n < total_hero_len:
    i = 0
    j = 0
    # 把英雄名字变为英文
    for heroname_cn in name_comb[list_n]:
        name_comb[list_n][j] = heroes_dict[heroname_cn]
        j = j + 1
    # 把英雄的名字和胜率按照标准顺序排序
    hero_n = 0
    while hero_n < total_hero_len:
        if name_comb[list_n][i] == hero_list[hero_n]:
            name_comb[list_n][i] = name_comb[list_n][hero_n]
            name_comb[list_n][hero_n] = hero_list[hero_n]
            temp = rate_comb[list_n][i]
            rate_comb[list_n][i] = rate_comb[list_n][hero_n]
            rate_comb[list_n][hero_n] = temp
            hero_n = hero_n + 1
            i = hero_n
        else:
            i = i + 1
            if i == len(name_comb[list_n]):
                print(list_n, hero_n, hero_list[list_n], hero_list[hero_n])
                name_comb[list_n].insert(hero_n, hero_list[hero_n])
                rate_comb[list_n].insert(hero_n, comb_data.cell(hero_n + 1, list_n + 1).value)
                hero_n = hero_n + 1
                i = hero_n
    print(list_n + 1, ' /{}'.format(total_hero_len), hero_list[list_n], len(name_comb[list_n]))
    list_n = list_n + 1

# 这里写入临时文件
date_time = datetime.today().strftime('%Y-%m-%d')
with open(date_time + "_anti.txt", 'w') as out:
    out.write('\t'.join(name_anti[0]) + '\n')
    out.write('\t'.join([heroes_dict_en[x] for x in name_anti[0]]) + '\n')
    csvWriter = csv.writer(out, delimiter='\t')
    csvWriter.writerows(rate_anti)
    # out.write(rate_anti + '\n')

with open(date_time + "_comb.txt", 'w') as out:
    out.write('\t'.join(name_comb[0]) + '\n')
    out.write('\t'.join([heroes_dict_en[x] for x in name_comb[0]]) + '\n')
    csvWriter = csv.writer(out, delimiter='\t')
    csvWriter.writerows(rate_comb)
    # out.write(rate_anti + '\n')

for idx, hero_i in enumerate(hero_list):
    heroes_name_index[hero_i] = idx
# 将数据写入到表格
need_write_excel = False
input_hero_chn = "力丸,龙骑士,巫医,沉默术士"
input_list_en = [heroes_dict[x] for x in input_hero_chn.split(",")]
input_hero = "axe,morphling,razor,sniper"
if not input_hero_chn:
    input_list = input_hero.split(",")
else:
    input_list = input_list_en
input_idx_list = []
rate_anti_total = []
total_each = 0.0
tmp_sum_list = []
for each_hero in input_list:
    idx_input = heroes_name_index[each_hero]
    # get hero anti
    if len(rate_anti_total) == 0:
        rate_anti_total = [float(x.strip('%')) for x in rate_anti[idx_input]]
    else:
        rate_anti_total = add_two_list(rate_anti_total, rate_anti[idx_input])
print(rate_anti_total)
name_rate_map = {}
for idx, hero_i in enumerate(hero_list):
    name_rate_map[heroes_dict_en[hero_i]] = rate_anti_total[idx]
# 排序
hero_out = dict(sorted(name_rate_map.items(), key=lambda item: item[1]))
print('最克制人物{}的为{}'.format([heroes_dict_en[each_hero] for each_hero in input_list], hero_out))

if need_write_excel:
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet1 = workbook.add_sheet('anti_h')
    worksheet2 = workbook.add_sheet('comb_h')
    for row in range(1, total_hero_len):
        worksheet1.write(row, 0, hero_list[row - 1])
    for col in range(1, total_hero_len):
        worksheet1.write(0, col, hero_list[col - 1])
    for row in range(1, total_hero_len):
        for col in range(1, total_hero_len):
            worksheet1.write(row, col, rate_anti[row - 1][col - 1])
    for row in range(1, total_hero_len):
        worksheet2.write(row, 0, hero_list[row - 1])
    for col in range(1, total_hero_len):
        worksheet2.write(total_hero_len, col, hero_list[col - 1])
    for col in range(1, total_hero_len):
        for row in range(1, total_hero_len):
            worksheet2.write(row, col, rate_comb[col - 1][row - 1])
    workbook.save('Dota_BP_h.xls')
