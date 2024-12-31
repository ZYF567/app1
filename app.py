import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import os
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

def process_text_for_frequency(text):
    # 使用 jieba 分词
    words = jieba.cut(text)
    
    filtered_words = [word for word in words if
                      len(word) > 1 and word.strip() not in ['\n', ' ', '。', ',', '，', '！', '：', '；', '(', ')', '“',
                                                             '”']]

    word_counts = Counter(filtered_words)
    return word_counts


# 创建词云图
def create_wordcloud(words):
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    font_path = 'SimHei.ttf'  
    if not os.path.isfile(font_path):
        st.error("字体文件SimHei.ttf不存在，请上传字体文件到应用根目录。")
        return
    wordcloud = WordCloud(font_path=font_path, width=800, height=400).generate(' '.join(words))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)


# 创建柱状图
def create_bar_chart(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    fig = px.bar(data, x='词语', y='频率', title="词频柱状图")
    fig.update_layout(
        font=dict(
            family="SimHei",
            size=12,
            color="Black"
        )
    )
    st.plotly_chart(fig)


# 创建饼图
def create_pie_chart(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    fig = px.pie(data, names='词语', values='频率', title="词频饼图")
    fig.update_layout(
        font=dict(
            family="SimHei",
            size=12,
            color="Black"
        )
    )
    st.plotly_chart(fig)


# 创建折线图
def create_line_chart(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    fig = px.line(data, x='词语', y='频率', title="词频折线图")
    fig.update_layout(
        font=dict(
            family="SimHei",
            size=12,
            color="Black"
        )
    )
    st.plotly_chart(fig)


# 使用seaborn创建热力图
def create_heatmap(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    words = data.index.tolist()
    frequencies = data['频率'].tolist()
    heatmap_data = [[freq] for freq in frequencies]

    fig, ax = plt.subplots(figsize=(8, len(words) / 2))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", yticklabels=words, cbar_kws={'label': '词频'})
    ax.set_title("热力图")
    ax.set_ylabel("词语")
    ax.set_xlabel("类别")
    st.pyplot(fig)


# 创建散点图
def create_scatter_plot(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    fig = px.scatter(data, x='词语', y='频率', title="词频散点图")
    fig.update_layout(
        font=dict(
            family="SimHei",
            size=12,
            color="Black"
        )
    )
    st.plotly_chart(fig)


# 创建条形图
def create_horizontal_bar_chart(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    fig = px.bar(data, x='频率', y='词语', orientation='h', title="词频条形图")
    fig.update_layout(
        font=dict(
            family="SimHei",
            size=12,
            color="Black"
        )
    )
    st.plotly_chart(fig)


# 主函数
def main():
    st.title("比赛项目词频分析")

    # 文章 URL 输入框
    url = st.text_input("请输入文章 URL:")

    if url:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/89.0.4389.128 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }

        # 抓取文章内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，抛出异常

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有 <a> 标签
        a_tags = soup.find_all('a')

        # 提取 <a> 标签内的文本内容并拼接
        if a_tags:
            article_content = ""
            for a_tag in a_tags:
                article_content += a_tag.get_text(separator="\n", strip=True) + "\n"
        else:
            st.error("无法找到 <a> 标签内容，页面结构可能有所不同。")
            return

        st.write(article_content)

        # 显示全文
        st.write("### 文章全文")
        st.text_area("全文显示", value=article_content, height=300)

        # 分词并统计词频
        word_freq_counts = process_text_for_frequency(article_content)

        # 将词频转换为 pandas DataFrame
        word_freq_df = pd.DataFrame(list(word_freq_counts.items()), columns=['词语', '频率']).sort_values(by='频率',
                                                                                                          ascending=False)

        # 显示所有词频统计结果
        st.write("### 所有词频统计结果")
        st.dataframe(word_freq_df)

        # 获取词频排名前20的词汇
        top_20_word_freq_df = pd.DataFrame(list(word_freq_counts.most_common(20)), columns=['词语', '频率'])

        # 显示词频 Top 20 表格
        st.write("### 词频 Top 20")
        st.dataframe(top_20_word_freq_df)

        # 侧边栏：选择图形类型和词频数量
        chart_type = st.sidebar.selectbox(
            "选择图形类型",
            ["词云图", "柱状图", "饼图", "折线图", "热力图", "散点图", "条形图"]
        )
        top_n = st.sidebar.slider("选择显示的词频数量", min_value=1, max_value=len(word_freq_df), value=20, step=1)

        # 根据选择的词频数量和图形类型绘制相应的图形
        if top_n > 0:
            top_n_word_freq_df = word_freq_df.head(top_n)

            if chart_type == "词云图":
                st.write("### 词云图")
                create_wordcloud(top_n_word_freq_df['词语'].tolist())
            elif chart_type == "柱状图":
                st.write("### 词频柱状图")
                create_bar_chart(top_n_word_freq_df)
            elif chart_type == "饼图":
                st.write("### 词频饼图")
                create_pie_chart(top_n_word_freq_df)
            elif chart_type == "折线图":
                st.write("### 词频折线图")
                create_line_chart(top_n_word_freq_df)
            elif chart_type == "热力图":
                st.write("### 热力图")
                create_heatmap(top_n_word_freq_df)
            elif chart_type == "散点图":
                st.write("### 词频散点图")
                create_scatter_plot(top_n_word_freq_df)
            elif chart_type == "条形图":
                st.write("### 词频条形图")
                create_horizontal_bar_chart(top_n_word_freq_df)


if __name__ == "__main__":
    main()
