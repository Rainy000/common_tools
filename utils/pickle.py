import os
import pickle

def dump_pickle(urls, pickle_file):
    all_videos = []
    for url in urls:
        url_dict = {}
        url_dict['tenantName'] = url['tenantName']
        url_dict['tenantId'] = url['tenantId']
        url_dict['projectName'] = url['projectName']
        url_dict['projectId'] = url['projectId']
        url_dict['deviceName'] = url['deviceName']
        url_dict['deviceId'] = url['deviceId']

        url_dict['sourceType'] = url['sourceType']
        url_dict['fromTime'] = url['fromTime']
        url_dict['toTime'] = url['toTime']

        url_dict['videoUrl'] = url['videoUrl']

        all_videos.append(url_dict)
    if not os.path.exists(pickle_file):
        with open(pickle_file, 'wb') as f:
            pickle.dump(all_videos, f, pickle.HIGHEST_PROTOCOL)
    else:
        pass


def load_pickle(pickle_file):
    pass