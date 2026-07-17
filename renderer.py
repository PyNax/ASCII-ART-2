import cv2
import sys


# 밝기 순서 ASCII 문자
ASCII_CHARS = (
    " .'`^\",:;Il!i~+_-?][}{1)(|\\/"
    "tfjrxnuvczXYUJCLQ0OZmwqpdbkhao"
    "*#MW&8%B@$"
)



class Renderer:


    def __init__(
        self,
        width=120,
        color=True
    ):

        self.width = width

        self.color = color



    def resize_frame(self, frame):

        """
        터미널 출력 크기에 맞게 축소
        """

        height, width = frame.shape[:2]


        # 터미널 문자는 세로가 더 길기 때문에 보정

        new_height = int(
            height *
            self.width /
            width *
            0.45
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