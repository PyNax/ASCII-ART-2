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
        default=0,
        help="ASCII output width"
    )

    parser.add_argument(
        "--buffer",
        type=int,
        default=3,
        help="buffer seconds"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="show debug information"
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
        width=None if args.width <= 0 else args.width,
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
        
            renderer.draw(frame)

            if audio:

                draw_progress_bar(
                    audio.get_position(),
                    decoder.get_duration()
                )

            if args.debug:

                draw_debug(
                    audio.get_position() if audio else 0,
                    timestamp,
                    decoder.get_buffer_size()
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

def format_time(seconds):

    seconds = int(seconds)

    m = seconds // 60

    s = seconds % 60

    return f"{m:02}:{s:02}"


import shutil

def draw_progress_bar(current, duration):

    cols, _ = shutil.get_terminal_size(
        fallback=(120, 40)
    )

    width = max(20, cols - 20)

    progress = 0

    if duration > 0:
        progress = current / duration

    progress = max(0.0, min(progress, 1.0))

    filled = int(progress * width)

    bar = (
        "█" * filled +
        "░" * (width - filled)
    )

    sys.stdout.write("\n")

    sys.stdout.write(
        f"{bar} "
        f"{format_time(current)}"
        f"/"
        f"{format_time(duration)}"
    )

    sys.stdout.flush()


def draw_debug(
    audio_time,
    frame_time,
    buffer_size
):

    sys.stdout.write("\n")

    sys.stdout.write(
        f"Audio : {audio_time:.3f}s\n"
    )

    sys.stdout.write(
        f"Frame : {frame_time:.3f}s\n"
    )

    sys.stdout.write(
        f"Buffer: {buffer_size}\n"
    )

    sys.stdout.flush()

if __name__ == "__main__":

    main()