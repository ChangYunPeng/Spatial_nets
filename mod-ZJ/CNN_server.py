# from BaseHTTPServer import BaseHTTPRequestHandler
import http.server
from TEST_SpatialNets import conver_images
import cgi
import json
import os
import _thread
import requests
import argparse

def start_detect(detail_json, ip_port):

    model_path_list = os.listdir(detail_json['initialization'])
    print(model_path_list)
    model_path = os.path.join(detail_json['initialization'], model_path_list[0])
    print(model_path)
    try:
        for idx,(img_path,img_save_path,img_uid,img_thumbnail_save_path) in enumerate(zip(detail_json['images_url'],detail_json['result_list'],detail_json['app_images_uid'], detail_json['thumbnail_list'])):
            print(img_path,img_save_path,img_uid,img_thumbnail_save_path)
            conver_images(img_path,model_path,img_save_path,img_thumbnail_save_path,img_uid,detail_json['uid'], ip_port)
    except:
        return 

    back_json ={}
    back_json['uid'] = detail_json['uid']
    url = "http://" + ip_port+ "/model_app/DoneAppMissionFromGPU"
    #         url = "http://192.168.88.151:8989"
    r = requests.post(url, json=back_json)
    return

class http_server:
    def __init__(self,  port, ip_Port):
        
        server = http.server.HTTPServer(('', port), TodoHandler)
        server.my_ip_Port = ip_Port
        server.serve_forever()


        
class TodoHandler(http.server.BaseHTTPRequestHandler):
    TODOS = []

    def do_GET(self):
        if self.path != '/':
            self.send_error(404, "File not found.")
            return

        # Just dump data to json, and return it
        message = json.dumps(self.TODOS)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(message)

    def do_POST(self):
        """Add a new todo

        Only json data is supported, otherwise send a 415 response back.
        Append new todo to class variable, and it will be displayed
        in following get request
        """
        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        if ctype == 'application/json':
            length = int(self.headers['content-length'])
            post_values = json.loads(self.rfile.read(length).decode('utf-8'))
            print(post_values)
            print(self.server.my_ip_Port)
            result = {}
            _thread.start_new_thread( start_detect, (post_values, self.server.my_ip_Port))

            try:
                
                result['statue'] = "start detecting ..."
            except:
                result['statue'] = "Error: unable to start thread"

           

                 
            # print(json.dumps(post_values))
        else:
            self.send_error(415, "Only json data is supported.")
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # self.wfile.write(result)


if __name__ == '__main__':
    # Start a simple server, and loop forever
    
    # from BaseHTTPServer import HTTPServer

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_port', default='192.168.88.168:8096', type=str)
    parser.add_argument('--port', default=8998, type=int)
    args = parser.parse_args()
    ip_port = args.ip_port
    port = args.port

    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    server = http_server( port, ip_port)
        

#     server = HTTPServer(('', 6969), TodoHandler)
#     print("Starting server, use <Ctrl-C> to stop")
#     server.serve_forever()
