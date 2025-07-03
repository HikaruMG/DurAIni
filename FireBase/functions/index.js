const functions = require("firebase-functions");
const region = "asia-southeast1";
const request = require("request-promise");


const LINE_CHANNEL_SECRET = process.env.LINE_CHANNEL_SECRET;
const LINE_MESSAGING_API = process.env.LINE_MESSAGING_API;
const LINE_ACCESS_TOKEN = process.env.LINE_ACCESS_TOKEN;


const LINE_HEADER = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${LINE_ACCESS_TOKEN}`
  };

  //Firebase-Cloud
  // สำหรับการเข้าถึง Cloud Storage
const admin = require('firebase-admin')
admin.initializeApp()
  
  // สำหรับสร้าง public url ใน Cloud Storage
const UUID = require('uuid-v4')
  
  // สำหรับจัดการไฟล์
const path = require('path')
const os = require('os')
const fs = require('fs');

exports.DurainniXTest = functions.region(region).https.onRequest(async (req, res) => {
  if (req.method === "POST") {
    let event = req.body.events[0]
    if (event.type === "message" && event.message.type === "text" && event.message.text !== "ติดตามการรักษาโรค" && event.message.text !== "อัปโหลดรูปภาพ" && event.message.text !== "ประเมินความพึงพอใจ" ) {
      postToDialogflow(req);
      console.log('DialogflowNotYolo')

    } else if (event.type === "message" && event.message.type === "text" && event.message.text === "ติดตามการรักษาโรค" && event.message.text !== "ประเมินความพึงพอใจ") {
      postToYolo(req);
      console.log('YoloFollow')
    
    }  else if (event.type === "message" && event.message.type === "text"  && event.message.text === "ประเมินความพึงพอใจ" && event.message.text !== "ติดตามการรักษาโรค") {
      await postToYolo(req);
      console.log('YoloFollow')
    
    } else if (event.type === "message" && event.message.type === "image") {
      // await upload(event) //ใช้เมื่อ Deploy Firebase แล้วเท่านั้น
      await postToYolo(req);
      console.log('Yolo')
    }  
    else {
      reply(req);
      console.log('Reply')
    }
  }
  return res.status(200).send(req.method);
});

const postToDialogflow = req => {
  return request.post({
    uri: process.env.DIALOGFLOW_KEY, 

    body: JSON.stringify(req.body)
  });
};

const reply = req => {
  return request.post({
    uri: `${LINE_MESSAGING_API}/message/reply`,
    headers: LINE_HEADER,
    body: JSON.stringify({
      replyToken: req.body.events[0].replyToken,
      messages: [
        {
          type: "text",
          text: "กรุณาใส่เฉพาะรูปภาพและตัวอักษร"
          
        }
      ]
    })
  });
};

const postToYolo = req => {
    return request.post({
        headers: {
            
        "x-line-signature": req.headers["x-line-signature"],
        "content-type": "application/json;charset=UTF-8"

        },
        uri: process.env.CLOUDPROCESS_API,
        body: JSON.stringify(req.body)
    });
  };

const upload = async (event) => {
  // ดาวน์โหลด binary จาก LINE 
  const LINE_CONTENT_API = 'https://api-data.line.me/v2/bot/message'
  let url = `${LINE_CONTENT_API}/${event.message.id}/content`
  let buffer = await request.get({
    headers: LINE_HEADER,
    uri: url,
    encoding: null // กำหนดเป็น null เพื่อให้ได้ binary ที่สมบูรณ์
  })

  // สร้างไฟล์ temp ใน local โดยใช้ timestamp ที่ได้จาก webhook เป็นชื่อไฟล์
  let filename = `${event.timestamp}.jpg`
  let tempLocalFile = path.join(os.tmpdir(), filename)
  await fs.writeFileSync(tempLocalFile, buffer)

  // generate ตัว uuid
  let uuid = UUID()
  
  // อัพโหลดไฟล์ขึ้น Cloud Storage
  let bucket = admin.storage().bucket()
  let file = await bucket.upload(tempLocalFile, {
    // กำหนด path ในการเก็บไฟล์แยกเป็นแต่ละ userId
    destination: `photos/${event.source.userId}/${filename}`,
    metadata: {
      cacheControl: 'no-cache',
      metadata: {
        firebaseStorageDownloadTokens: uuid
      }
    }
  })
  
  // ลบไฟล์ temp เมื่ออัพโหลดเรียบร้อย
  fs.unlinkSync(tempLocalFile)

  // วิธีลัดในการสร้าง download url ขึ้นมา
  let prefix = `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o`
  let suffix = `alt=media&token=${uuid}`
  return `${prefix}/${encodeURIComponent(file[0].name)}?${suffix}`
}