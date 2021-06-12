import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import bot.utility as utility
import matplotlib.font_manager as fm

LINE1="FUCK"
LINE2="OFF"

async def get_motivated():
    image_list = utility.image_list('../motivashon/')
    image = image_list.pop(random.randrange(len(image_list)))

    img = Image.open("../motivashon/"+image)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 200)
    draw.text( (150, 1800), get_quote(), (255,255,255), font)
    img.save('../motivashon/scuff_motivation.jpg')
    
    # make sure to delete image after sending

def get_quote():
    text1 = open("../motivashon/motivashon1.txt", 'r')
    t1 = [line.split(',') for line in text1.readlines()]

    text2 = open("../motivashon/motivashon2.txt", 'r')
    t2 = [line.split(',') for line in text2.readlines()]
    return t1.pop(random.randrange(len(t1)))[0]+t2.pop(random.randrange(len(t2)))[0]
