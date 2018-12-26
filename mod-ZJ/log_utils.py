

import datetime
import json

def write_json_logs(info={}):
    with open('/root/workdir/log.txt', 'a') as f:
        f.writelines(json.dumps(info))
        f.writelines('\n')
        timenow = datetime.datetime.now()
        f.writelines(str(timenow))
        f.writelines('\n')
    return
