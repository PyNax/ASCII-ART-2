import cv2
import sys
import shutil


# 밝기 순서 ASCII 문자
ASCII_CHARS = (
    " .'`^\",:;Il!i~+_-?][}{1)(|\\/"
    "tfjrxnuvczXYUJCLQ0OZmwqpdbkhao"
    "*#MW&8%B@$"
)



class Renderer:


    def __init__(
        self,
        width=None,
        color=True
    ):

        self.width = width

        self.color = color

    def get_terminal_size(self):
        """
        현재 터미널 크기 반환
        (columns, rows)
        """
        return shutil.get_terminal_size(
            fallback=(120, 40)
        )
    
    def calculate_size(
        self,
        frame
    ):
        """
        현재 터미널 크기에 맞는
        ASCII 출력 크기 계산
        """

        frame_height, frame_width = frame.shape[:2]

        cols, rows = self.get_terminal_size()

        # 플레이바 및 디버그용으로 3줄 예약
        available_rows = max(rows - 3, 1)

        # 가로 기준
        width = cols

        # 문자 높이 보정
        height = int(
            frame_height *
            width /
            frame_width *
            0.45
        )

        # 화면보다 높으면 다시 계산
        if height > available_rows:

            scale = available_rows / height

            height = available_rows
            width = max(1, int(width * scale))

        return width, height



    def resize_frame(self, frame):

        """
        터미널 출력 크기에 맞게 축소
        """

        new_width = self.width
        new_height = None

        if new_width is None:

            new_width, new_height = self.calculate_size(frame)

        else:

            frame_height, frame_width = frame.shape[:2]

            new_height = int(
                frame_height *
                new_width /
                frame_width *
                0.45
            )

        new_height = max(new_height, 1)

        return cv2.resize(
            frame,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )


        resized = cv2.resize(
            frame,
            (
                self.width,
                new_height
            )
        )


        return resized



    def brightness_to_char(
        self,
        r,
        g,
        b
    ):

        """
        RGB 밝기 -> ASCII 문자
        """


        brightness = (
            0.2126 * r +
            0.7152 * g +
            0.0722 * b
        )


        index = int(
            brightness /
            255 *
            (len(ASCII_CHARS)-1)
        )


        return ASCII_CHARS[index]



    def color_char(
        self,
        char,
        r,
        g,
        b
    ):

        """
        ANSI TrueColor 적용
        """

        return (
            f"\033[38;2;{r};{g};{b}m"
            f"{char}"
            f"\033[0m"
        )



    def frame_to_ascii(
        self,
        frame
    ):


        frame = self.resize_frame(
            frame
        )


        # OpenCV BGR → RGB

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        lines = []


        height, width = frame.shape[:2]


        # 이중 반복문 방식

        for y in range(height):


            line = ""


            for x in range(width):


                r, g, b = frame[y][x]


                char = self.brightness_to_char(
                    r,
                    g,
                    b
                )


                if self.color:

                    char = self.color_char(
                        char,
                        int(r),
                        int(g),
                        int(b)
                    )


                line += char



            lines.append(
                line
            )


        return "\n".join(lines)



    def draw(
        self,
        frame
    ):

        """
        터미널 출력
        """

        ascii_frame = self.frame_to_ascii(
            frame
        )


        # 커서를 처음 위치로 이동
        # 화면 전체 삭제보다 빠름

        sys.stdout.write(
            "\033[H"
        )


        sys.stdout.write(
            ascii_frame
        )


        sys.stdout.flush()



    def clear(self):

        """
        종료 시 터미널 정리
        """

        sys.stdout.write(
            "\033[0m"
        )

        sys.stdout.write(
            "\033[2J"
        )

        sys.stdout.write(
            "\033[H"
        )

        sys.stdout.flush()