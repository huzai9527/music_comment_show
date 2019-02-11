from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def gen_pic(csv_name):
    with open(csv_name+'.csv', 'r', encoding='utf-8') as f:
         content = f.read()
    font = r'C://Windows//Fonts/simkai.ttf'
    bg = np.array(Image.open("background/bg.png"))
    pic = WordCloud(collocations=False, font_path=font,  background_color="white", max_words=800,  mask=bg, max_font_size=300, random_state=42).generate(content)
    plt.imshow(bg, cmap=plt.cm.gray)
    image_colors = ImageColorGenerator(bg)
    plt.imshow(pic.recolor(color_func=image_colors))
    plt.axis("off")
    plt.show()


