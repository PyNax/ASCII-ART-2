import pygame
import threading
import os
import tempfile
import time

from moviepy import VideoFileClip



class AudioPlayer:


    def __init__(
        self,
        video_path
    ):

        self.video_path = video_path

        self.audio_file = None


        self.running = False

        self.thread = None


        self.start_time = None



    def extract_audio(self):

        """
        영상에서 wav 추출
        """

        temp_dir = tempfile.gettempdir()


        self.audio_file = os.path.join(
            temp_dir,
            "ascii_player_audio.wav"
        )


        clip = VideoFileClip(
            self.video_path
        )


        if clip.audio is None:

            clip.close()

            return False



        clip.audio.write_audiofile(
            self.audio_file,
            logger=None
        )


        clip.close()


        return True



    def start(self):

        self.running = True


        self.thread = threading.Thread(
            target=self._play,
            daemon=True
        )


        self.thread.start()



    def _play(self):


        try:


            if not self.extract_audio():

                return



            pygame.mixer.init()



            pygame.mixer.music.load(
                self.audio_file
            )


            pygame.mixer.music.play()



            # 실제 재생 시작 시간 기록

            self.start_time = time.perf_counter()



            while self.running:


                time.sleep(
                    0.05
                )



        except Exception as e:


            print(
                "[Audio Error]",
                e
            )



    def get_position(self):

        """
        현재 오디오 시간 반환

        단위: 초
        """


        if self.start_time is None:

            return 0



        if not pygame.mixer.music.get_busy():

            return 0



        return (
            time.perf_counter()
            -
            self.start_time
        )



    def stop(self):


        self.running = False



        try:

            pygame.mixer.music.stop()

            pygame.mixer.quit()


        except:

            pass



        if self.thread:

            self.thread.join(
                timeout=1
            )



        if self.audio_file:

            try:

                os.remove(
                    self.audio_file
                )

            except:

                pass