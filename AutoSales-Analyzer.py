import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from wordcloud import WordCloud


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive"
        }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(e)


def parse_html_1(html):
    out_list = []
    param_list = []
    txt = json.loads(html)
    # print(txt)
    for row in txt["data"]['list']:
        # print(row)
        series_name = row["series_name"]
        brand_name = row['brand_name']
        count = row["count"]
        price = row["price"]
        series_id = row["series_id"]
        urls = "https://www.dongchedi.com/auto/params-carIds-x-"+str(series_id)
        htmls = get_html(urls)
        param_list.extend(parse_html_2(htmls))
        out_list.append([brand_name, series_name, price, count])
    return out_list, param_list


def parse_html_2(html):
    params = []
    soup = BeautifulSoup(html,"lxml")
    for row in soup.select("#__next > div > div > div > div.configuration_wrapper__1ydsq > "
                           "div.configuration_main__2NCwO > div:nth-child(2)"):
        level = row.select("div:nth-child(4) > div:nth-child(2) > div")[0].text
        manufacturer = row.select("div:nth-child(3) > div:nth-child(2) > div")[0].text
        energy = row.select("div:nth-child(5) > div:nth-child(2) > div")[0].text
        time = row.select("div:nth-child(6) > div:nth-child(2) > div")[0].text
        params.append([level, manufacturer, energy, time])
    return params


def save_datas(info, param):
    df_out = pd.DataFrame(info, columns=['品牌名', '系列名称', '价格', '销量'])
    df_param = pd.DataFrame(param, columns=['级别', '厂商', '能源类型', '上市时间'])
    with pd.ExcelWriter('output.xlsx') as writer:
        df_out.to_excel(writer, sheet_name='销售数据', index=False)
        df_param.to_excel(writer, sheet_name='参数信息', index=False)

def show_datas(info, param):
    # 假设 info 和 param 已经是两个列表或字典，包含了所有需要的数据
    df_info = pd.DataFrame(info, columns=['品牌名', '系列名称', '价格', '销量'])
    df_param = pd.DataFrame(param, columns=['级别', '厂商', '能源类型', '上市时间'])

    # 由于数据是一一对应的，我们可以直接根据索引连接两个DataFrame
    df_combined = pd.concat([df_info, df_param], axis=1)

    # 统计综合信息
    total_cars = len(df_combined)
    max_sales_row = df_combined.loc[df_combined['销量'].idxmax()]
    max_sales_car = [max_sales_row['品牌名'], max_sales_row['系列名称']]
    max_sales_model = max_sales_row['系列名称']
    max_sales = max_sales_row['销量']

    def get_avg_price(price_str):
        parts = price_str.replace('万', '').split('-')
        return (float(parts[0]) + float(parts[-1])) / 2 if len(parts) > 1 else float(parts[0])

    df_combined['平均价格'] = df_combined['价格'].apply(get_avg_price)
    average_price = (df_combined['平均价格'] * df_combined['销量']).sum() / df_combined['销量'].sum()

    brand_counts = df_combined.groupby('品牌名').size().reset_index(name='车型数量')
    most_models_brand = brand_counts.loc[brand_counts['车型数量'].idxmax(), '品牌名']

    # 计算不同类型的销售占比
    sales_by_type = df_combined.groupby('能源类型')['销量'].sum().to_dict()
    total_sales = df_combined['销量'].sum()

    oil_sales_ratio = sales_by_type.get("汽油", 0) / total_sales * 100 if total_sales > 0 else 0
    electric_sales_ratio = sales_by_type.get("纯电动", 0) / total_sales * 100 if total_sales > 0 else 0
    hybrid_sales_ratio = sales_by_type.get("插电式混合动力", 0) / total_sales * 100 if total_sales > 0 else 0

    # 控制台打印统计信息
    print(f"车辆总数: {total_cars}")
    print(f"销量最多汽车: {' '.join(max_sales_car)}")
    print(f"销量最多车型: {max_sales_model}")
    print(f"车辆最高销售量: {max_sales}")
    print(f"车辆平均价格: {average_price:.2f} 万元")
    print(f"车型最多的品牌: {most_models_brand}")
    print(f"油车销售占比: {oil_sales_ratio:.2f}%")
    print(f"电车销售占比: {electric_sales_ratio:.2f}%")
    print(f"油电混销售占比: {hybrid_sales_ratio:.2f}%")

    # 按品牌统计销量并导出到 Excel
    brand_sales = df_combined.groupby('品牌名')['销量'].sum().reset_index()
    brand_sales.to_excel('brand_sales.xlsx', index=False, sheet_name='Brand Sales')
    print("已导出品牌销量排行榜至 brand_sales.xlsx")

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文

    # 绘制饼图
    plt.figure(figsize=(12, 12))
    plt.pie(brand_sales['销量'], labels=brand_sales['品牌名'], autopct='%1.1f%%', startangle=140,
            textprops={'fontsize': 12}, pctdistance=0.85)
    plt.title('汽车品牌销量占比')
    plt.show()

    # 制作词云图
    series_freq = dict(zip(df_combined['系列名称'], df_combined['销量']))
    font_path = r'C:\Windows\Fonts\Calibri'# 尝试使用系统自带的字体
    if not os.path.exists(font_path):
        print("警告: 字体文件不存在，请确保路径正确。")
        alternative_fonts = [
            r'C:\Windows\Fonts\msyh.ttc',  # 微软雅黑
            r'C:\Windows\Fonts\simsun.ttc'  # 宋体
        ]
        for alt_font in alternative_fonts:
            if os.path.exists(alt_font):
                font_path = alt_font
                break
        else:
            print("警告: 没有找到合适的中文字体文件。")
            font_path = None
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          font_path=font_path).generate_from_frequencies(series_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('汽车系列名称词云图')
    plt.show()

    # 销量前 10 的汽车柱状图
    df_unique = df_combined.drop_duplicates(subset=['系列名称', '销量'], keep='first')
    df_grouped = df_unique.groupby('系列名称')['销量'].max().reset_index()
    top_10_sales = df_grouped.nlargest(10, '销量')
    print("去重/聚合后的销量前 10 的汽车数据：")
    print(top_10_sales)
    plt.figure(figsize=(10, 6))
    plt.bar(top_10_sales['系列名称'], top_10_sales['销量'], color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('系列名称')
    plt.ylabel('销量')
    plt.title('销量前 10 的汽车')
    plt.tight_layout()
    plt.show()

    # 销量价格占比柱状图
    price_bins = [0, 5, 10, 20, 30, float('inf')]
    price_labels = ['0-5w', '5-10w', '10-20w', '20-30w', '30以上']
    df_combined['价格区间'] = pd.cut(df_combined['平均价格'], bins=price_bins, labels=price_labels)

    price_sales = df_combined.groupby('价格区间', observed=True)['销量'].sum()

    plt.figure(figsize=(10, 6))
    plt.bar(price_sales.index, price_sales.values, color='lightgreen')
    plt.xlabel('价格区间')
    plt.ylabel('销量')
    plt.title('汽车销量价格占比')
    plt.show()


if __name__ == '__main__':
    out_lists = []
    param_lists = []
    for page in range(0, 70, 10):
        html_1 = get_html(f"https://www.dongchedi.com/motor/pc/car/rank_data?aid=1839&app_name=auto_web_pc&city_name=%E5%8C%97%E4%BA%AC&count={page}&offset=20&month=&new_energy_type=&rank_data_type=11&brand_id=&price=&manufacturer=&series_type=&nation=0")
        info, param = parse_html_1(html_1)
        out_lists.extend(info)
        param_lists.extend(param)
        print(f"第{page}页已爬取")
    save_datas(out_lists, param_lists)
    show_datas(out_lists,param_lists)



