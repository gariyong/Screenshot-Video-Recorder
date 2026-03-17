import cv2 as cv
import datetime

# 카메라 설정
address = "rtsp://210.99.70.120:1935/live/cctv001.stream"
cap = cv.VideoCapture(address)

# 동영상 저장 설정
fourcc = cv.VideoWriter_fourcc(*"XVID")
fps = 20.0
# width/height 기본값 설정
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)) or 640
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)) or 480
out = None

# 상태 제어 변수
is_recording = False
is_gray = False  # 흑백 모드 변수


# 마우스 콜백 함수 (스크린샷)
def take_screenshot(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{now}.png"
        # param['frame']을 통해 현재 화면을 저장
        cv.imwrite(filename, param["current_frame"])
        print(f"스크린샷 저장 완료: {filename}")


# 윈도우 생성 및 마우스 콜백 연결
cv.namedWindow("Video Recorder")
state = {"current_frame": None}
cv.setMouseCallback("Video Recorder", take_screenshot, state)

print("프로그램 시작: Space(녹화), G(흑백), ESC(종료), 마우스클릭(캡처)")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("영상을 불러올 수 없습니다.")
        break

    # 흑백 필터 처리
    if is_gray:
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)  # 녹화(3채널)를 위해 다시 변환

    # 실시간 타임스탬프 표시
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv.putText(
        frame,
        now_str,
        (10, height - 20),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv.LINE_AA,
    )

    # 마우스 핸들러에 현재 프레임 전달
    state["current_frame"] = frame.copy()

    # Record 모드 표시 및 저장
    if is_recording:
        cv.circle(frame, (30, 30), 10, (0, 0, 255), -1)
        cv.putText(frame, "REC", (50, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if out is not None:
            out.write(frame)

    cv.imshow("Video Recorder", frame)

    key = cv.waitKey(1) & 0xFF

    # 키 입력 처리
    if key == ord(" "):  # 녹화 토글
        is_recording = not is_recording
        if is_recording:
            out = cv.VideoWriter("recorded_video.avi", fourcc, fps, (width, height))
            print("녹화 시작")
        else:
            if out is not None:
                out.release()
                out = None
            print("녹화 중지 및 저장 완료")

    elif key == ord("g") or key == ord("G"):  # 흑백 모드 토글
        is_gray = not is_gray
        print(f"필터 변경: {'흑백' if is_gray else '컬러'}")

    elif key == 27:  # ESC 종료
        break

# 리소스 해제
cap.release()
if out is not None:
    out.release()
cv.destroyAllWindows()
