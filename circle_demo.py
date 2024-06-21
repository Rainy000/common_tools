import os
import cv2
import argparse
import numpy as np
from qrcode.circle_detect import circle_detect


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
        '--resize',
        action='store_true', 
        help='Resize the camera width & height prop or not.'
    )
    parser.add_argument(
        '--color',
        action='store_true', 
        help='Convert the camera image color or not.'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save image or not.'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = args_parse()
    print(args)

    root = args.root
    prefix = args.prefix
    camera_id = args.camera_id
    interval = args.interval
    resize = args.resize
    color = args.color
    save = args.save

    video = cv2.VideoCapture(camera_id)
    if resize:
        video.set(3, 1280)
        video.set(4, 800)

    fps = video.get(cv2.CAP_PROP_FPS)
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print('fps={}\nsize={}\n'.format(fps, size))

    frame_idx = 0
    while True:
        ret, frame = video.read()
        if not ret:
            continue
        frame_idx += 1

        if color:
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = frame
        
        detected_circles = circle_detect(gray_image)
        if detected_circles is None:
            print('Nothing.')
            if save:
                save_full_path = os.path.join(root, 'houghTransform', 'no_det')
                if not os.path.exists(save_full_path):
                    os.makedirs(save_full_path)
                cv2.imwrite(os.path.join(save_full_path, prefix+'_'+str(frame_idx)+'.png'), 
                            gray_image)
        else:
            print('{} circles detected.'.format(detected_circles.shape[1]))
            # Convert the circle parameters a, b and r to integers.
            detected_circles = np.uint16(np.around(detected_circles))

            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]

                # Draw the circumference of the circle.
                gray_image = cv2.circle(gray_image, (a, b), r, (255, 0, 0), 3)

                if save:
                    save_full_path = os.path.join(root, 'houghTransform', 'det')
                    if not os.path.exists(save_full_path):
                        os.makedirs(save_full_path)
                    cv2.imwrite(os.path.join(save_full_path, prefix+'_'+str(frame_idx)+'.png'), 
                                gray_image)
        
        cv2.imshow("A video", gray_image)
        c = cv2.waitKey(1)
        if c == 27:
            break
    video.release()
    cv2.destroyAllWindows()
    
    