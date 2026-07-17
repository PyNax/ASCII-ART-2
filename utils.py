import os
import sys
import shutil
import platform


def enable_ansi():

    """
    Windows CMD에서 ANSI escape 활성화

    Windows Terminal은 기본 지원하지만
    CMD 환경을 위해 처리
    """

    if platform.system() == "Windows":

        os.system("")



def get_terminal_size():

    """
    현재 터미널 크기 반환

    return:
        width, height
    """

    size = shutil.get_terminal_size()

    return (
        size.columns,
        size.lines
    )



def clear_terminal():

    """
    터미널 화면 초기화
    """

    sys.stdout.write(
        "\033[2J"
    )

    sys.stdout.write(
        "\033[H"
    )

    sys.stdout.flush()



def hide_cursor():

    """
    재생 중 커서 숨김
    """

    sys.stdout.write(
        "\033[?25l"
    )

    sys.stdout.flush()



def show_cursor():

    """
    종료 후 커서 복구
    """

    sys.stdout.write(
        "\033[?25h"
    )

    sys.stdout.flush()



def move_cursor_home():

    """
    커서를 화면 맨 위로 이동
    """

    sys.stdout.write(
        "\033[H"
    )

    sys.stdout.flush()



def is_windows():

    """
    Windows 여부 확인
    """

    return (
        platform.system()
        ==
        "Windows"
    )



def safe_exit():

    """
    프로그램 종료 시 터미널 복구
    """

    show_cursor()

    clear_terminal()