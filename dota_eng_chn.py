# -*- coding: UTF-8 -*-
import requests
from lxml import etree
import random, time
import xlrd
import xlwt

# 浏览器头文件
head = {}
head[
    'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
# comb_data = data.sheets()[1]
urltest = 'http://dotamax.com/hero/rate'
r = requests.get(urltest, headers=head).text
print(r)
s = etree.HTML(r)

hero_list = []
heroes_dict_en = {}
heroes_dict = {}
hero_list_chn = s.xpath("//span[@class='hero-name-list']/text()")
hero_list_en = s.xpath("//img[@class='hero-img-list']/@src")
print(hero_list_chn)
print(hero_list_en)
hero_list = []
heroes_dict_en = {}
heroes_dict = {}
for en_hero in hero_list_en:
    en_hero_name = (en_hero.split('/')[-1]).replace('_hphover.png', '')
    hero_list.append(en_hero_name)

for idx, chn_hero in enumerate(hero_list_chn):
    heroes_dict_en[hero_list[idx]] = chn_hero
    heroes_dict[chn_hero] = hero_list[idx]

print(heroes_dict_en)
print(heroes_dict)
