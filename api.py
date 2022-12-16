
# 메세지 형식 예시
#{'id': '18456bf888fd397a', 'threadId': '18456bf5a94df61e', 'labelIds': ['SENT', 'INBOX'], 'snippet': 'ayo this is a spam', 'payload': {'partId': '', 'mimeType': 'multipart/alternative', 'filename': '', 'headers': [{'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Date', 'value': 'Tue, 8 Nov 2022 19:18:22 +0900'}, {'name': 'Message-ID', 'value': '<CAKKYdfnrBtNsnKC_3Ws5PLJce0ZCt1irYQPE-de9Jptp4YPGnA@mail.gmail.com>'}, {'name': 'Subject', 'value': 'Test'}, {'name': 'From', 'value': '"조찬희" <chanheecho426@gmail.com>'}, {'name': 'To', 'value': 'fireslayer426@gmail.com'}, {'name': 'Content-Type', 'value': 'multipart/alternative; boundary="0000000000002e4f6205ecf2dc2a"'}], 'body': {'size': 0}, 'parts': [{'partId': '0', 'mimeType': 'text/plain', 'filename': '', 'headers': [{'name': 'Content-Type', 'value': 'text/plain; charset="UTF-8"'}], 'body': {'size': 20, 'data': 'YXlvIHRoaXMgaXMgYSBzcGFtDQo='}}, {'partId': '1', 'mimeType': 'text/html', 'filename': '', 'headers': [{'name': 'Content-Type', 'value': 'text/html; charset="UTF-8"'}], 'body': {'size': 41, 'data': 'PGRpdiBkaXI9Imx0ciI-YXlvIHRoaXMgaXMgYSBzcGFtPC9kaXY-DQo='}}]}, 'sizeEstimate': 571, 'historyId': '675619', 'internalDate': '1667902702000'}

#메세지 id 예시
#[{'id': '1851842d187e67a6', 'threadId': '1851842ba20e1bce'}]

from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 편의변수
SCOPES = ['https://mail.google.com/']
CLIENT_SECRETS_FILE = "credentials.json"


# 일반변수
message_counter = 1
ask_delete = True




# API 가져오기(구글에서 제공하는 퀵스타트)
def get_service():
    creds = None
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            # 예 여기는 이미 했어요(같은 파일 내에 token.json 파일이 생성되었음!)

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
    except HttpError as error:
        # TODO (developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    return service



# 이메일 파일 id 추출
def get_list(service, user_id, search_string):
    try:
        message_list = service.users().messages().list(
            userId=user_id, q=search_string).execute()
        return message_list
    except HttpError as error:
        print(f"얘 에러란다!{error}")



# 메세지 삭제
def trash_messages(service, user_id, message_id):
    service.users().messages().trash(userId=user_id, id=message_id).execute()




# 메세지 정보 얻어오기
def get_message(service, user_id, message_id):
    message_payload = service.users().messages().get(
        userId=user_id, id=message_id, format='full').execute()
    return message_payload


service = get_service()

#메세지 있는지 없는지 판단
try:
    brought_messages = get_list(service, "me", "label:unread")["messages"]  # 읽은 메세지 리스트
    
except:
    input("새로운 메세지가 없습니다.")
    quit()

# 메세지 리스트가 있는 json 파일에서 각각의 메세지 id 추출
for message in brought_messages:
    # id 추출한 것 가지고 메세지 json 정의
    msg = get_message(service, "me", message['id'])
    # json에서 페이로드 추출
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    print(f"\n{message_counter}.")
    for header in headers:  # 메세지 정보 출력
        value = header.get("value")
        name = header.get("name")
        if name.lower() == 'from':
            print("보낸 사람:", value)
        if name.lower() == "subject":
            print("제목:", value)
        if name.lower() == "date":
            print("보낸 날짜:", value)
    message_counter += 1

# 삭제할 메세지 묻기
# - TODO 인풋값이 메세지개수 벗어나나 판별
while ask_delete:

    delete_message = input("https://www.google.com/gmail/\n삭제할 메세지의 번호를 쓰시오(복수 선택시 콤마 넣으세요,없으면 적지 마세요)\n:")
    delete_message_number = sorted(delete_message.split(","))

    # 삭제메세지 없음 조건
    if not (len(delete_message_number) == 1 and delete_message_number[0] == ""):
        try:  # 메세지 번호 형식에 맞춰 적은것이 맞냐 확인중
            for number in delete_message_number:
                int(number)
        except:
            print("숫자를 적어달라니까요?")
            continue
    if len(delete_message_number) == 1 and delete_message_number[0] == "":
        print("안지울거 맞나요?(y/n)")  # 재차 확인(메세지 삭제 안함)
    else:
        delete_message_number = list(set(delete_message_number))  # 메세지 겹침 제거 , 정렬
        delete_message_number = list(map(int, delete_message_number))  # 메세지 형태 변환
        delete_message_number.sort()
        print(f"{delete_message_number}번을 지우실거 맞나요?(y/n)")  # 재차 확인(메세지 삭제)
    delete_check = input(":")
    if delete_check == "y":
        ask_delete = False
    else:
        continue

message_counter = 1  # 메세지 세는 변수(재활용)

for message in brought_messages:  # 메세지 삭제
    for number in delete_message_number:
        if message_counter == number:
            trash_messages(service, 'me', message['id'])