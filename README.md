# Vision AI와 기하학적 분석을 이용한 Raspberry Pi Pico 보드의 불량 검출

이 프로젝트는 라즈베리 파이 피코 보드의 품질 검사를 위한 자동화된 시스템을 제시합니다. Superb AI의 YOLOv8을 통한 객체 탐지 API를 활용하여 실제 보드 이미지에서 인식한 부품들의 위치들(1)과, 인식한 부품 중 두개의 위치로 계산한 검사할 모든 부품의 위치들(2)을 비교하여 정상 보드인지 판단합니다.

## 주요 기능
### 1. Vision AI 기반 부품 탐지(conveyor.py)
- Superb AI API를 통해 실시간으로 카메라 이미지에서 객체를 탐지합니다.
- GPU 없이 네트워크를 통해 이미지 상 부품의 위치 추론이 가능합니다.
- 6가지 부품 인식: RASPBERRY PICO, USB, CHIPSET, OSCILLATOR, BOOTSEL, HOLE

### 2. 부품의 기하학적 위치 계산(predict.py)
- USB와 RASPBERRY PICO 중심점을 기반으로 좌표계를 설정하고 각도 회전을 고려한 동적 부품 위치를 계산합니다.
- 수학적 변환을 통한 예상 바운딩박스 생성

### 3. 정상품 평가 및 검증(eval.py)
- 예상 위치(계산)와 Vision AI 탐지 위치(YOLOv8) 간 오차를 비교해 정상품 여부를 평가합니다.
- threshold 기본값은 8.1픽셀이며(테스트 환경에서 약 0.1인치) 허용 오차 범위 내 정상 판정

### 4. 시각적 시연
스크립트는 OpenCV를 사용하여 분석 결과를 시각화합니다.
- 파란색 바운딩박스: Vision AI가 탐지한 초기 랜드마크인 RASPBERRY PICO와 USB입니다.
- 빨간색 바운딩박스: 상세 추론 단계에서 Vision AI가 탐지한 부품들의 위치입니다.
- 초록색 바운딩박스: 기하학적 모델이 예측한 부품의 위치입니다.

정상적인 보드는 초록색 상자가 빨간색 상자 위에 거의 완벽하게 정렬된 모습으로 나타납니다. 만약 두 상자 간의 정렬이 크게 벗어난다면 잠재적인 결함을 의미합니다.

## 사용 기술
- 프로그래밍 언어: <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
- 수학 연산: <img src="https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white">
- Computer Vision: <img src="https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white">, Superb AI Vision API

## 활용 분야
- 제조업 품질 관리: 전자 보드 생산라인에서 실시간 검증
- 자동화 시스템: 대량 생산 환경에서의 자동 품질 검사

## 향후 개선 방향
- 모델 독립성 확보: 다른 Vision AI 제공업체로 쉽게 전환할 수 있도록 API 호출 로직을 리팩토링
- 설정 파일 도입: 하드코딩된 변수(API 키, 임계값, 비율 등)를 config.json 등의 파일로 옮겨 설정 편의성 향상
- 에러 분석 강화: 어떤 부품이 검사에 실패했는지, 허용 오차를 얼마나 벗어났는지 등 더 상세한 정보 제공

![alt text](https://github.com/idingg/pcb-qc-ai/blob/main/screenshot/1.png?raw=true)
![alt text](https://github.com/idingg/pcb-qc-ai/blob/main/screenshot/2.png?raw=true)
![alt text](https://github.com/idingg/pcb-qc-ai/blob/main/screenshot/3.png?raw=true)
![alt text](https://github.com/idingg/pcb-qc-ai/blob/main/screenshot/4.png?raw=true)
