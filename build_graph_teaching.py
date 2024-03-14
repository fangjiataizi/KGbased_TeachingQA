import json
from py2neo import Graph, Node, Relationship

# 连接neo4j数据库，输入你的用户名、密码和数据库地址
graph =Graph("neo4j+s://b4aa5de0.databases.neo4j.io",  # neo4j服务器的地址
            user="neo4j",  # 数据库用户名
            password="dnt8t8RRucD60d_Zr4wJp05TxQ4kaOM9VrgiCTu2qLA")  # 数据库密码
# 读取json文件
with open('data/teaching.json', 'r') as f:
    lines = f.readlines()

# 遍历每一行，每一行是一个独立的json对象
for line in lines:
    print(line)
    item = json.loads(line)
    if item['type'] == 'node':
        node = Node(*item['labels'], **item['properties'])
        graph.create(node)
    elif item['type'] == 'relationship':
        start_node = Node(*item['start']['labels'], **item['start']['properties'])
        end_node = Node(*item['end']['labels'], **item['end']['properties'])
        relationship = Relationship(start_node, item['label'], end_node)
        graph.create(relationship)