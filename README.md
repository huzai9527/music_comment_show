# music_comment_show
music_163 

## 分析热评的请求URL
 - 首先我们先对请求抓包，发现所有的评论都包含在 **https://music.163.com/weapi/v1/resource/comments/R_SO_4_32785700?csrf_token="**里面，然后再去分析这个请求，发现这是一个**POST**请求，请求参数由两个**params**以及**encSecKey**。好了到此我们需要的东西都有了，接下来我们分析如何去得到这两个参数。
 ### 找到请求
 ![1.png](1.png)
 ### 分析请求参数
 ![2.png](2.png)

 ## 分析js加密
 - 找到全局js文件，找到两个参数所在的位置
 ![3.png](3.png)
 - 发现这两个参数是由**window.asrsea**获得的，接着去定位到这个函数找到对应的原函数**d**
 ![4.ong](4.png)
 - 对js进行调试，发现d的四个参数，有三个是定值，这个函数还用到了a、b、c三个函数
 ![5](5.png)
 - 其中a是产生一个16位的随机数（这里我直接让它等于**FwtEYduOXlNEHbLP**）为什么要等与这个呢 hhh 因为我发现这个随机数，他在生成encText的时候用了一次，生成encSecKey的时候，又用了一次，而且encSecKey就只跟这个随机数相关，所以让这个随机数为定值的话，就可以直接得到encSecKey的值，不用再去搞一个rsa加密，为了让你们看清楚，我还是把贴出来把
 ![6](6.png)
 - **b**函数就是我们主要要解决的**AES**加密，经过调试，我们可以知道它的两个参数a、b分别是加密字符转、密钥。以及AES的偏移量为**0102030405060708**、加密模式为**CBC**
 ![7](7.png)
 - 接下来看c函数，c函数其实是**RSA**加密，获取encSecKey的值的他的三个参数，只有a是变量，是我们随机生成的16为随机数，这里我们就默认为定值，b、c应该是和rsa加密有关的参数，应为本身并没有学过加密，这里我就不多说了，但是经过调试，我们可以知道b、c是定值 **b =010001** c是一大串字符串。见下图。
 ![8](8.png)
 - 最后我们具体分析一下d函数，经过N次调试，我发现这其实和我的想法差不多，h是一个字典，包含了我们需要的两个参数。encText是由两次AES加密产生的及两次b，加密字符串是一样的，然后密钥第一次是个定值**0CoJUm6Qyw8W8jud**，第二次是16位随机数，也相当于定值。所以encText就出来了，params是由一次RSA加密产生的，并且只与16位的随机数有关，这里就清楚为什么我让随机数直接等于**FwtEYduOXlNEHbLP**，哈哈。因为我调试的时候，刚好出现了这么个随机数，于是我就直接拿过来用了，这个随机数对应的encSecKey = **81e7a41af9830200d5606be1a632e57eb0006b3cdae579127115c6323d4c4802f3af9efcee21d9f4126dde266773cbd795f19ae44028f9f8d038cd62d2816952fa99bb61ecb5fba87d5b178ff4b982ee34c7491808f7cb774554a0235a210caf2e5e867a0e2ebdf6f994be1b198ab43b14ce1f7cfa6f80b9070dea5fc5d6c712**
 ![](9.png)

 ## 用python重写js加密

 - 经过js加密码的分析，我用python实现了一下AES加密，具体代码如下，包含两个参数，一个是需要加密的字符串，一个是密钥具体如下
 ```python
 def AES_encrypt(text, key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, "0102030405060708")
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text
 ```
 - 两次调用这个函数。得到结果与调试的结果对比，一模一样。哈哈，上代码、上图
 ```python
f_key = "0CoJUm6Qyw8W8jud"
text = "{\"rid\":\"R_SO_4_32785700\",\"offset\":\"20\",\"total\":\"true\",\"limit\":\"20\",\"csrf_token\":\"\"}"
rs = AES_encrypt(text, f_key)
params = AES_encrypt(str(rs)[2:-1], "FwtEYduOXlNEHbLP")
 ```
 这里解释一下，text是我进过N次调试得出的，因为在请求评论之前，text有好几个值来验证其他的东西，这里我大概理解了一下text的含义，这里我们只要知道offset是偏移量，limit是每次请求多少条，比如你请求前二十条则offset=0，limit = 20，我上面的是请求20-40条。
 ![](10.png)
 ![](11.png)

 - 然后直接获取的encSecKey直接赋值就好啦，结合这两个参数，我们的请求参数就构造好了，直接POST吧，就能得到评论啦，哈哈，上代码，上图
 ```python
 data = {
    'params': params,
    'encSecKey': encSecKey
}
headers = {
    'Accept-Language':"zh-CN,zh;q=0.9,en;q=0.8",
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',

    'Cookie': 'appver=1.5.0.75771',
    'Referer': 'http://music.163.com/'
}
url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_32785700?csrf_token="
raw = requests.post(url,headers=headers, data=data)
print(raw.json())
 ```
 ![](12.png)

## 解析json，获取评论
- 上面我们已经获取了原始数据，接下来我们从json数据中获取我们需要的评论
```python
def getComment(raw, comments):
    comment = comments
    contents = raw["comments"]
    for content in contents:
        part = []
        content.pop('beReplied')
        part.append(content["user"]['nickname'])
        part.append(content["content"])
        part.append(content["time"])
        comment.append(part)
    return comment

def getAll(id,total,limit):
    comment = []
    for i in range(0, int(total), 100):
        raw = getRawData.getRawJson(id, i.__str__(), limit)
        comment = getComment(raw, comment)
    return comment
```
- 获取了全部的评论之后，我们将其写入csv文件
```python
def getCSV(id,total, csv_name):
    comment = getAll(id, total, '100')
    df = pd.DataFrame(data=comment,
                  columns=['user', 'content', 'time'])
    df['content'].to_csv(csv_name+'.csv', encoding='utf-8')
```
- 获取的评论如下
![](13.png)

- 最后根据评论生成词云
```python 
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
```
- 最终效果如下
![](14.png)
![](15.png)
