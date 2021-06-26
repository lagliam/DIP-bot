import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import bot.utility as utility
import matplotlib.font_manager as fm


async def get_motivated():
    image_list = utility.image_list('../motivashon/')
    image = image_list.pop(random.randrange(len(image_list)))

    img = Image.open("../motivashon/"+image)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 200)
    text = get_quote()
    w, h = draw.textsize(text, font)
    drawTextWithOutline(text, img.width/2 - w/2, img.height/2 + h/3, draw, font)
    basewidth = 1024
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    img.save('../motivashon/scuff_motivation.jpg')
    
    # make sure to delete image after sending

async def get_insulted(t):
    text = utility.wrap_by_word(t, 4)
    image_list = utility.image_list('../motivashon/')
    image = image_list.pop(random.randrange(len(image_list)))

    img = Image.open("../motivashon/"+image)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 200)
    w, h = draw.textsize(text, font)
    drawTextWithOutline(text, img.width/2 - w/2, img.height/2 + h/3, draw, font)
    basewidth = 1024
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    img.save('../motivashon/scuff_insult.jpg')
    
    # make sure to delete image after sending

def get_quote():
    text1 = open("../motivashon/motivashon1.txt", 'r')
    t1 = [line.split(',') for line in text1.readlines()]

    text2 = open("../motivashon/motivashon2.txt", 'r')
    t2 = [line.split(',') for line in text2.readlines()]
    return t1.pop(random.randrange(len(t1)))[0]+t2.pop(random.randrange(len(t2)))[0]

def drawTextWithOutline(text, x, y, draw, font):
        draw.text((x-10, y-10), text,(0,0,0),font=font)
        draw.text((x+10, y-10), text,(0,0,0),font=font)
        draw.text((x+10, y+10), text,(0,0,0),font=font)
        draw.text((x-10, y+10), text,(0,0,0),font=font)
        draw.text((x, y), text, (255,255,255), font=font)
        return
