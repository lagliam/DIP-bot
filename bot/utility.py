import os


def image_list():
    directory = '../images/'
    images = []
    for filename in os.listdir(directory):
        if (filename.lower().endswith(".jpg")
                or filename.lower().endswith(".png")
                or filename.lower().endswith(".gif")
                or filename.lower().endswith(".jpeg")):
            images.append(filename)
            continue
        else:
            continue
    return images


def write_viewed_image_list_for_guild(filename, guild_id=None):
    with open(f'../guilds/images_{guild_id}.txt', 'a+') as f:
        f.write("%s\n" % filename)


def file_to_array(filename):
    array = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            array = f.readlines()
    return array