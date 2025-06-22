#!/usr/bin/env python
# coding: utf-8

# In[1]:


import jieba
import jieba.posseg as pseg
import os
import re
from collections import Counter
import matplotlib.pyplot as plt
from tqdm import tqdm
jieba.load_userdict('customdict.txt')
plt.rcParams['font.family'] = 'simhei'
plt.rcParams['axes.unicode_minus'] = False


# In[3]:


# 基础功能函数
def clean_text(text):
    # 只保留汉字与标点符号。
    text = re.sub(r'[^\u4e00-\u9fff。，？、；：（）「」《》“”‘’——……]', '', text)
    return text

def open_file(fname):
    # 接受文件名，返回清洗后的字符串
    with open(fname, "r",encoding = "utf-8", errors = "ignore") as f:
        text=f.read()
    return clean_text(text)

def load_stopwords(fname):
    stopwords = set()
    with open(fname, 'r', encoding = "utf-8", errors = "ignore") as f:
        stopwords.update(line.strip() for line in f if line.strip())
    return stopwords


def filtered_seg(text):
    # 返回词语+词类的元组列表
    stopwords = load_stopwords('hit_stopwords.txt')
    words = pseg.cut(text)
    return [(w, t) for w, t in words if t != 'x' and w not in stopwords]


def count(lst):
    # 接收列表，返回降序排列的列表
    lst = [item for item in lst if item != '' or item !=' ']
    count = Counter(lst)
    return count.most_common()


def bi_gram(lst):
    # 二元统计。接受（分词后的）列表，返回二元统计列表 
    return [(lst[i],lst[i+1]) for i in range(len(lst)-1)]


def tri_gram(lst):
    # 三元统计。接受（分词后的）列表，返回三元统计列表
    return [(lst[i],lst[i+1],lst[i+2]) for i in range(len(lst)-2)]


def plot_top_words(lst, title, xlabel, ylabel, colour, suffix='.png'):
    # 接受排序好的以元祖为元素的列表，以条形图的方式可视化，并保存图片
    items = [' '.join(x[0]) if isinstance(x[0], tuple) else x[0] for x in lst]
    freq = [x[1] for x in lst]
    fname = f'{title}{suffix}'
    plt.figure(figsize=(10, 6)) 
    plt.bar(items, freq, align = "center", color = colour)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel,fontsize=12)
    plt.ylabel(ylabel,fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(fname, dpi=400)
    plt.close()


# In[5]:


# 整合函数功能
def analyse_text(text):
    # 对一部作品实现多个指标的统计
    words_with_tags = filtered_seg(text)
    words = [w for w,t in words_with_tags]
    return {
        '词语词频列表': count(words),
        '二元词频率列表': count(bi_gram(words)),
        '三元词频率列表': count(tri_gram(words)),
    }


def to_file(result:dict, prefix:str, output_dir: str = '词频统计结果'):
    # 将analyse_text生成的每项结果写入文件
    try: # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)  # 递归创建目录（如果不存在）
    except Exception as e:
        print(f'创建输出目录 {output_dir} 时出错：{e}')
        return
    # 结果写入文件
    for name in result:
        data = result[name] # 以元组为元素的列表
        filename = f'{prefix}_{name}.txt'
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for j,k in data:
                    f.write(f'{j},{k}\n')
            print(f'{filename}输出成功')
        except Exception as e:
            print(f'写入文件 {filename} 时出错：{e}')


def plot_all(result, title_prefix):
    # 接收analyse_text函数返回的字典，以条形图方式可视化
    try:
        top_words = result['词语词频列表'][:20]
        plot_top_words(top_words, f'{title_prefix}_top20词语','词语','词频',colour='steelblue')
        print(f'{title_prefix}_top20词语输出成功')
    except Exception as e:
        print(f'{title_prefix}:词语词频图失败:{e}')

    try:
        top_bigram = result['二元词频率列表'][:20]
        plot_top_words(top_bigram, f'{title_prefix}_top20二元词语','二元词','词频', colour='mediumseagreen')
        print(f'{title_prefix}_top20二元词语输出成功')
    except Exception as e:
        print(f'{title_prefix}:二元词词频图失败:{e}')

    try:
        top_trigram = result['三元词频率列表'][:20]
        plot_top_words(top_trigram, f'{title_prefix}_top20三元词语','三元词','词频', colour='coral')
        print(f'{title_prefix}_top20三元词语输出成功')
    except Exception as e:
        print(f'{title_prefix}:三元词词频图失败:{e}')


# In[9]:


# 在此指定需要分析的作者及作品
authors = {'萧红':['生死场.txt','呼兰河传.txt','马伯乐.txt','小城三月.txt'],
           '丁玲':['韦护.txt','一九三零.txt','母亲.txt','桑干河.txt']
}


def main():
    for author, works in tqdm(authors.items()):
        all_text = ''
        
        # 以作品为单位的统计
        for filepath in tqdm(works):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = clean_text(f.read())
                all_text += text + '\n'  # 合并所有作品文本

                # 统计单个作品、可视化输出
                result = analyse_text(text)
                fname = f'{author}_{filepath[:-4]}'
                plot_all(result, title_prefix=fname)
                to_file(result, fname)
            except Exception as e:
                print(f'处理作品 {filepath} 时出错：{e}')

        # 以作家为单位的统计
        try: 
            result_all = analyse_text(all_text)
            fname_all = f'{author}_all_works'
            plot_all(result_all, title_prefix=fname_all)
            to_file(result_all, fname_all)
        except Exception as e:
            print(f'写入作家{author}的统计文件时出错：{e}')

main()


# In[ ]:




