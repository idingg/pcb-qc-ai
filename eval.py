import math

threshold_px = 7


# 중심점 계산 함수
def get_center(box):
    x1, y1, x2, y2 = box
    return (x1 + x2) // 2, (y1 + y2) // 2


max = 0


# 일반 객체 거리 계산 및 출력 함수 (클래스가 "HOLE"이 아닌 객체만 계산)
def calculate_distances(predicted_objects, new_boxes):
    new_boxes_centers = {obj["class"]: get_center(obj["box"]) for obj in new_boxes}
    for predicted_obj in predicted_objects:
        predicted_class = predicted_obj["class"]
        # "HOLE" 클래스는 제외하고 계산
        if predicted_class != "HOLE":
            predicted_center = get_center(predicted_obj["box"])
            if predicted_class in new_boxes_centers:
                new_boxes_center = new_boxes_centers[predicted_class]
                distance = math.sqrt(
                    (predicted_center[0] - new_boxes_center[0]) ** 2
                    + (predicted_center[1] - new_boxes_center[1]) ** 2
                )
                # print(
                #     f"{predicted_class} predicted center: {predicted_center}, new_boxes center: {new_boxes_center}, distance: {distance:.2f} px"
                # )
                # 거리 조건 확인
                if distance >= threshold_px:
                    # print(
                    #     f"Fail: {predicted_class} distance is {distance:.2f} px (≥ threshold_px px)"
                    # )
                    return "Fail", distance
    return "Success", distance


# 가장 가까운 HOLE 찾기 함수
def find_closest_holes(new_boxes, reference_holes):
    global max
    new_boxes_holes = [
        get_center(obj["box"]) for obj in new_boxes if obj["class"] == "HOLE"
    ]
    for i, new_boxes_hole_center in enumerate(new_boxes_holes):
        min_distance = float("inf")
        for ref_label, ref_center in reference_holes.items():
            distance = math.sqrt(
                (new_boxes_hole_center[0] - ref_center[0]) ** 2
                + (new_boxes_hole_center[1] - ref_center[1]) ** 2
            )
            if distance < min_distance:
                min_distance = distance
                # print(
                #     f"new_boxes HOLE {i+1} center: {new_boxes_hole_center}, closest hole in reference distance: {min_distance:.2f} px"
                # )
        if min_distance >= threshold_px:
            # print(
            #     f"Fail: HOLE {i+1} closest distance is {min_distance:.2f} px (≥ threshold_px px)"
            # )
            return "Fail", min_distance
    return "Success", min_distance


# 거리 비교 및 성공 여부 확인 함수
def check_distances(boxes1, boxes2, threshold=7.0):
    global max, threshold_px
    max = 0
    threshold_px = threshold
    # 기준 HOLE 중심점 계산
    reference_holes = {
        f"HOLE_{i+1}": get_center(obj["box"])
        for i, obj in enumerate(boxes1)
        if obj["class"] == "HOLE"
    }
    # 일반 객체 거리 계산
    result, max = calculate_distances(boxes1, boxes2)
    if result == "Fail":
        return "Fail", max
    # HOLE 거리 계산
    result, max = find_closest_holes(boxes2, reference_holes)
    if result == "Fail":
        return "Fail", max
    # print("Success: All distances are below threshold_px px")
    return "Success", max


# 실행 부분
if __name__ == "__main__":
    pass
    # 데이터 정의
    # test1 = [
    # 	{"class": "RASPBERRY PICO", "score": 0.9817214012145996, "box": [61, 76, 149, 240]},
    # 	{"class": "USB", "score": 0.9771053791046143, "box": [80, 219, 107, 241]},
    # 	{"class": "CHIPSET", "score": 0.9164227843284607, "box": [93, 143, 119, 168]},
    # 	{"class": "OSCILLATOR", "score": 0.91110759973526, "box": [110, 127, 123, 137]},
    # 	{"class": "BOOTSEL", "score": 0.8878934979438782, "box": [103, 193, 115, 208]},
    # 	{"class": "HOLE", "score": 0.7713636755943298, "box": [95, 82, 102, 89]},
    # 	{"class": "HOLE", "score": 0.7433789372444153, "box": [129, 87, 136, 93]},
    # 	{"class": "HOLE", "score": 0.7062215805053711, "box": [109, 226, 116, 233]},
    # 	{"class": "HOLE", "score": 0.6256393790245056, "box": [75, 221, 82, 228]},
    # ]
    # new_boxes = [
    # 	{"class": "RASPBERRY PICO", "score": 0.9839377999305725, "box": [68, 84, 138, 244]},
    # 	{"class": "USB", "score": 0.9696625471115112, "box": [86, 226, 112, 246]},
    # 	{"class": "OSCILLATOR", "score": 0.9339773058891296, "box": [106, 131, 118, 141]},
    # 	{"class": "BOOTSEL", "score": 0.8906445503234863, "box": [105, 196, 117, 212]},
    # 	{"class": "CHIPSET", "score": 0.8333213925361633, "box": [91, 149, 116, 174]},
    # 	{"class": "HOLE", "score": 0.7666055560112, "box": [85, 88, 92, 94]},
    # 	{"class": "HOLE", "score": 0.6751471161842346, "box": [114, 230, 121, 237]},
    # 	{"class": "HOLE", "score": 0.610098659992218, "box": [79, 229, 86, 235]},
    # 	{"class": "HOLE", "score": 0.5473525524139404, "box": [120, 90, 127, 96]},
    # ]

    # result = check_distances(test1, new_boxes)
    # print(result)
