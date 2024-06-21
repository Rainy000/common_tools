import os
import shutil

IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
                  '.tiff', '.webp')

VIDEO_EXTENSIONS = ('.mp4', '.avi')
PLAIN_EXTENTIONS = ('.txt',)
RICH_EXTENTIONS = ('.xml', '.json')
EXTENSIONS_LIST = ['image', 'video', 'plain', 'rich']


def is_file(file_name, type):
    file_name = file_name.lower()
    if type == 'image':
        return any(file_name.endswith(ext) for ext in IMG_EXTENSIONS)
    if type == 'plain':
        return any(file_name.endswith(ext) for ext in PLAIN_EXTENTIONS)
    if type == 'rich':
        return any(file_name.endswith(ext) for ext in RICH_EXTENTIONS)
    if type == 'video':
        return any(file_name.endswith(ext) for ext in VIDEO_EXTENSIONS)


def get_file_list(dirpath, type='image', full_path=False):
    assert type in EXTENSIONS_LIST, '{} is invalid, only support {}'.format(type, EXTENSIONS_LIST)
    files_list = []
    if not os.path.exists(dirpath):
        print('{} not exists'.format(dirpath))
    else:
        fullDirpath = os.path.expanduser(dirpath)
        for root, _ , fnames in sorted(os.walk(fullDirpath)):
            for fname in sorted(fnames):
                if is_file(fname, type):
                    if full_path:
                        files_list.append(os.path.join(root, fname))
                    else:
                        files_list.append(fname)
    return files_list

def delete_file(file_path):
    assert os.path.isfile(file_path), "{} is't file".format(file_path)
    os.remove(file_path)


def copy_file(src_file, target_file):
    assert os.path.isfile(src_file), "{} is't file".format(src_file)
    shutil.copyfile(src_file, target_file)

def read_file(file_path):
    assert os.path.isfile(file_path), "{} is't file".format(file_path)
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        contents = f.readlines()
    return contents


def write_file(file_path, contents):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(contents)
    


def annotation_cls_calibration(root, subdir, savedir):
    """
        correct annotation class information
    """
    file_path = os.path.join(root, subdir)
    filelists = get_file_list(file_path, type='txt')

    save_path = os.path.join(root, savedir)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    for file_name in filelists:
        src_file_path = os.path.join(file_path, file_name)
        contents = read_file(src_file_path)
        for i in range(len(contents)):
            if contents[i][0] != '0':
                contents[i] = '0' + contents[i][1:]
        target_file_path = os.path.join(save_path, file_name)
        write_file(target_file_path, contents)

def sample_data_with_freq(root, subdir, savedir, freq):
    """
        sample image with frequency
    """
    file_path = os.path.join(root, subdir)
    filelists = get_file_list(file_path, type='image')

    save_path = os.path.join(root, savedir)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    for file_name in filelists:
        index = int(os.path.splitext(file_name)[0].split('_')[-1])
        if index % freq == 0:
            copy_file(os.path.join(file_path, file_name),
                      os.path.join(save_path, file_name))
        else:
            pass

def check_image_and_label(root, subdir):
    """
        check if image and label file exist, if not, delete image
    """
    file_path = os.path.join(root, subdir)
    image_lists = get_file_list(file_path, type='image', full_path=False)

    for image_file in image_lists:
        image_name = os.path.splitext(image_file)[0]
        label_file = image_name+'.txt'
        if not os.path.exists(os.path.join(file_path, label_file)):
            delete_file(os.path.join(file_path, image_file))


