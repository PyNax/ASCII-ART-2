import argparse
import sys
import os
import signal
import threading
import time
import shutil

from decoder import VideoDecoder
from renderer import Renderer
from audio import AudioPlayer


# 프로그램 종료 신호
running = True


def signal_handler(sig, frame):
    global running

    print("\n\n[INFO] Stopping player...")

    running = False


signal.signal(signal.SIGINT, signal_handler)


def get_terminal_size():
    """
    현재 터미널 크기 반환
    """

    size = shutil.get_terminal_size()

    return size.columns, size.lines



def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Terminal ASCII Video Player"
    )

    parser.add_argument(
        "video",
        help="video file path"
    )

    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="disable audio playback"
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI color"
    )

    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="ASCII output width"
    )

    parser.add_argument(
        "--buffer",
        type=int,
        default=3,
        help="buffer seconds"
    )


    return parser.parse_args()



def main():

    global running

    args = parse_arguments()


    if not os.path.exists(args.video):

        print(
            f"[ERROR] File not found: {args.video}"
        )

        return


    # 터미널 크기 확인

    terminal_width, terminal_height = get_terminal_size()


    if args.width:

        ascii_width = args.width

    else:

        # 기본값:
        # 터미널 너비의 약 90%

        ascii_width = int(
            terminal_width * 0.9
        )


    print(
        "[INFO] Terminal size:",
        terminal_width,
        "x",
        terminal_height
    )

    print(
        "[INFO] ASCII width:",
        ascii_width
    )


    # 영상 디코더

    decoder = VideoDecoder(
        args.video,
        buffer_seconds=args.buffer
    )


    # 렌더러

    renderer = Renderer(
        width=ascii_width,
        color=not args.no_color
    )


    # 오디오

    audio = None

    # 디코더 시작

    decoder.start()



    # 첫 프레임 준비 대기

    print("[INFO] Preparing video buffer...")


    while decoder.get_buffer_size() < 2:

        time.sleep(0.01)



    print("[INFO] Video ready")



    # 오디오 시작

    audio = None


    if not args.no_audio:


        audio = AudioPlayer(
            args.video
        )


        audio.start()



        # 오디오 시작 대기

        while audio.get_position() <= 0:

            time.sleep(0.01)



    print("[INFO] Playback started")

    start_time = time.perf_counter()


    try:
        
        start_time = time.perf_counter()

        while running:


            # 오디오가 켜져 있으면
            # 오디오 시간을 기준으로 사용

            if audio:

                audio_time = audio.get_position()

            else:

                # 오디오가 없으면
                # 시스템 시간 사용

                audio_time = (
                    time.perf_counter()
                    -
                    start_time
                )



            frame_data = decoder.peek_frame()



            if frame_data is None:

                time.sleep(0.005)

                continue



            timestamp, frame = frame_data



            # ------------------------------------------------
            # 너무 늦은 프레임 제거
            # ------------------------------------------------

            if timestamp < audio_time - 0.10:


                decoder.pop_frame()

                continue



            # ------------------------------------------------
            # 출력할 시간이 된 프레임
            # ------------------------------------------------

            if timestamp <= audio_time + 0.02:


                decoder.pop_frame()


                renderer.draw(
                    frame
                )


            else:

                # 아직 시간이 안 됨

                time.sleep(
                    0.005
                )


    except Exception as e:

        print(
            "[ERROR]",
            e
        )


    finally:


        running = False


        decoder.stop()


        if audio:

            audio.stop()


        renderer.clear()



        print(
            "[INFO] Player closed"
        )



if __name__ == "__main__":

    main()