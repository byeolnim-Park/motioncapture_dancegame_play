"""
python>>(landmark)>>C#
server: python
client: C#

소켓 통신 속 랜드마크 계산.
str 형태로 전송
딜레이 약 0.01초
"""

import socket, threading
import timeit
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

window_draw = False
video_play = False

# 서버와 클라이언트 연결 후 client로받은 데이터를 echo
def binder(client_socket, addr):
    print("connected by", addr)
    cap = cv2.VideoCapture(0)
    start_time = timeit.default_timer()
    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        while True:
            try:
                """
                data = client_socket.recv(4)  # 4바이트의 크기 정보 데이터 대기, 데이터 수신 확인용
                length = int.from_bytes(data, "big")  # big 엔디언으로 byte to int, C#의 bitconverter 처리 방식은 big엔디언
                data = client_socket.recv(length)  # 나머지 데이터 수신
                msg = data.decode()  # str로 decode
                print("Received from", addr, msg)
                """

                # 랜드마크에 대한 크기 정보 및 내용을 송신
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    return "error"

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.flip(image, 1)
                results = pose.process(image)

                hip_x = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x +
                         results.pose_landmarks.landmark[
                             mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
                hip_y = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y +
                         results.pose_landmarks.landmark[
                             mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
                hip_z = 0.0

                keypoints = []

                for data_point in results.pose_world_landmarks.landmark:
                    keypoints.append({
                        data_point.x,
                        data_point.y,
                        data_point.z
                    })
                keypoints.append([hip_x,
                                  hip_y,
                                  hip_z])

                image.flags.writeable = True

                if (video_play):
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

                    # Flip the image and 3Dpose horizontally for a selfie-view display.
                    cv2.imshow('MediaPipe Pose', image)

                if cv2.waitKey(5) & 0xFF == 27:
                    break

                delay = timeit.default_timer() - start_time
                data = ("[" + str(delay) + "]," + str(keypoints)).encode()  # str to byte
                start_time = timeit.default_timer()
                length = len(data)
                client_socket.sendall(length.to_bytes(4, byteorder='big'))  # 데이터 크기 정보 송신
                client_socket.sendall(data)  # 데이터 내용 송신
            except:
                data = "not found".encode()
                client_socket.sendall(length.to_bytes(4, byteorder='big'))  # 데이터 크기 정보 송신
                client_socket.sendall(data)  # 데이터 내용 송신



server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 생성
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 소켓 레벨 및 데이터 형식 설정
server_socket.bind(('', 9999))  # ip, 포트 설정
server_socket.listen()  # 설정 완료 후 listen
print("wait for client...")

try:  # while을 빼고 예외 발생 시에만 릴리즈 할 수 없나?
    while True:  # 이 경우 여러개의 클라이언트를 상대 가능
        client_socket, addr = server_socket.accept()  # 클라이언트 요청이 온 경우 accept 및 정보 받기
        th = threading.Thread(target=binder, args=(client_socket, addr))  # 쓰레드를 이용하여 여러 클라이언트를 받기
        th.start();
except:
    print("server")
finally:
    cap.release()
    client_socket.close()
    server_socket.close()
    exit(0)

# """
# python>>(landmark)>>C#
# server: python
# client: C#
#
# 소켓 통신 속 랜드마크 계산.
# str 형태로 전송
# 딜레이 약 0.01초
# """
#
# import socket, threading
# import timeit
# import cv2
# import mediapipe as mp
#
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles
# mp_pose = mp.solutions.pose
#
# window_draw = False
# video_play = False
#
# # 서버와 클라이언트 연결 후 client로받은 데이터를 echo
# def binder(client_socket, addr):
#     print("connected by", addr)
#     cap = cv2.VideoCapture(0)
#     start_time = timeit.default_timer()
#     try:
#         with mp_pose.Pose(
#                 min_detection_confidence=0.5,
#                 min_tracking_confidence=0.5) as pose:
#             while True:
#
#                 """
#                 data = client_socket.recv(4)  # 4바이트의 크기 정보 데이터 대기, 데이터 수신 확인용
#                 length = int.from_bytes(data, "big")  # big 엔디언으로 byte to int, C#의 bitconverter 처리 방식은 big엔디언
#                 data = client_socket.recv(length)  # 나머지 데이터 수신
#                 msg = data.decode()  # str로 decode
#                 print("Received from", addr, msg)
#                 """
#
#                 # 랜드마크에 대한 크기 정보 및 내용을 송신
#                 success, image = cap.read()
#                 if not success:
#                     print("Ignoring empty camera frame.")
#                     # If loading a video, use 'break' instead of 'continue'.
#                     return "error"
#
#                 # To improve performance, optionally mark the image as not writeable to
#                 # pass by reference.
#                 image.flags.writeable = False
#                 image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#                 image = cv2.flip(image, 1)
#                 results = pose.process(image)
#                 print(results)
#
#                 hip_x = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x +
#                          results.pose_landmarks.landmark[
#                              mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
#                 hip_y = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y +
#                          results.pose_landmarks.landmark[
#                              mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
#                 hip_z = 0.0
#
#                 keypoints = []
#
#                 for data_point in results.pose_world_landmarks.landmark:
#                     keypoints.append({
#                         data_point.x,
#                         data_point.y,
#                         data_point.z
#                     })
#                 keypoints.append([hip_x,
#                                   hip_y,
#                                   hip_z])
#
#                 image.flags.writeable = True
#
#                 if (video_play):
#                     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#                     mp_drawing.draw_landmarks(
#                         image,
#                         results.pose_landmarks,
#                         mp_pose.POSE_CONNECTIONS,
#                         landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#
#                     # Flip the image and 3Dpose horizontally for a selfie-view display.
#                     cv2.imshow('MediaPipe Pose', image)
#
#                 if cv2.waitKey(5) & 0xFF == 27:
#                     break
#
#                 delay = timeit.default_timer() - start_time
#                 data = ("[" + str(delay) + "]," + str(keypoints)).encode()  # str to byte
#                 start_time = timeit.default_timer()
#                 length = len(data)
#                 client_socket.sendall(length.to_bytes(4, byteorder='big'))  # 데이터 크기 정보 송신
#                 client_socket.sendall(data)  # 데이터 내용 송신
#     except:
#         print("Except : ", addr)  # 접속 중단
#         cap.release()
#         client_socket.close()  # 접속 중단 시 close
#         exit(0)
#     finally:
#         client_socket.close()  # 접속 중단 시 close
#         cap.release()
#         exit(0)
#
#
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 생성
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 소켓 레벨 및 데이터 형식 설정
# server_socket.bind(('', 9999))  # ip, 포트 설정
# server_socket.listen()  # 설정 완료 후 listen
# print("wait for client...")
#
# try:  # while을 빼고 예외 발생 시에만 릴리즈 할 수 없나?
#     while True:  # 이 경우 여러개의 클라이언트를 상대 가능
#         client_socket, addr = server_socket.accept()  # 클라이언트 요청이 온 경우 accept 및 정보 받기
#         th = threading.Thread(target=binder, args=(client_socket, addr))  # 쓰레드를 이용하여 여러 클라이언트를 받기
#         th.start();
# except:
#     print("server")
# finally:
#     cap.release()
#     server_socket.close()
#     exit(0)



