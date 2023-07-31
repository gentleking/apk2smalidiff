#!/bin/bash

./classDiff.py ../samples/hope-3-10-5-7.apk ../samples/hope-3-10-6-2.apk > class_diff_hope.txt

#./classDiff.py ../samples/OYO酒店-5-9.apk ../samples/OYO-5-11.apk > class_diff_OYO酒店.txt 

./classDiff.py ../samples/douban-7-17-1.apk ../samples/douban-7-20-0.apk > class_diff_douban.txt

./classDiff.py ../samples/JJ斗地主-5-14-01.apk ../samples/JJ斗地主-5-14-02.apk > class_diff_JJ斗地主.txt

./classDiff.py ../samples/adidas-4-17-1.apk ../samples/adidas-4-18-2.apk > class_diff_adidas.txt

# ./classDiff.py ../samples/世纪佳缘-9-5-1.apk ../samples/世纪佳缘-9-5-5.apk > class_diff_世纪佳缘.txt

./classDiff.py ../samples/苏鲜生活-1-9-1.apk ../samples/苏鲜生活-1-9-3.apk > class_diff_苏鲜生活.txt

./classDiff.py ../samples/马蜂窝旅游-10-7-3.apk ../samples/马蜂窝旅游-10-7-6.apk > class_diff_马蜂窝旅游.txt

./classDiff.py ../samples/天天果园-8-1-16.apk ../samples/天天果园-8-1-17.apk > class_diff_天天果园.txt
