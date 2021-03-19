import json


class Hero:

    def __init__(self, chn_name, en_name, anti_rate_dict):
        self.chn_name = chn_name
        self.en_name = en_name
        self.anti_rate_dict = anti_rate_dict

    def __repr__(self):
        return '{}\t{}\t{}'.format(self.chn_name, self.en_name, self.anti_rate_dict)


def read_file_to_list(filename):
    # 这里写入临时文件
    with open(filename) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content


def get_hero_info(anti_file_list):
    if not anti_file_list:
        return
    hero_en_list = anti_file_list[0].split('\t')
    hero_chn_list = anti_file_list[1].split('\t')
    inner_heroes_dict_en = {}

    for idx, hero_chn in enumerate(hero_chn_list):
        hero_en_outter = hero_en_list[idx]
        anti_rate_list = [float(x.strip('%')) for x in anti_file_list[idx + 2].split("\t")]
        pair_rate_dict = {}
        for idy, hero_en_inner in enumerate(hero_en_list):
            pair_rate_dict[hero_en_inner] = anti_rate_list[idy]
        inner_heroes_dict_en[hero_en_outter] = Hero(chn_name=hero_chn, en_name=hero_en_outter,
                                                    anti_rate_dict=pair_rate_dict)
    return inner_heroes_dict_en


def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__


def get_hero_list(hero_obj_map):
    if not hero_obj_map:
        return []


def get_chn_en_dict(hero_obj_map):
    if not hero_obj_map:
        return {}
    my_dictionary = dict(map(lambda kv: (kv[1].chn_name, kv[0]), hero_obj_map.items()))
    return my_dictionary


def get_en_chn_dict(hero_obj_map):
    if not hero_obj_map:
        return {}
    my_dictionary = dict(map(lambda kv: (kv[0], kv[1].chn_name), hero_obj_map.items()))
    return my_dictionary


#  输入克制列表 输出 每个英雄名称: 'antimage': {'total': '10', detail:[{'bane':1},{'crystal_maiden':1},{'drow_ranger':3}] }
def calc_recommend(hero_obj_list, heroes_dict_en_alias):
    if not hero_obj_list:
        return {}
    recommend_dict = {}
    # 对于每一个英文名英雄 加起来所有的克制关系
    for hero_name_en, v in hero_obj_list[0].anti_rate_dict.items():
        detail_from_map = {}
        total_rate_each = 0.0
        for hero_obj in hero_obj_list:
            rate = hero_obj.anti_rate_dict[hero_name_en]
            detail_from_map[hero_obj.chn_name] = rate
            # detail_from_list.append(detail_from_map)
            total_rate_each += rate
            # 这里把关系加起来
        recommend_dict[heroes_dict_en_alias[hero_name_en]] = {'total': total_rate_each, 'detail': detail_from_map}
    return recommend_dict


def main():
    anti_file_list = read_file_to_list("2021-03-19_anti.txt")
    # key=英文英雄名 value Hero对象
    hero_obj_map = get_hero_info(anti_file_list)

    input_hero_chn = "巫医,钢背兽,露娜,影魔,瘟疫法师"
    input_hero = "axe,morphling,razor,sniper"
    # 拿到中文->英文
    heroes_dict_chn = get_chn_en_dict(hero_obj_map)
    heroes_dict_en = get_en_chn_dict(hero_obj_map)
    if input_hero_chn:
        input_list_en = [heroes_dict_chn[x] for x in input_hero_chn.split(",")]
    else:
        input_list_en = [x.strip().replace('npc_dota_hero_', '') for x in input_hero.split(",")]

    # 把克制关系比率加起来 得到一个列表
    middle_result = []
    for each_hero in input_list_en:
        hero_obj = hero_obj_map[each_hero]
        middle_result.append(hero_obj)
    calc_result = calc_recommend(middle_result, heroes_dict_en)

    ordered = dict(sorted(calc_result.items(), key=lambda i: i[1]['total'], reverse=False))
    print(json.dumps(ordered, ensure_ascii=False))


# def

if __name__ == "__main__":
    main()
