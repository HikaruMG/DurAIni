from __future__ import unicode_literals

import errno
import os
import sys
import tempfile
from dotenv import load_dotenv

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler 
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import *
from linebot.models import (TextSendMessage,FlexSendMessage)
import json
import time
from pathlib import Path

import cv2
import torch
from utils.plots import Annotator, colors

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# reads the key-value pair from .env file and adds them to environment variable.
load_dotenv()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


### YOLOv5 ###
# Setup
weights, view_img, save_txt, imgsz = 'yolov5l.pt', False, False, 640
conf_thres = 0.25
iou_thres = 0.45
classes = None
agnostic_nms = False
save_conf = False
save_img = True
line_thickness = 3

# Directories
save_dir = 'static/tmp/'

#------------Load model MaSakAunDI------------------
#yolov5(size=n)
#model = torch.hub.load('./', 'custom', path='leafdata_n', source='local', force_reload=True)

#yolov5(size=s)
model = torch.hub.load('./', 'custom', path='leafdata_s', source='local', force_reload=True)

#yolov5(size=m)
#model = torch.hub.load('./', 'custom', path='leafdata_m', source='local', force_reload=True)

#yolov5(size=l)
#model = torch.hub.load('./', 'custom', path='leafdata_l', source='local', force_reload=True)

#yolov5(size=x)
#model = torch.hub.load('./', 'custom', path='leaf_(yolov5x).pt', source='local', force_reload=True)
#---------------------------------------------------

#model = torch.hub.load('./' ,'custom', path='leaf_detect(1).pt', source='local', force_reload=True)
#model = torch.hub.load('./', 'custom', path='leaf26-02(yolov5l)', source='local', force_reload=True)
#model = torch.hub.load('ultralytics/yolov5', 'custom', 'runs/train/exp/weights/best.mlmodel')


def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route("/", methods=['GET'])
def home():
    return "Object Detection API"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#-------- Flex Message -------
follow_message = FlexSendMessage(
    alt_text='hello',
    contents={
  "type": "bubble",
  "size": "mega",
  "header": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "แผนการ",
            "color": "#ffffff66",
            "size": "sm"
          },
          {
            "type": "text",
            "text": "ระยะเวลาดำเนินงาน",
            "color": "#ffffff",
            "size": "xl",
            "flex": 4,
            "weight": "bold"
          }
        ]
      }
    ],
    "paddingAll": "20px",
    "backgroundColor": "#1C4E09",
    "spacing": "md",
    "height": "90px",
    "paddingTop": "22px"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "position": "absolute",
        "paddingEnd": "xxl",
        "paddingStart": "xxl",
        "offsetStart": "xxl"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "ขั้นที่ 3",
            "size": "sm",
            "gravity": "center"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "cornerRadius": "30px",
                "height": "12px",
                "width": "12px",
                "borderColor": "#B7B7B7",
                "borderWidth": "2px"
              },
              {
                "type": "filler"
              }
            ],
            "flex": 0
          },
          {
            "type": "text",
            "text": "เสร็จสิ้นกระบวนการ",
            "gravity": "center",
            "flex": 4,
            "size": "sm"
          }
        ],
        "spacing": "lg",
        "cornerRadius": "30px",
        "margin": "xl"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "contents": [
              {
                "type": "filler"
              }
            ],
            "flex": 1
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "filler"
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "width": "2px",
                    "backgroundColor": "#B7B7B7"
                  },
                  {
                    "type": "filler"
                  }
                ],
                "flex": 1
              }
            ],
            "width": "12px"
          },
          {
            "type": "text",
            "text": "รอขั้นตอนถัดไป",
            "gravity": "center",
            "flex": 4,
            "size": "xs",
            "color": "#8c8c8c"
          }
        ],
        "spacing": "lg",
        "height": "64px"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "text",
                "text": "ขั้นที่ 2",
                "gravity": "center",
                "size": "sm"
              }
            ],
            "flex": 1
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "cornerRadius": "30px",
                "width": "12px",
                "height": "12px",
                "borderWidth": "2px",
                "borderColor": "#B7B7B7"
              },
              {
                "type": "filler"
              }
            ],
            "flex": 0
          },
          {
            "type": "text",
            "text": "คำแนะนำเพิ่มเติม",
            "gravity": "center",
            "flex": 4,
            "size": "sm"
          }
        ],
        "spacing": "lg",
        "cornerRadius": "30px"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "contents": [
              {
                "type": "filler"
              }
            ],
            "flex": 1
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "filler"
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "width": "2px",
                    "backgroundColor": "#B7B7B7"
                  },
                  {
                    "type": "filler"
                  }
                ],
                "flex": 1
              }
            ],
            "width": "12px"
          },
          {
            "type": "text",
            "text": "กำลังดำเนินการ",
            "gravity": "center",
            "flex": 4,
            "size": "xs",
            "color": "#8c8c8c"
          }
        ],
        "spacing": "lg",
        "height": "64px"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "ขั้นที่ 1",
            "gravity": "center",
            "size": "sm"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "cornerRadius": "30px",
                "width": "12px",
                "height": "12px",
                "borderColor": "#6486E3",
                "borderWidth": "2px"
              },
              {
                "type": "filler"
              }
            ],
            "flex": 0
          },
          {
            "type": "text",
            "text": "โรคและวิธีการรักษา",
            "gravity": "center",
            "flex": 4,
            "size": "sm"
          }
        ],
        "spacing": "lg",
        "cornerRadius": "30px"
      }
    ]
  }
}
)

underment_message = FlexSendMessage(
    alt_text='hello',
      contents={
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "⚠️ ระบบติดตามผลกำลังพัฒนา ⚠️",
        "weight": "bold",
        "size": "md"
      },
      {
        "type": "box",
        "layout": "vertical",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "Sorry, This menu is under development",
                "color": "#666666",
                "size": "md",
                "flex": 5
              }
            ]
          }
        ]
      }
    ]
  }
}
)

choose_message = FlexSendMessage(
    alt_text='hello',
      contents={
  "type": "carousel",
  "contents": [
    {
      "type": "bubble",
      "size": "micro",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "ขั้นตอนที่ 1",
            "color": "#ffffff",
            "align": "start",
            "size": "md",
            "gravity": "center"
          },
          {
            "type": "text",
            "text": "โรคและวิธีรักษา",
            "color": "#ffffff",
            "align": "start",
            "size": "xs",
            "gravity": "center",
            "margin": "lg"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "filler"
                  }
                ],
                "width": "40%",
                "backgroundColor": "#0D8186",
                "height": "6px"
              }
            ],
            "backgroundColor": "#9FD8E36E",
            "height": "6px",
            "margin": "sm"
          }
        ],
        "backgroundColor": "#27ACB2",
        "paddingTop": "19px",
        "paddingAll": "12px",
        "paddingBottom": "16px"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "เริ่มต้น",
                  "text": "คุยกับน้องเรียน"
                }
              }
            ],
            "flex": 1
          }
        ],
        "spacing": "md",
        "paddingAll": "12px"
      }
    },
    {
      "type": "bubble",
      "size": "micro",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "ขั้นตอนที่ 2",
            "color": "#ffffff",
            "align": "start",
            "size": "md",
            "gravity": "center"
          },
          {
            "type": "text",
            "text": "คำแนะนำเพิ่มเติม",
            "color": "#ffffff",
            "align": "start",
            "size": "xs",
            "gravity": "center",
            "margin": "lg"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "filler"
                  }
                ],
                "width": "70%",
                "backgroundColor": "#DE5658",
                "height": "6px"
              }
            ],
            "backgroundColor": "#FAD2A76E",
            "height": "6px",
            "margin": "sm"
          }
        ],
        "backgroundColor": "#FF6B6E",
        "paddingTop": "19px",
        "paddingAll": "12px",
        "paddingBottom": "16px"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "เริ่มต้น",
                  "text": "คำปรึกษาเพิ่มเติม"
                }
              }
            ],
            "flex": 1
          }
        ],
        "spacing": "md",
        "paddingAll": "12px"
      }
    },
    {
      "type": "bubble",
      "size": "micro",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "ขั้นตอนที่ 3",
            "color": "#ffffff",
            "align": "start",
            "size": "md",
            "gravity": "center"
          },
          {
            "type": "text",
            "text": "เสร็จสิ้นกระบวนการ",
            "color": "#ffffff",
            "align": "start",
            "size": "xs",
            "gravity": "center",
            "margin": "lg"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "filler"
                  }
                ],
                "width": "100%",
                "backgroundColor": "#7D51E4",
                "height": "6px"
              }
            ],
            "backgroundColor": "#9FD8E36E",
            "height": "6px",
            "margin": "sm"
          }
        ],
        "backgroundColor": "#A17DF5",
        "paddingTop": "19px",
        "paddingAll": "12px",
        "paddingBottom": "16px"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "เริ่มต้น",
                  "text": "อัปโหลดข้อมูล"
                }
              }
            ],
            "flex": 1
          }
        ],
        "spacing": "md",
        "paddingAll": "12px"
      }
    }
  ]
}
)

database_ex = FlexSendMessage(
    alt_text='hello',
      contents={
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "🌟 ประเมินความพึงพอใจ",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "box",
        "layout": "vertical",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "สามารถเลือกลำดับคะแนนหรือพิมพ์ข้อเสนอแนะได้เลยโดยเลือกได้อย่างใดอย่างหนึ่ง",
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "xs",
    "contents": [
      {
        "type": "button",
        "style": "primary",
        "height": "sm",
        "action": {
          "type": "message",
          "label": " ⭐",
          "text": "พอใช้"
        }
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "margin": "sm"
      },
      {
        "type": "button",
        "action": {
          "type": "message",
          "label": " ⭐ ⭐",
          "text": "ดี"
        },
        "style": "primary",
        "height": "sm"
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": " ⭐ ⭐ ⭐",
              "text": "ดีเยี่ยม"
            },
            "style": "primary",
            "height": "sm"
          }
        ],
        "margin": "sm"
      }
    ],
    "flex": 0,
    "offsetStart": "none",
    "margin": "none",
    "paddingAll": "15px",
    "paddingBottom": "xxl",
    "paddingTop": "none"
  }
}
)
#-----------------------------

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if text == 'ติดตามการรักษาโรค':
        line_bot_api.reply_message(
            event.reply_token, [follow_message,choose_message])
    elif (text == 'ประเมินความพึงพอใจ'):
        line_bot_api.reply_message(
            event.reply_token, [database_ex])

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title='Location', address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    os.rename(tempfile_path, dist_path)

    im_file = open(dist_path, "rb")
    im = cv2.imread(im_file)
    im0 = im.copy()

    results = model(im, size=640)  # reduce size=320 for faster inference
    print(results)
    annotator = Annotator(im0, line_width=line_thickness)
    # Write results 
    df = results.pandas().xyxy[0]
    for idx, r in df.iterrows():
          #if r.confidence >= 0.3 :
            c = int(r['class'])  # integer class
            name = r['name']
            label = f'{name} {r.confidence:.2f}'
            annotator.box_label((r.xmin, r.ymin, r.xmax, r.ymax), label, color=colors(c, True))

    save_path = str(save_dir + os.path.basename(tempfile_path) + '_result.' + ext) 
    cv2.imwrite(save_path, im0)

    url = request.url_root + '/' + save_path
    z = df.drop(labels=['xmin', 'xmax', 'ymin', 'ymax', 'class'],axis=1)
    g = z.sort_values(by=['confidence'], ascending = False)
    namelistedit = g[g['name'].duplicated()==0]
    renamelist = namelistedit.rename(columns={'confidence': 'ความแม่นยำ', 'name': 'ชื่อโรค'})
    namefirst = ["powder","n_loss","mg_loss","blight","spot"]
    namesec = ["ราแป้ง","ขาดธาตุ N","ขาดธาตุ Mg","ใบไหม้","ใบจุด"]
    renamelist01 = renamelist

    renamelist['ชื่อโรค'] = renamelist['ชื่อโรค'].replace(['powder', 'Blight', 'spot', 'n_loss'],["โรคราแป้ง","โรคใบไหม้","โรคใบจุด","ขาดธาตุ N"])
    for a in range(len(renamelist)):
        numes = renamelist.iloc[a,0]
        numse = round((numes)*100,2)
        renamelist = renamelist.replace(numes,f'{numse}%')
        
    renamelist.index = renamelist.index + 1
    

    if df.empty:
        nodata_flex_message = FlexSendMessage(
          alt_text='hello',
      contents={
    "type": "bubble",
    "body": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        {
          "type": "text",
          "text": "สรุปผลการวิเคราะห์",
          "weight": "bold",
          "size": "xl"
        },
        {
          "type": "box",
          "layout": "vertical",
          "margin": "lg",
          "spacing": "sm",
          "contents": [
            {
              "type": "box",
              "layout": "baseline",
              "spacing": "sm",
              "contents": [
                {
                  "type": "text",
                  "text": "ผล : ",
                  "color": "#aaaaaa",
                  "size": "sm",
                  "flex": 1
                },
                {
                  "type": "text",
                  "text": "ไม่พบโรคหรือระบุผลไม่ได้",
                  "color": "#666666",
                  "size": "sm",
                  "flex": 5
                }
              ]
            },
            {
              "type": "box",
              "layout": "baseline",
              "spacing": "sm",
              "contents": [
                {
                  "type": "text",
                  "text": "Acc.",
                  "color": "#aaaaaa",
                  "size": "sm",
                  "flex": 1
                },
                {
                  "type": "text",
                  "text": "Err.",
                  "color": "#666666",
                  "size": "sm",
                  "flex": 5
                }
              ]
            }
          ]
        }
      ]
    }
  }
)
        line_bot_api.reply_message(
            event.reply_token, [
                ImageSendMessage(url,url),
                nodata_flex_message,
          ])
    else :
        data_flex_message = FlexSendMessage(
    alt_text='hello',
    contents={
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "สรุปผลการวิเคราะห์",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "box",
        "layout": "vertical",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "ผล : ",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 1
              },
              {
                "type": "text",
                "text": f"{renamelist.iloc[0,1]}",
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "Acc.",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 1
              },
              {
                "type": "text",
                #"text": f"ความแม่นยำ {numse}%",
                "text": f"ความแม่นยำ {renamelist.iloc[0,0]}",
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "style": "link",
        "height": "sm",
        "action": {
          "type": "message",
          "label": "ต้องการติดตามการรักษา",
          "text": "ติดตามการรักษาโรค"
        }
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "margin": "sm"
      }
    ],
    "flex": 0
  }
}
)

        line_bot_api.reply_message(
            event.reply_token, [
                ImageSendMessage(url,url),
                data_flex_message,
            ])
      

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

# create tmp dir for download content
make_static_tmp_dir()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

