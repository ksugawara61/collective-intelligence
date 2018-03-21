from PIL import Image,ImageDraw

def readfile(filename):
    lines = [line for line in open(filename)]

    # 最初の行は列のタイトル
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # それぞれの行の最初の列は行の名前
        rownames.append(p[0])

        # 行の残り部分が行のデータ
        data.append([float(x) for x in p[1:]])
        
    return rownames, colnames, data

from math import sqrt

def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    # 平方の合計
    sum1Sq = sum([pow(v,2) for v in v1])
    sum2Sq = sum([pow(v,2) for v in v2])

    # 積の合計
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    # ピアソンによるスコア算出
    num = pSum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))
    if den == 0:
        return 0

    return 1.0 - num/den

class bicluster:
    def __init__(self, vec, left=None, right = None, distance = 0.0, id = None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def hcluster(rows, distance = pearson):
    distances = {}
    currentclustid = -1

    # クラスタは最初は行たち
    clust = [bicluster(rows[i], id = i) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        # すべての組をループし、もっとも距離の近い組を探す
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                # 距離をキャッシュしてあればそれを使う
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # ２つのクラスタの平均を計算
        mergevec = [
            (clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0
            for i in range(len(clust[0].vec))]

        # 新規クラスタの生成
        newcluster = bicluster(mergevec, left = clust[lowestpair[0]],
                               right = clust[lowestpair[1]],
                               distance = closest, id = currentclustid)

        # 元のセットではないクラスタのIDは負にする
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]

# クラスタの出力結果をプリントアウト
def printclust(clust, labels = None, n = 0):
    # 階層型のレイアウトにするためにインデントする
    for i in range(n): print(' ', end="")
    if clust.id < 0:
        print('-')
    else:
        if labels == None: print(clust.id)
        else: print(labels[clust.id])

    # 右と左の枝を表示する
    if clust.left != None:
        printclust(clust.left,  labels = labels, n = n + 1)
    if clust.right != None:
        printclust(clust.right, labels = labels, n = n + 1)


def getheight(clust):
    # 終端であれば高さは1にする
    if clust.left == None and clust.right == None:
        return 1

    # そうでなければ高さはそれぞれの枝の高さの合計
    return getheight(clust.left) + getheight(clust.right)

def getdepth(clust):
    # 終端への距離は0.0
    if clust.left == None and clust.right == None:
        return 0

    # 枝の距離は２つの方向の大きい方にそれ自身の距離を足したもの
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

def drawdendrogram(clust, labels, jpeg = 'clusters.jpg'):
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    scaling = float(w - 150) / depth

    img = Image.new('RGB', (w,h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line((0, h / 2, 10, h / 2), fill = (255, 0, 0))

    drawnode(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')


def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        ll = clust.distance * scaling

        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill = (255, 0, 0))

        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill = (255, 0, 0))

        draw.line((x, bottom - h2 / 2, x + 11, bottom - h2 / 2), fill = (255, 0, 0))

        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom + h2 / 2, scaling, labels)

    else:
        draw.text((x + 5, y - 7), labels[clust.id], (0,0,0))
