import os
import requests


from tools import makedir, time_transfrom

def download_video(save_path, json_content, log_file):
    '''
    video_name = "tenantId" + "_" +\
                 "projectId" + "_" + \
                 "deviceId" +  "_" + \
                 "fromTime" + "_" +\
                 "toTime" + ".mp4"
    '''
    if isinstance(json_content, list):
        with open(log_file, 'w') as exf:
            for e in json_content:
                from_time_add8h = time_transfrom(input_time=(e['fromTime'] + 28800000), mode=1)
                to_time_add8h = time_transfrom(input_time=(e['toTime'] + 28800000), mode=1)
                video_name = e['tenantId'] + '_' + e['projectId'] + '_' + e[
                    'deviceId'] + '_' + str(from_time_add8h) + '_' + str(to_time_add8h) + '.mp4'
                video_url = e['videoUrl']
                try:
                    sub_path = os.path.join(e['tenantName'], e['projectName'], e['deviceName'])
                    abs_path = os.path.join(save_path, sub_path)
                    makedir(abs_path)
                    video_file = os.path.join(abs_path, video_name)
                    if not os.path.exists(video_file):
                        r = requests.get(video_url, stream=True)
                        with open(video_file, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=1024 * 1024):
                                if chunk:
                                    f.write(chunk)
                        f.close()
                    else:
                        exf.write('{} already been downloaded\n'.format(video_url))
                except Exception as err:
                    exf.write('{}, {}\n'.format(video_url, err))
                    continue
        exf.close()
    else:
        print('json file content must be united and is list type, please check.')
