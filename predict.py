import math
import cv2
import numpy as np
import time


def get_box_center(box):
    x1, y1, x2, y2 = box
    return {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2}


def get_distance(p1, p2):
    return math.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["y"] - p2["y"]) ** 2)


def predict_pos(input_data):
    def get_p1(usb_center, pico_center):
        ratio = 0.97
        # ratio = 1.0
        p1_x = pico_center["x"] + (pico_center["x"] - usb_center["x"]) * ratio
        p1_y = pico_center["y"] + (pico_center["y"] - usb_center["y"]) * ratio
        return {"x": p1_x, "y": p1_y}

    def get_p2(usb_center, pico_center):
        ratio = 0.4
        p2_x = pico_center["x"] + (pico_center["x"] - usb_center["x"]) * ratio
        p2_y = pico_center["y"] + (pico_center["y"] - usb_center["y"]) * ratio
        return {"x": p2_x, "y": p2_y}

    def get_p3(usb_center, pico_center):
        ratio = 0.55
        p3_x = pico_center["x"] - (pico_center["x"] - usb_center["x"]) * ratio
        p3_y = pico_center["y"] - (pico_center["y"] - usb_center["y"]) * ratio
        return {"x": p3_x, "y": p3_y}

    def get_p4(usb_center, pico_center):
        ratio = 0.95
        p4_x = pico_center["x"] - (pico_center["x"] - usb_center["x"]) * ratio
        p4_y = pico_center["y"] - (pico_center["y"] - usb_center["y"]) * ratio
        return {"x": p4_x, "y": p4_y}

    def get_hole_lu(usb_center, pico_center):
        ratio = 0.25
        p1 = get_p1(usb_center, pico_center)

        hole_x = int(p1["x"] + (pico_center["y"] - usb_center["y"]) * ratio)
        hole_y = int(p1["y"] - (pico_center["x"] - usb_center["x"]) * ratio)
        return {"x": hole_x, "y": hole_y}

    def get_hole_ru(usb_center, pico_center):
        ratio = 0.25
        p1 = get_p1(usb_center, pico_center)

        # print((pico_center["y"] - usb_center["y"]), (pico_center["x"] - usb_center["x"]))
        hole_x = int(p1["x"] - (pico_center["y"] - usb_center["y"]) * ratio)
        hole_y = int(p1["y"] + (pico_center["x"] - usb_center["x"]) * ratio)
        return {"x": hole_x, "y": hole_y}

    def get_hole_ld(usb_center, pico_center):
        ratio = 0.25
        p4 = get_p4(usb_center, pico_center)

        hole_x = int(p4["x"] + (pico_center["y"] - usb_center["y"]) * ratio)
        hole_y = int(p4["y"] - (pico_center["x"] - usb_center["x"]) * ratio)
        return {"x": hole_x, "y": hole_y}

    def get_hole_rd(usb_center, pico_center):
        ratio = 0.25
        p4 = get_p4(usb_center, pico_center)

        # print((pico_center["y"] - usb_center["y"]), (pico_center["x"] - usb_center["x"]))
        hole_x = int(p4["x"] - (pico_center["y"] - usb_center["y"]) * ratio)
        hole_y = int(p4["y"] + (pico_center["x"] - usb_center["x"]) * ratio)
        return {"x": hole_x, "y": hole_y}

    def get_holes_center(centers):
        usb_center = centers["USB"]
        pico_center = centers["RASPBERRY PICO"]

        ret = []
        ret.append(get_hole_lu(usb_center, pico_center))
        ret.append(get_hole_ru(usb_center, pico_center))
        ret.append(get_hole_ld(usb_center, pico_center))
        ret.append(get_hole_rd(usb_center, pico_center))
        return ret

    def get_oscillator_center(centers):
        usb_center = centers["USB"]
        pico_center = centers["RASPBERRY PICO"]

        ratio = 0.07
        p2 = get_p2(usb_center, pico_center)

        oscil_x = int(p2["x"] - (pico_center["y"] - usb_center["y"]) * ratio)
        oscil_y = int(p2["y"] + (pico_center["x"] - usb_center["x"]) * ratio)
        return {"x": oscil_x, "y": oscil_y}

    def get_bootsel_center(centers):
        usb_center = centers["USB"]
        pico_center = centers["RASPBERRY PICO"]

        ratio = 0.15
        p3 = get_p3(usb_center, pico_center)

        hole_x = int(p3["x"] - (pico_center["y"] - usb_center["y"]) * ratio)
        hole_y = int(p3["y"] + (pico_center["x"] - usb_center["x"]) * ratio)
        return {"x": hole_x, "y": hole_y}

    def get_chip_center(centers):
        usb_center = centers["USB"]
        pico_center = centers["RASPBERRY PICO"]

        # ratio = 0.99
        ratio = 0.04
        p1_x = int(pico_center["x"] + (pico_center["x"] - usb_center["x"]) * ratio)
        p1_y = int(pico_center["y"] + (pico_center["y"] - usb_center["y"]) * ratio)
        return {"x": p1_x, "y": p1_y}

    def calculate_angle(a, b):
        # 빗변 계산
        c = math.sqrt(a**2 + b**2)

        # 코사인 값 계산 (밑변과 빗변 사이의 각도를 구하기 위해 코사인 사용)
        cos_theta = b / c

        # 역코사인을 이용하여 각도 계산 (단위: 라디안)
        theta_rad = math.acos(cos_theta)

        # 라디안을 도로 변환
        theta_deg = math.degrees(theta_rad)

        return theta_deg

    def get_chip_bbox(center):
        size = 25
        points = [
            {"x": -size / 2, "y": -size / 2},
            {"x": +size / 2, "y": -size / 2},
            {"x": -size / 2, "y": +size / 2},
            {"x": +size / 2, "y": +size / 2},
        ]

        triangle_width = abs(centers["RASPBERRY PICO"]["x"] - centers["USB"]["x"])
        triangle_height = abs(centers["RASPBERRY PICO"]["y"] - centers["USB"]["y"])
        theta = calculate_angle(triangle_height, triangle_width)

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        ret = {
            "class": "CHIPSET",
            "box": [center["x"], center["y"], center["x"], center["y"]],
        }
        for point in points:
            x = int(point["x"] * cos_theta - point["y"] * sin_theta)
            y = int(point["x"] * sin_theta + point["y"] * cos_theta)
            x += center["x"]
            y += center["y"]
            if x < ret["box"][0]:
                ret["box"][0] = x
            if y < ret["box"][1]:
                ret["box"][1] = y
            if x > ret["box"][2]:
                ret["box"][2] = x
            if y > ret["box"][3]:
                ret["box"][3] = y
        # print(points)
        # print(ret)
        return ret

    def get_bootsel_bbox(center):
        size_width = 18
        size_height = 13
        points = [
            {"x": -size_width / 2, "y": -size_height / 2},
            {"x": +size_width / 2, "y": -size_height / 2},
            {"x": -size_width / 2, "y": +size_height / 2},
            {"x": +size_width / 2, "y": +size_height / 2},
        ]

        triangle_width = abs(centers["RASPBERRY PICO"]["x"] - centers["USB"]["x"])
        triangle_height = abs(centers["RASPBERRY PICO"]["y"] - centers["USB"]["y"])
        theta = calculate_angle(triangle_height, triangle_width)

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        ret = {
            "class": "BOOTSEL",
            "box": [center["x"], center["y"], center["x"], center["y"]],
        }
        for point in points:
            x = int(point["x"] * cos_theta - point["y"] * sin_theta)
            y = int(point["x"] * sin_theta + point["y"] * cos_theta)
            x += center["x"]
            y += center["y"]
            if x < ret["box"][0]:
                ret["box"][0] = x
            if y < ret["box"][1]:
                ret["box"][1] = y
            if x > ret["box"][2]:
                ret["box"][2] = x
            if y > ret["box"][3]:
                ret["box"][3] = y
        # print(points)
        # print(ret)
        return ret

    def get_oscillator_bbox(center):
        size_width = 15
        size_height = 15
        points = [
            {"x": -size_width / 2, "y": -size_height / 2},
            {"x": +size_width / 2, "y": -size_height / 2},
            {"x": -size_width / 2, "y": +size_height / 2},
            {"x": +size_width / 2, "y": +size_height / 2},
        ]

        triangle_width = abs(centers["RASPBERRY PICO"]["x"] - centers["USB"]["x"])
        triangle_height = abs(centers["RASPBERRY PICO"]["y"] - centers["USB"]["y"])
        theta = calculate_angle(triangle_height, triangle_width)

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        ret = {
            "class": "OSCILLATOR",
            "box": [center["x"], center["y"], center["x"], center["y"]],
        }
        for point in points:
            x = int(point["x"] * cos_theta - point["y"] * sin_theta)
            y = int(point["x"] * sin_theta + point["y"] * cos_theta)
            x += center["x"]
            y += center["y"]
            if x < ret["box"][0]:
                ret["box"][0] = x
            if y < ret["box"][1]:
                ret["box"][1] = y
            if x > ret["box"][2]:
                ret["box"][2] = x
            if y > ret["box"][3]:
                ret["box"][3] = y
        # print(points)
        # print(ret)
        return ret

    def get_holes_bbox(hole_centers):
        def get_hole_bbox(p):
            hole_r = 5
            return [p["x"] - hole_r, p["y"] - hole_r, p["x"] + hole_r, p["y"] + hole_r]

        ret = []
        for hole in hole_centers:
            ret.append({"class": "HOLE", "box": get_hole_bbox(hole)})
        return ret

    ret = input_data.copy()

    centers = {}
    for box in input_data:
        centers[box["class"]] = get_box_center(box["box"])

    p_oscillator = get_oscillator_center(centers)
    p_bootsel = get_bootsel_center(centers)
    p_chip = get_chip_center(centers)

    ret.extend(get_holes_bbox(get_holes_center(centers)))
    ret.append(get_oscillator_bbox(p_oscillator))
    ret.append(get_bootsel_bbox(p_bootsel))
    ret.append(get_chip_bbox(p_chip))

    return ret


if __name__ == "__main__":
    # usb가 왼쪽 아래
    path3 = "img/20241108_173716.jpg"
    data3 = [
        {"class": "RASPBERRY PICO", "box": [74, 269, 241, 147]},
        {"class": "USB", "box": [78, 256, 104, 225]},
    ]

    # usb가 왼쪽
    path4 = "img/20241108_093331.jpg"
    data4 = [
        {"class": "RASPBERRY PICO", "box": [13, 259, 175, 191]},
        {"class": "USB", "box": [13, 240, 33, 216]},
    ]

    # usb가 왼쪽 위
    path5 = "img/20241108_093725.jpg"
    data5 = [
        {"class": "RASPBERRY PICO", "box": [50, 263, 209, 115]},
        {"class": "USB", "box": [60, 157, 90, 128]},
    ]

    # usb가 위
    path6 = "img/20241108_132649.jpg"
    data6 = [
        {"class": "RASPBERRY PICO", "box": [113, 242, 182, 81]},
        {"class": "USB", "box": [137, 104, 162, 81]},
    ]

    # usb가 오른쪽 위
    path7 = "img/20241108_093323.jpg"
    data7 = [
        {"class": "RASPBERRY PICO", "box": [54, 273, 220, 145]},
        {"class": "USB", "box": [185, 192, 216, 163]},
    ]

    # usb가 오른쪽
    path8 = "img/20241108_173747.jpg"
    data8 = [
        {"class": "RASPBERRY PICO", "box": [68, 271, 232, 187]},
        {"class": "USB", "box": [209, 232, 231, 207]},
    ]

    # usb가 오른쪽 아래
    path9 = "img/20241108_174343.jpg"
    data9 = [
        {"class": "RASPBERRY PICO", "box": [102, 256, 193, 90]},
        {"class": "USB", "box": [149, 256, 175, 233]},
    ]

    total_input_data = [data3, data4, data5, data6, data7, data8, data9]  # data9
    total_input_path = [path3, path4, path5, path6, path7, path8, path9]
    input_data = total_input_data[0]
    input_path = total_input_path[0]

    for i in range(7):
        input_data = total_input_data[i]
        input_path = total_input_path[i]
        # print(input_path)
        ret = predict_pos(input_data)
        print(ret)

        # img = np.zeros((512, 512, 3), np.uint8)
        img = cv2.imread(input_path)

        for item in input_data:
            cv2.rectangle(
                img,
                item["box"][:2],
                item["box"][2:],
                (0, 0, 255),
                3,
            )

        for item in ret:
            cv2.rectangle(
                img,
                item["box"][:2],
                item["box"][2:],
                (0, 255, 0),
                1,
            )

        cv2.imshow("title", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time.sleep(1.5)

    cv2.destroyAllWindows()


def start_end_to_start_wh(box):
    x1, y1, x2, y2 = box
    return {"coord": {"x": x1, "y": y1, "width": abs(x2 - x1), "height": abs(y2 - y1)}}
