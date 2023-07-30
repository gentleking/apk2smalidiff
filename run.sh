#!/bin/bash

./classDiff.py ../samples/hope-3-10-5-7.apk ../samples/hope-3-10-6-2.apk > class_diff_hope.txt

#./classDiff.py ../samples/OYO酒店-5-9.apk ../samples/OYO-5-11.apk > class_diff_oyo.txt 

./classDiff.py ../samples/douban-7-17-1.apk ../samples/douban-7-20-0.apk > class_diff_douban.txt

./classDiff.py ../samples/JJ斗地主-5-14-01.apk ../samples/JJ斗地主-5-14-02.apk > class_diff_jjdoudizhu.txt

./classDiff.py ../samples/adidas-4-17-1.apk ../samples/adidas-4-18-2.apk > class_diff_adidas.txt

# ./classDiff.py ../samples/世纪佳缘-9-5-1.apk ../samples/世纪佳缘-9-5-5.apk > class_diff_shijijiayuan.txt

./classDiff.py ../samples/苏鲜生活-1-9-1.apk ../samples/苏鲜生活-1-9-3.apk > class_diff_suxianshenghuo.txt

./classDiff.py ../samples/马蜂窝旅游-10-7-3.apk ../samples/马蜂窝旅游-10-7-6.apk > class_diff_mafengwo.txt