import getRawData
import pandas as pd
raw = getRawData.getRawJson('R_SO_4_32785700', '0', '20')


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


def getCSV(id,total, csv_name):
    comment = getAll(id, total, '100')
    df = pd.DataFrame(data=comment,
                  columns=['user', 'content', 'time'])
    df['content'].to_csv(csv_name+'.csv', encoding='utf-8')


