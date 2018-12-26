# coding:utf-8
"""
__file__

    task_manager.py

__description__

    This file provides the basic functions of tasks management.

——time——

    2018年09月25日12:14:53

__author__

    Weihua Jin <wh.jin@hotmail.com>

"""

import sys
import importlib
import json
import datetime
import multiprocessing
from kafka import KafkaConsumer
from kafka import KafkaProducer

# from BaseHTTPServer import BaseHTTPRequestHandler
# import http.server
# from svm_detect import conver_images
# import cgi
# import json
# import os
# import _thread
# import requests
# import argparse
import numpy as np

import http.server
from TEST_SpatialNets import conver_images
import cgi
import json
import os
import _thread
import requests
import argparse
from log_utils import write_json_logs

def get_bound(detail_json):
    bound_list = []
    for i,(lat1,lat2,lat3,lat4,lon1,lon2,lon3,lon4) in enumerate(zip(detail_json['lat1'],detail_json['lat2'],detail_json['lat3'], detail_json['lat4'],detail_json['lon1'],detail_json['lon2'],detail_json['lon3'], detail_json['lon4'])):
        w = min(lon1,lon2,lon3,lon4)
        s = min(lat1,lat2,lat3,lat4)
        e = max(lon1,lon2,lon3,lon4)
        n = max(lat1,lat2,lat3,lat4)
        bound = [w,s,e,n]
        bound_list.append(bound)
    return bound_list

def start_detect(ip_port, detail_json):

    model_path_list = os.listdir(detail_json['initialization'])
    print(model_path_list)
    model_path = os.path.join(detail_json['initialization'], model_path_list[0])
    print(model_path)
    bound_list = get_bound(detail_json)
    try:
        for idx,(img_path,img_save_path,img_uid,img_thumbnail_save_path, bound ) in enumerate(zip(detail_json['images_url'],detail_json['result_list'],detail_json['app_images_uid'], detail_json['thumbnail_list'], bound_list)):
            print(img_path,img_save_path,img_uid,img_thumbnail_save_path)
            conver_images(img_path,model_path,bound,img_save_path,img_thumbnail_save_path,img_uid,detail_json['uid'], ip_port,detail_json['userid'])
        back_json ={}
        back_json['uid'] = detail_json['uid']
        back_json['status'] = 1
        url = "http://" + ip_port+ "/model-app/DoneAppMissionFromGPU"
        #         url = "http://192.168.88.151:8989"
        r = requests.post(url, json=back_json)
        write_json_logs(back_json)
    except Exception as err:
        
        back_json ={}
        back_json['uid'] = detail_json['uid']
        back_json['status'] = 0
        url = "http://" + ip_port+ "/model-app/DoneAppMissionFromGPU"
        #         url = "http://192.168.88.151:8989"
        r = requests.post(url, json=back_json)
        write_json_logs(back_json)
        print(err)
        info ={}
        info['error'] = str(err)
        write_json_logs(info)
        return 

    
    return


def loader_script(name, task_uid, kafkaipport, ip_port, detail_json):
    """执行任务脚本
    Arguments:
        name {[string]} -- [参数]
        script_name {[string]} -- [脚本名称]
        task_uid {[string]} -- [任务uid]
        user_id {[int]} -- [用户id]
        bbox {[list]} -- [可视范围]
        out_shape {[int]} -- [输出大小]
    Returns:
        [type] -- [description]
    """

    producer = KafkaProducer(
        bootstrap_servers=[kafkaipport],
        value_serializer=lambda m: json.dumps(m).encode('utf-8'))
    try:

        # 向消息队列发送任务创建的消息
        producer.send(
            'return_status', {
                "uid": task_uid,
                "topic": "return_status",
                "msg": "create",
                "name": name
            })

        start_detect( ip_port, detail_json )
        # 向消息队列发送任务执行成功的消息
        producer.send(
            'return_status', {
                "uid": task_uid,
                "topic": "return_status",
                "msg": "success",
                "name": name
            })
    except Exception as err:
        # 向消息队列发送任务执行失败的消息
        producer.send('return_status', {
            "uid": task_uid,
            "topic": "return_status",
            "msg": "fail",
            "name": name
        })
        print(err)
        return False, str(err)
    else:
        return True


def run(kafkaipport, ip_port):
    """执行任务
    """

    # pool = multiprocessing.Pool(processes=config.max_job_count)
    # pool.apply_async(test, (
    #     'fuck',
    #     'you',
    # ))

    # pool.close()
    # pool.join()

    consumer = KafkaConsumer(
        'topic-dl-class',
        group_id='0',
        enable_auto_commit=False,
        bootstrap_servers=[kafkaipport])
    copyinfo = []
    for message in consumer:
        consumer.commit()
        try:
            if isinstance(message.value, bytes):
                info = json.loads(message.value.decode('utf-8'))
            else:
                info = json.loads(message.value)
            print(info)
            # kafka消息会莫名的重复，过滤重复
            if info == copyinfo:
                continue
            copyinfo = info
            params = json.loads(info['msg'])
            # user_id = params['user_id']
            # script_name = params['uid']
            # user_id = 4
            print(info)
            write_json_logs(info)
            if params['model_type'] == 1:
                task_uid = info['uid']
                name = info['name']
                loader_script(name, task_uid, kafkaipport, ip_port, params)

            # params = json.loads(info['msg'])
            # user_id = params['user_id']
            # script_name = params['uid']
            # user_id = 4
            # print(info)
            # if info['model_type'] == 1:
            #     task_uid = info['task_uid']
            #     name = info['name']
            #     loader_script(name, task_uid, kafkaipport, ip_port, info)
        except Exception as e:
            print(str(e))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_port', default='192.168.88.168:8076', type=str)
    parser.add_argument('--port', default=6969, type=int)
    parser.add_argument('--kafka_server', default='192.168.88.168:9092', type=str)
    args = parser.parse_args()
    ip_port = args.ip_port
    port = args.port
    kafkaipport = args.kafka_server
    run( kafkaipport, ip_port )
