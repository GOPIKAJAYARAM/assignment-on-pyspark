# -*- coding: utf-8 -*-
"""Assignment_Solution_Gopika_Jayaram.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14BNHVw3pL0vhp3hcY4Zid_VabJoYIb1_

**SECTION 1**
"""

!apt-get update -y

!apt-get install openjdk-8-jdk-headless -qq > /dev/null

!wget -q https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop2.7.tgz

!tar xf spark-3.1.2-bin-hadoop2.7.tgz

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.1.2-bin-hadoop2.7"

!pip install -q findspark
import findspark
findspark.init()

from pyspark.sql import SparkSession
spark = (SparkSession
.builder
.appName("<app_name>")
.getOrCreate())

from google.colab import drive
drive.mount('/content/gdrive')

chess_info = spark.read.csv("/content/gdrive/MyDrive/Groker/chess_wc_history_game_info.csv",header="true")

chess_moves = spark.read.csv("/content/gdrive/MyDrive/Groker/chess_wc_history_moves.csv",header="true")

eco_codes = spark.read.csv("/content/gdrive/MyDrive/Groker/eco_codes.csv",header="true")

from pyspark.sql.functions import split,col

"""**SECTION 2**

1. List of Winners of Each World champions Trophy Hint: Total Result of all rounds of Tournament for that player is considered as that player's
Score/Result.
Result attributes: winner, tournament_name
"""

chess_info.show(truncate=False)

#Splitting winner column to get the first name
chess_info1=chess_info.withColumn("winner_split",split(col("winner"),"[,]"))\
          .withColumn("winner1",col("winner_split")[0]).drop("winner_split","winner")

chess_info1.show(4)

che =chess_info1.groupBy("tournament_name","winner1").count().where("winner1 !='draw'")

import pyspark.sql.functions as F

result1 = che.groupBy("tournament_name") \
    .agg(F.max(F.struct("count", "winner1")).alias("max")) \
    .selectExpr("tournament_name","max.winner1 as winner", "max.count as winning_count")
wc=result1

result_1=result1.select("tournament_name","winner")
result_1.show(5)

"""2. List of Players with number of times they have won Tournament in descending order(Max to min).
Result attributes: player_name, number_of_wins
"""

result2=wc.sort('winning_count',ascending=False)
result2=result2.withColumnRenamed("winning_count","number_of_wins")
result2=result2.withColumnRenamed("winner","player_name")
result2=result2.select("player_name","number_of_wins")

result2.show(15)

"""3. Most and Least Popular eco move in world championship history.
Result attributes: eco, eco_name, number_of_occurences
Final result will have only two rows
"""

chess_moves.show(5)

chess_info.show(6)

eco_codes.show(6)

eco_info=eco_codes.join(chess_info, eco_codes.eco==chess_info.eco,how="inner").drop(eco_codes.eco)

eco_info_move=eco_info.join(chess_moves, eco_info.game_id==chess_moves.game_id,how="inner").drop(chess_moves.game_id)

eco_info_move.show(5)

data=eco_info_move.groupBy("eco","eco_name").count()
data=data.withColumnRenamed("count","number_of_occurences")
data1=data.sort("number_of_occurences",ascending=False)
data1=data1.limit(1)
data2=data.sort("number_of_occurences",ascending=True)
data2=data2.limit(1)

data3=data1.unionByName(data2)
data3.show()

"""4. Find the eco move with most winnings.
Ps. Use this opening move in your next chess game????
Result attributes: eco, eco_name
"""

df4=eco_info_move.select("eco","eco_name").where("winner != 'draw'")

df_4= df4.groupBy("eco","eco_name").count()
df_4=df_4.sort("count",ascending=False)
df_4=df_4.select("eco","eco_name")
df_4=df_4.limit(1)
df_4.show()

"""5. Longest and shortest game ever played in a world championship in terms of move.
Chess Funda: "move" is completed once both White and Black have played one turn. e.g If a game lasts 10 moves, both White and Black have
played 10 moves)
Result attributes: game_id, event, tournament_name, number_of_moves
Final result will have only two rows
"""

df_pre=chess_moves.groupBy("game_id").count()
df1 = df_pre.sort("count",ascending=False)
df2 = df_pre.sort("count",ascending=True)

highest_count=df1.limit(1)
lowest_count=df2.limit(1)

result5= highest_count.unionByName(lowest_count)

result05=chess_info.join(result5, chess_info1.game_id==result5.game_id, how="right").drop(result5.game_id)

result05.select("game_id","event","tournament_name","count").show()

"""6. Shortest and Longest Draw game ever Played.
Result attributes: game_id, event, tournament_name, number_of_moves
Final result will have only two rows
"""

chess_info1.show(5)

result6=chess_info1.where("winner1 = 'draw'")

result06 =result6.groupBy("tournament_name").count()

df61 = result06.sort("count",ascending=False)
df62 = result06.sort("count",ascending=True)

highest_count=df61.limit(1)
lowest_count=df62.limit(1)

result006= highest_count.unionByName(lowest_count)

result_06=chess_info.join(result006, chess_info1.tournament_name==result006.tournament_name, how="inner").drop(result006.tournament_name)

a1=result_06.select("game_id","event","tournament_name","count").limit(1)

highest_count.show()

result_06.show()

"""7. Most and Least rated Player.
Result attributes: player_name, elo
Chess Funda: elo is the rating of the player in chess tournament.
Final result will have only two rows
"""

chess_info.show(10)

chess_in1=chess_info.withColumn("black_split",split(col("black"),"[,]"))\
          .withColumn("black1",col("black_split")[0]).drop("black_split","black")
chess_info1=chess_in1.withColumn("white_split",split(col("white"),"[,]"))\
          .withColumn("white1",col("white_split")[0]).drop("white_split","white")

chess_info1=chess_info1.where("white_elo != 'null'")
chess_info1=chess_info1.where("black_elo != 'null'")

result7= chess_info1.groupBy("black1").agg(F.avg("black_elo"))
res7 = result7.sort("avg(black_elo)",ascending=False)

result7l=chess_info1.groupBy("white1").agg(F.avg("white_elo"))
res7l = result7l.sort("avg(white_elo)",ascending=True)

result71=res7.limit(1)
result72=res7l.limit(1) 

df1=result71.withColumnRenamed("black1","name")
df1=df1.withColumnRenamed("avg(black_elo)","avg_elo")

df2=result72.withColumnRenamed("white1","name")
df2=df2.withColumnRenamed("avg(white_elo)","avg_elo")


result7_final= df1.unionByName(df2)

result7_final.show()

"""8. 3rd Last Player with most Loss.
Result attributes: player_name
Final result will have only one row
"""

chess_info.show(10)

chess_loser=chess_info.withColumn("loser_split",split(col("loser"),"[,]"))\
          .withColumn("loser1",col("loser_split")[0]).drop("loser_split","loser")
chess_loser=chess_loser.where("loser != 'draw'")

result8=chess_loser.groupBy("loser1").count()
result8=result8.sort("count",ascending=False)
result8=result8.withColumnRenamed("loser1","player_name")
result8=result8.collect()[2]
result8

"""9. How many times players with low rating won matches with their total win Count.
Result attributes: player_name, win_count
"""

data= chess_info.where("winner != 'draw'")

data.show(5)

data=data.select("winner").where("winner_elo < loser_elo")

data=data.groupBy("winner").count()
result9=data.sort("count",ascending=False)
result9.show()



"""10. Move Sequence for Each Player in a Match.
Result attributes: game_id, player_name, move_sequence, move_count
"""

chess_moves.show(10)

from pyspark.sql.functions import split, reverse
chess_move1=chess_moves.withColumn("move_sequence_split",split(col("move_sequence"),"[|]"))\
          .withColumn("last_move_sequence",reverse(col("move_sequence_split"))[0]).drop("move_sequence_split","move_sequence")

chess_move1.show(6)

result10=chess_move1.select("game_id","player","last_move_sequence","move_no")

result10.show(5)



"""11. Total Number of games where losing player has more Captured score than Winning player.
Hint: Captured score is cumulative, i.e., for 3rd capture it will have score for 1, 2, and 3rd.
Result attributes: total_number_of_games Final result will have only one row
"""

chess_info.show(6)

#converting white and black column to only first name
df_info=chess_info.withColumn("black_split",split(col("black"),"[,]"))\
          .withColumn("black1",col("black_split")[0]).drop("black_split","black")
df_info=df_info.withColumn("white_split",split(col("white"),"[,]"))\
          .withColumn("white1",col("white_split")[0]).drop("white_split","white")

df_info.show(5)

import sys 
from pyspark.sql.window import Window 
import pyspark.sql.functions as F 
df_info111=df_info.where("winner != 'draw'")

cum_sum_df = df_info111.withColumn('winner_elo_cum_sum',F.sum(df_info111.winner_elo).over(Window.partitionBy("winner").orderBy().rowsBetween(-sys.maxsize,0)))
cum_sum_df =cum_sum_df.withColumn('loser_elo_cum_sum',F.sum(cum_sum_df.loser_elo).over(Window.partitionBy("loser").orderBy().rowsBetween(-sys.maxsize,0)))
cum_sum_df.show(5)

df_11=cum_sum_df.where("loser_elo_cum_sum > winner_elo_cum_sum")
result_11=df_11.count()
result_11

"""12. List All Perfect Tournament with Winner Name.
Chess Funda: Perfect Tournament means a player has won all the matches excluding draw matches. e.g Player A has won 5 matches out of 7
Matches in tournament where 2 matches are draw and player B has won 0 matches)
Result attributes: winner_name, tournament_name
"""

chess_info.show(5)

prft=chess_info.withColumn("result_split",split(col("result"),"[-]"))\
          .withColumn("resultw",col("result_split")[0]).drop("result_split")

prft=prft.withColumn("result_split",split(col("result"),"[-]"))\
          .withColumn("resultb",col("result_split")[1]).drop("result_split","result")

prft=prft.where("winner != 'draw'")

prft.show(5)

a=prft.groupBy("tournament_name","winner").agg(F.sum("resultw"),F.sum("resultb"))

a1=a.where("sum(resultb) = 0")
a1=a1.select("tournament_name","winner")
a2=a.where("sum(resultw) =0")
a2=a2.select("tournament_name","winner")

result12=a1.unionByName(a2)

result12.show()

"""13. Player with highest winning ratio.
Hint: Winning ratio: (Number of rounds won)/(Number of rounds played)
Result attributes: player_name
Final result will have only one row
"""

chess_info.show(10)

chess_info12=chess_info.withColumn("white_split",split(col("white"),"[,]"))\
          .withColumn("whitew",col("white_split")[0]).drop("white_split","white")

chess_info12=chess_info12.withColumn("black_split",split(col("black"),"[,]"))\
          .withColumn("blackw",col("black_split")[0]).drop("black_split","black")

chess_info12.show()

a1=chess_info12.groupBy("whitew").count()
a1=a1.withColumnRenamed("whitew","name")
a1=a1.withColumnRenamed("count","countw")


a2=chess_info12.groupBy("blackw").count()
a2=a2.withColumnRenamed("blackw","name")
a2=a2.withColumnRenamed("count","countb")

a=a1.join(a2,a1.name==a2.name, how ="inner").drop(a2.name)

a.show(5)

from pyspark.sql.functions import col

df_13=a.select("name",((col("countw") + col("countb"))).alias("rounds_played"))
df_13.show(30)

chess_info12.show(5)

chess_info12=chess_info12.where("winner !='draw'")
chess_info12=chess_info12.withColumn("winner_split",split(col("winner"),"[,]"))\
          .withColumn("winnerw",col("winner_split")[0]).drop("winner_split","winner")

b1=chess_info12.select("winnerw").where("whitew = winnerw")
b1=b1.groupBy("winnerw").count()
b1=b1.withColumnRenamed("count","countw")

b2=chess_info12.select("winnerw").where("blackw = winnerw")
b2=b2.groupBy("winnerw").count()
b2=b2.withColumnRenamed("count","countb")

b=b2.join(b1,b1.winnerw==b2.winnerw, how ="inner").drop(b2.winnerw)

b.show()

df_13a=b.select("winnerw",((col("countw") + col("countb"))).alias("rounds_won"))
df_13a.show(30)

result13=df_13.join(df_13a,df_13.name==df_13a.winnerw, how="inner").drop(df_13a.winnerw)

result13=result13.select("name",((col("rounds_won")/ col("rounds_played"))).alias("winning_ratio"))
result13=result13.sort("winning_ratio",ascending=False)
result13=result13.limit(1)
result13.show()

"""14. Player who had given checkmate with Pawn.
Note: Consider all events for this query
Result attributes: player_name
Final result will have only one row
"""

chess_moves.show()

result_14 = chess_moves.where("is_check_mate != 0")
result_14 = result_14.where("piece = 'P'")

result_14=chess_info.join(result_14, chess_info.game_id==result_14.game_id, how="inner").drop(result_14.game_id)

result_14=result_14.select("winner")
result_14.show()

"""15. List games where player has won game without queen.
Result attributes: game_id, event, player_name
"""

chess_moves.show(10)

df=chess_moves.where("white_queen_count = '0'")
df=df.where("black_queen_count = '0'")

df=df.select("game_id","player")

df=chess_info.join(df, chess_info.game_id==df.game_id, how="inner").drop(df.game_id)

df=df.where("winner != 'draw'")

df=df.distinct()

result_15=df.select("game_id","event","winner")

result_15.show(10,truncate=False)

"""**SECTION 3**"""

!pip install pydrive

# Commented out IPython magic to ensure Python compatibility.
def create_file(listt): 
  from pydrive.drive import GoogleDrive
  from pydrive.auth import GoogleAuth

  import os 
  gauth = GoogleAuth()
  
  gauth.LocalWebserverAuth()       
  drive = GoogleDrive(gauth)

  path = r"gdrive/MyDrive/DE_SOLUTION_Gopika_Jayaram"  
  for x in os.listdir(path):
   
    f = drive.CreateFile({'title': "DE_SOLUTION_Gopika_Jayaram"})
    f.SetContentFile(os.path.join(path, "DE_SOLUTION_Gopika_Jayaram"))
    f.Upload()
  
  pandas_df=[]
  no=1
  for i in listt:
      
      pandas_df.append(i.toPandas())

      from google.colab import drive

      drive.mount('/content/drive')
      path = 'gdrive/MyDrive/DE_SOLUTION_Gopika_Jayaram'
      
      
      f="DE_SOLUTION_Gopika_Jayaram/df."+f'{no}'+".csv"
#       %notebook+=1
      with open(path, 'w', encoding = 'utf-8-sig') as f:
        i.to_csv(f)