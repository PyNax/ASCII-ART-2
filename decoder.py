import cv2
import threading
import queue
import time



class VideoDecoder:


    def __init__(
        self,
        path,
        buffer_seconds=3
    ):

        self.path = path

        self.buffer_seconds = buffer_seconds


        self.cap = cv2.VideoCapture(
            self.path
        )


        if not self.cap.isOpened():

            raise RuntimeError(
                "Cannot open video file"
            )


        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )


        if self.fps <= 0:

            self.fps = 30

        self.total_frames = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )


        if self.fps > 0:

            self.duration = (
                self.total_frames /
                self.fps
            )

        else:

            self.duration = 0


        self.width = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )


        self.height = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )


        buffer_size = int(
            self.fps *
            self.buffer_seconds
        )


        self.buffer = queue.Queue(
            maxsize=buffer_size
        )


        self.running = False

        self.thread = None


        self.frame_index = 0
        self.current_frame = 0



    def start(self):

        self.running = True


        self.thread = threading.Thread(
            target=self._decode_loop,
            daemon=True
        )


        self.thread.start()



    def _decode_loop(self):


        while self.running:


            # 버퍼가 가득 차면 기다림

            if self.buffer.full():

                time.sleep(0.01)

                continue



            ret, frame = self.cap.read()



            if not ret:

                self.running = False

                break



            timestamp = (
                self.frame_index /
                self.fps
            )


            self.frame_index += 1



            self.buffer.put(
                (
                    timestamp,
                    frame
                )
            )



        self.cap.release()



    def peek_frame(self):

        """
        버퍼의 첫 프레임 확인

        제거하지 않음
        """

        if self.buffer.empty():

            return None


        return self.buffer.queue[0]



    def pop_frame(self):

        """
        현재 프레임 제거
        """

        if self.buffer.empty():

            return None


        frame = self.buffer.get_nowait()

        self.current_frame += 1

        return frame



    def get_buffer_size(self):

        return self.buffer.qsize()



    def stop(self):


        self.running = False



        if self.thread:

            self.thread.join(
                timeout=1
            )



        if self.cap:

            self.cap.release()
    
    def get_duration(self):

        return self.duration
    
    def get_total_frames(self):

        return self.total_frames
    
    def get_current_frame(self):

        return self.current_frame
    
    def get_progress(self):

        if self.total_frames == 0:

            return 0

        return (
            self.current_frame /
            self.total_frames
        )