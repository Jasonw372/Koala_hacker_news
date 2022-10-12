import os
import re
import json
import requests

os.environ["NO_PROXY"] = "bilibili.com"

headers = {
    'authority': 'api.bilibili.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'origin': 'https://space.bilibili.com',
    'referer': 'https://space.bilibili.com/489667127/channel/collectiondetail?sid=249279',
    'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37',
}

def get_data() -> list[object]:
    page_num = 0
    while True:
        page_num += 1
        bv_list = []
        params = {
            'mid': '489667127',
            'season_id': '249279',
            'sort_reverse': 'false',
            'page_num': str(page_num),
            'page_size': '30',
        }

        response = requests.get('https://api.bilibili.com/x/polymer/space/seasons_archives_list', params=params, headers=headers)
        data = response.json()
        if len(data['data']['archives']) == 0:
            break

        print(len(data['data']['archives']))
        for obj in data['data']['archives']:
            bv_list.append(obj)

        yield bv_list


def get_commont_data() -> None:
    base_url = 'http://api.bilibili.com/x/v2/reply/main'
    for urls in get_data():
        for url in urls:
            data = json.loads(json.dumps(url))
            params = {
                'type': 1,
                'oid': data['aid']
            }
            commont_data = requests.get(url=base_url, params=params, headers=headers)
            commont_data = commont_data.json()
            with open('data.json', 'a', encoding='utf-8') as f:
                if commont_data['data']['top']['upper'] is not None:
                    f.write(json.dumps(commont_data['data']['top']['upper']['content'], ensure_ascii=False))
                else:
                    f.write('{"aid": ' + str(data['aid']) + '}')
                f.write(',')
                f.write('\n')

# get_commont_data()

def parse_top_commont() -> None:
    with open('data.json', 'r', encoding='utf-8') as f:
        top_commont = json.load(f)
        # for i in range(0, len(top_commont)):
        #     if (msg := top_commont[i].get('message')) is not None:
        #         for content in msg.split('\n'):
        #             print(content)

        msg = top_commont[0].get('message')
        # 本期时间轴：
        # 00:09 sharing｜将电脑中的文件通过二维码分享给手机
        # 00:31 Steampipe｜ 浏览云服务资产的交互式命令行工具
        # 00:54 Horizon UI｜ 基于 Chakra UI 的管理后台模版
        # 01:16 Postgres WASM｜ 开源 WASM 运行 PostgresSQL 方案
        # 01:50 v86｜ 通过 WebAssembly 运行 x86 兼容的虚拟机
        # 02:06  libSQL｜ SQLite 下游版本
        # 02:38 TypeScript  10 years anniversary
        # Bam｜Wingsuit Flying by Michele Nobler
        # 本期项目链接：
        # https://github.com/parvardegr/sharing
        # https://steampipe.io/
        # https://horizon-ui.com/
        # https://supabase.com/blog/postgres-wasm
        # https://github.com/copy/v86
        # https://github.com/libsql/libsql & https://itnext.io/sqlite-qemu-all-over-again-aedad19c9a1c
        # https://devblogs.microsoft.com/typescript/ten-years-of-typescript/
        for content in msg.split('\n'):
            if re.match(r'^\d{2}:\d{2}', time := content.strip()[:5]) != None or re.match(r'\w*[|｜]\w*', content) != None:
                print(time, end=' ')
                print(content.strip()[6:])
            elif re.match(r'时间轴', content) != None or re.match(r'链接', content) != None:
                continue
            elif re.match(r'https', content) != None:
                print(content)
            else:
                continue


parse_top_commont()
