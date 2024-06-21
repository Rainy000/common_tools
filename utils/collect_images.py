import os
import cv2

def save_image_from_camera(camera_id, interval, save_flag, level=3, prefix='', save_path=''):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    video = cv2.VideoCapture(camera_id)
    # video.set(3, 1280)
    # video.set(4, 800)

    fps = video.get(cv2.CAP_PROP_FPS)
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print('fps={}\nsize={}\n'.format(fps, size))
    frame_idx = 0
    save_path = os.path.join(save_path, prefix+'_{}.png')
    while True:
        ret, frame = video.read()
        if not ret:
            continue
        frame_idx += 1
        if frame_idx % interval == 0:
            if save_flag:
                cv2.imwrite(save_path.format(frame_idx), frame, [cv2.IMWRITE_PNG_COMPRESSION, level])
        cv2.imshow("A video", frame)
        c = cv2.waitKey(1)
        if c == 27:
            break
    video.release()
    cv2.destroyAllWindows()


import argparse
from PyCameraList.camera_device import list_video_devices
def args_parse():
    parser = argparse.ArgumentParser(description='QR code detect.')
    parser.add_argument('root', type=str, help='Root path for operation.')
    parser.add_argument('prefix', type=str, help='Prefix of image name')
    parser.add_argument(
        '--camera-id', 
        type=int,
        default= 0, 
        help='Camera id.'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=25,
        help='Image sample interval.'
    )
    parser.add_argument(
        '--save',
        action='store_true', 
        help='If save image or not.'
    )
    parser.add_argument(
        '--level',
        type=int,
        default=3,
        help='Compression level for png format'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = args_parse()
    print(args)
    cameras_list = [element[0] for element in list_video_devices()]
    if args.camera_id in cameras_list:
        save_image_from_camera(args.camera_id, 
                              args.interval,
                              args.save,
                              args.level,
                              args.prefix,
                              args.root)
    else:
        print('Invalid camera id, only support: {}'.format(cameras_list))