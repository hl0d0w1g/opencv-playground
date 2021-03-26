import cv2
import numpy as np
import time
import datetime
import os
import pickle
import base64  # for base64.urlsafe_b64decode
import googleapiclient.errors as errors
from googleapiclient.discovery import build
# MIME parts for constructing a message
from email.mime.audio       import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base        import MIMEBase
from email.mime.image       import MIMEImage
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText
import mimetypes  # for mimetypes.guesstype


ALARM_TIMEOUT_MIN = 10  # Minutes
VIDEO_LENGHT = 50 # N frames


def create_message_with_attachment(sender, to, subject, message_text, file):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEMultipart()
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  msg = MIMEText(message_text)
  message.attach(msg)

  content_type, encoding = mimetypes.guess_type(file)

  if content_type is None or encoding is not None:
    content_type = 'application/octet-stream'
  main_type, sub_type = content_type.split('/', 1)
  if main_type == 'text':
    fp = open(file, 'rb')
    msg = MIMEText(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'image':
    fp = open(file, 'rb')
    msg = MIMEImage(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'audio':
    fp = open(file, 'rb')
    msg = MIMEAudio(fp.read(), _subtype=sub_type)
    fp.close()
  else:
    fp = open(file, 'rb')
    msg = MIMEBase(main_type, sub_type)
    msg.set_payload(fp.read())
    fp.close()
  filename = os.path.basename(file)
  msg.add_header('Content-Disposition', 'attachment', filename=filename)
  message.attach(msg)

  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

service = build('gmail', 'v1', credentials=creds)

alarm_activated = True
last_alarm_time = None
motion = False
video_recording = False
frames_in_video = 0

cap = cv2.VideoCapture(0)

FRAME_WIDTH = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))

while (cap.isOpened()):
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = [contour for contour in contours if cv2.contourArea(contour) > 900]
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if alarm_activated:
            
            alarm_time = time.time()
            if last_alarm_time is None:
                motion = True
                last_alarm_time = alarm_time
            elif ((alarm_time - last_alarm_time) / 60) > ALARM_TIMEOUT_MIN:
                motion = True
                last_alarm_time = alarm_time


    image = frame1.copy()
    cv2.imshow("feed", frame1)

    if motion:
        if not video_recording:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            ffourcc = cv2.VideoWriter_fourcc('X','V','I','D')
            video_filename = 'recording ' + st + '.avi'
            out = cv2.VideoWriter(video_filename, ffourcc, 10.0, (FRAME_WIDTH, FRAME_HEIGHT))
            video_recording = True

            out.write(image)
            frames_in_video += 1

        elif (frames_in_video > VIDEO_LENGHT):
            message = create_message_with_attachment('from@gmail.com', 'to@gmail.com', 'Movement detection', 'Test', video_filename)
            send_message(service, 'me', message)

            frames_in_video = 0
            motion = False
            video_recording = False

        else:
          out.write(image)
          frames_in_video += 1

    frame1 = frame2
    ret, frame2 = cap.read()


    if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

cv2.destroyAllWindows()
cap.release()