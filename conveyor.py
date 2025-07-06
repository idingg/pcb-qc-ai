import glob
import os
import json
import spb.sdk
import requests
from requests.auth import HTTPBasicAuth
import cv2
from io import BytesIO
import time

import predict
import eval

team_name = "kdt2024_1-22"
access_key = "IPZnSkpxSn2wUcsmyeYz6tQUFEhriBV6H8PsYB0j"
project_name = "E^^2"
dataset_name = "E-2_241107"

# API endpoint
api_url = "https://suite-endpoint-api-apne2.superb-ai.com/endpoints/2acab353-c6d6-4b6c-8d05-fda4113d8f1b/inference"  # L
# api_url = "https://suite-endpoint-api-apne2.superb-ai.com/endpoints/d0a4be54-17a4-4de9-badf-61451c2d96c3/inference"  # N
# 가상의 비전 AI API URL (예: 객체 탐지 API)
# VISION_API_URL = "https://suite-endpoint-api-apne2.superb-ai.com/endpoints/6f14581c-a991-4fee-b4d3-3372cc907ae0/inference"
TEAM = "kdt2024_1-22"
ACCESS_KEY = "IPZnSkpxSn2wUcsmyeYz6tQUFEhriBV6H8PsYB0j"

labels_base_dir = "E^^2 2024-11-10 194626"
meta_dir = os.path.join(labels_base_dir, "meta", dataset_name)

image_dir = "result24"

file_name_id = {}
for i in glob.glob(os.path.join(meta_dir, "*.json")):
    with open(i, "r") as f:
        file_data = json.load(f)
        file_name_id[file_data["data_key"]] = file_data["label_id"]

# image_ids = [
#     os.path.basename(i[: -(len(".json"))])
#     for i in glob.glob(os.path.join(labels_base_dir, "labels", "*.json"))
# ]


client = spb.sdk.Client(
    team_name=team_name,
    access_key=access_key,
    project_name=project_name,
)


def only_pico_usb(response_json):
    ret = []
    for object in response_json["objects"]:
        if object["class"] == "RASPBERRY PICO" or object["class"] == "USB":
            ret.append(object)
    return ret


def count_class(response_json, name):
    if len(response_json) < 2:
        return 0

    cnt = 0
    for item in response_json:
        if item["class"] == name:
            cnt += 1
    return cnt


def get_class(response_json, name):
    for item in response_json:
        if item["class"] == name:
            return item


cnt_total = 0
cnt_goodpos = 0
cnt_9 = 0
cnt_no_good_pos = 0
max_distance_total = 0
min_score_total = 1.0

print(len(file_name_id))
for file_name, image_id in file_name_id.items():
    cnt_total += 1
    print(f"{cnt_total}/{len(file_name_id)}", file_name, end=" ")
    img = cv2.imread(os.path.join(image_dir, file_name))
    if img is None:
        continue
    _, img_encoded = cv2.imencode(".jpg", img)
    # Prepare the image for sending
    img_bytes = BytesIO(img_encoded.tobytes())

    # image_datahandle = client.get_data(
    #     "0a2d3cec-3551-4399-8321-3fdbb69e03fd"
    # )  # 아이디 넣어야 함

    # 서버에 이미지 보내서 response 받기
    # 받은 dict 로 9개 위치 계산
    # coordinates로 변환

    # cv2.imshow("Image Window", img)
    # if cv2.waitKey(1) & 0xFF == ord("q"):
    #     break

    # image_datahandle.download_image("test_dir")

    # starttime = time.time()
    response = requests.post(
        url=api_url,
        auth=HTTPBasicAuth(TEAM, ACCESS_KEY),
        headers={
            "Content-Type": "image/jpeg",
        },
        data=img_bytes,
    )
    # read image with opencv

    if response.status_code == 200:
        trimed_objects = only_pico_usb(response.json())
        # print(count_class(trimed_objects, "RASPBERRY PICO"))
        # print(count_class(trimed_objects, "USB"))
        objects = response.json()["objects"]
        if (
            count_class(objects, "RASPBERRY PICO") == 1
            and count_class(objects, "USB") == 1
            and count_class(objects, "CHIPSET") == 1
            and count_class(objects, "OSCILLATOR") == 1
            and count_class(objects, "BOOTSEL") == 1
            and count_class(objects, "HOLE") == 4
        ):
            threshold = 0.4
            min_score = 1.0
            object_copy = []
            for object in objects:
                if object["score"] < min_score:
                    min_score = object["score"]
                if min_score < min_score_total:
                    min_score_total = min_score
                if object["score"] >= threshold:
                    object_copy.append(object)
            objects = object_copy
            del object_copy
            print(f"min_score:{min_score:.4}/{min_score_total:.4}", end=" ")

            for object in objects:
                cv2.rectangle(img, object["box"][:2], object["box"][2:], (0, 0, 255), 2)
            cv2.imshow("Image Window", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            cnt_9 += 1
            print("good 9 :", cnt_9, end=" ")

            for object in trimed_objects:
                cv2.rectangle(img, object["box"][:2], object["box"][2:], (255, 0, 0), 2)
            cv2.imshow("Image Window", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            predict_pos = predict.predict_pos(trimed_objects)
            for object in predict_pos:
                cv2.rectangle(img, object["box"][:2], object["box"][2:], (0, 255, 0), 1)
            cv2.imshow("Image Window", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            is_good_pos, max_distance = eval.check_distances(
                objects, predict_pos, 8.1
            )  # 0.1인치
            if is_good_pos == "Success":

                cnt_goodpos += 1
                print("goodpos:", cnt_goodpos, end=" ")
                # print(f"goodpos, max difference:{max_distance:.4} px")
            else:
                # print("no goodpos", max_distance)
                cnt_no_good_pos += 1
                print("no goodpos:", cnt_no_good_pos, end=" ")
            if max_distance > max_distance_total:
                max_distance_total = max_distance
            print(min_score_total, end="\n")
        else:
            print("no 9")
        print(max_distance_total)

        if (
            count_class(trimed_objects, "RASPBERRY PICO") != 1
            or count_class(trimed_objects, "USB") != 1
        ):
            print("no pico or usb")
            continue
        else:
            pico_center = predict.get_box_center(
                get_class(trimed_objects, "RASPBERRY PICO")["box"]
            )
            cv2.rectangle(
                img,
                get_class(trimed_objects, "USB")["box"][:2],
                get_class(trimed_objects, "USB")["box"][2:],
                (0, 0, 255),
                2,
            )

            usb_center = predict.get_box_center(get_class(trimed_objects, "USB")["box"])
            predicted_objects = predict.predict_pos(trimed_objects)
            print(predicted_objects)

            for item in predicted_objects:
                cv2.rectangle(img, item["box"][:2], item["box"][2:], (255, 0, 0), 2)
                cv2.imshow("Image Window", img)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    else:
        print("response error")

cv2.destroyAllWindows()
