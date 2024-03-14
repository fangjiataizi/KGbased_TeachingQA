def get_fewshot_examples(openai_api_key):
    return f"""
    以下是一些示例：
#有哪些活动采用了模型应用环节？
MATCH (m:Model)-[:应用环节]->(a:Activity) RETURN a

#哪些能力被设定为目标，以支持“蜘蛛图头脑风暴”活动？
MATCH (a:Ability)-[:能力目标]->(b:Activity)
WHERE b.活动设计背景 = "蜘蛛图头脑风暴"
RETURN a.name
"""


#
# 你的任务是将关于Neo4j数据库内容的问题转换为Cypher查询。以下是一些示例：
#
# #Emil Eifrem与Michael Hunger之间有什么关联？
# MATCH (p1:Person {{name:"Emil Eifrem"}}), (p2:Person {{name:"Michael Hunger"}})
# MATCH p=shortestPath((p1)-[*]-(p2))
# RETURN p
#
# #关于Google有什么最新消息？
# MATCH (o:Organization {{name:"Google"}})<-[:MENTIONS]-(a:Article)-[:HAS_CHUNK]->(c)
# RETURN a.title AS title, c.text AS text, c.date AS date
# ORDER BY date DESC LIMIT 3
#
# #有关回归办公政策的新闻吗？
# CALL apoc.ml.openai.embedding(["Are there any news regarding return to office policies?"],
#    "{openai_api_key}") YIELD embedding
# MATCH (c:Chunk)
# WITH c, gds.similarity.cosine(c.embedding, embedding) AS score
# ORDER BY score DESC LIMIT 3
# RETURN c.text, score
#
# #Microsoft的回归办公政策是什么？
# CALL apoc.ml.openai.embedding(["What is Microsoft policy regarding to the return to office?"], "{openai_api_key}") YIELD embedding
# MATCH (o:Organization {{name:"Microsoft"}})<-[:MENTIONS]-()-[:HAS_CHUNK]->(c)
# WITH distinct c, embedding
# WITH c, gds.similarity.cosine(c.embedding, embedding) AS score
# ORDER BY score DESC LIMIT 3
# RETURN c.text, score
# 在搜索文本块中的特定信息时，永远不要使用CONTAINS子句，而应始终使用apoc.ml.openai.embedding和gds.similarity.cosine函数，如示例中所示。返回文本块时，始终返回恰好三个块，不多也不少。记住，要在文本块内查找信息，使用apoc.ml.openai.embedding和gds.similarity.cosine函数，而不是使用CONTAINS。
