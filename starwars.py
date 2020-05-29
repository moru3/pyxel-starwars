import pyxel
import random

class App:

    # パイプ定数
    NUM_OF_PIPE = 20
    PIPE_HEIGHT = 8
    PIPE_WIDTH = 40
    HIT_PIPE_INDEX = 2
    
    INIT_LIFE = 3
    SCORE_WIDTH = 5
    
    # ゲームステージ開始のゲームフレーム
    FIRST_STAGE = 100
    SECOND_STAGE = 1000
    THIRD_STAGE = 1500

    class Pipe:
        def __init__(self, x):
            self.x = x
            self.y = 0
        
        def add_idx(self):
            self.y += 8


    def __init__(self):
        pyxel.init(80, self.PIPE_HEIGHT*self.NUM_OF_PIPE, caption="Starwars the Death Star")

        pyxel.load("starwars.pyxres")

        # X-Wingの初期状態
        self.xwing_x = 32
        self.xwing_y = 120
        self.life = self.INIT_LIFE

        # 無敵開始フレームを入れる。Noneのときは無敵ではない
        self.muteki_frame = None
        
        # ブラスターの弾の座標（1つのみ存在、存在しない時はNone）
        self.blaster_x = None
        self.blaster_y = None

        # ボスのデススターコアの座標
        self.core_x = None
        self.core_y = None

        # クリア済みか
        self.cleared = False
        # 生存しているか
        self.player_is_alive = True

        self.pipe_list = [
            None, None, None, None, None,
            None, None, None, None, None,
            None, None, None, None, None,
            None, None, None, None, self.Pipe(80/2 - self.PIPE_WIDTH/2)
        ]

        # ゲームBGM
        pyxel.playm(0, loop=True)

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.player_is_alive and self.cleared == False:
            self.update_xwing()
            self.update_pipe()
            self.update_blaster()
            self.update_core()

    def update_xwing(self):
        # 接触してたら死
        hit_min = 0
        hit_max = pyxel.width - 16


        if self.pipe_list[self.HIT_PIPE_INDEX] != None:
            hit_min = self.pipe_list[self.HIT_PIPE_INDEX].x
            hit_max = self.pipe_list[self.HIT_PIPE_INDEX].x + self.PIPE_WIDTH
            if self.muteki_frame != None:
                if self.muteki_frame + 10 <= pyxel.frame_count:
                    self.muteki_frame = None
            else:
                if self.xwing_x < hit_min or (self.xwing_x + 16) > hit_max:
                    self.life = self.life - 1
                    self.muteki_frame = pyxel.frame_count
                    pyxel.play(3, 3, loop=False)
                    if self.life == 0:
                        self.player_is_alive = False
                        pyxel.play(3, 4, loop=False)
        
        # キーボード操作による移動
        # 画面から飛び出ない、パイプをはみ出さない
        if pyxel.btn(pyxel.KEY_LEFT):
            self.xwing_x = max(max(self.xwing_x - 2, 0), hit_min - 1)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.xwing_x = min(min(self.xwing_x + 2, pyxel.width - 16), hit_max - 16 + 1)

    def update_pipe(self):
        for idx in range(self.NUM_OF_PIPE):
            if idx < self.NUM_OF_PIPE - 1:
                tmp_pipe = self.pipe_list[idx+1]
                if self.pipe_list[idx+1] != None:
                    tmp_pipe.add_idx()
                self.pipe_list[idx] = tmp_pipe
            else:
                if pyxel.frame_count < self.FIRST_STAGE :
                    self.pipe_list[self.NUM_OF_PIPE-1] = self.Pipe(self.pipe_list[self.NUM_OF_PIPE-2].x)
                elif pyxel.frame_count >= self.FIRST_STAGE and pyxel.frame_count < self.SECOND_STAGE:
                    self.pipe_list[self.NUM_OF_PIPE-1] = self.create_next_pipe(self.pipe_list[self.NUM_OF_PIPE-2], 0.5)
                elif pyxel.frame_count >= self.SECOND_STAGE and pyxel.frame_count < self.THIRD_STAGE:
                    self.pipe_list[self.NUM_OF_PIPE-1] = self.create_next_pipe(self.pipe_list[self.NUM_OF_PIPE-2], 0.1)
                elif pyxel.frame_count >= self.THIRD_STAGE:
                    self.pipe_list[self.NUM_OF_PIPE-1] = None
    
    def create_next_pipe(self, prev_pipe, prob):
        move_pix = 4
        # 一定確率でそのまま前のやつを返す
        if random.random() < prob:
            return self.Pipe(prev_pipe.x)
        # 前のパイプの+-5pxでランダムでずらしたpipeを返す
        min = 0
        max = 80 - self.PIPE_WIDTH
        if prev_pipe.x-move_pix > min:
            min = prev_pipe.x-move_pix
        if prev_pipe.x+move_pix < max:
            max = prev_pipe.x+move_pix
        return self.Pipe(random.randint(min, max))

    def update_blaster(self):
        if self.blaster_x == None:
            if pyxel.btn(pyxel.KEY_SPACE):
                self.blaster_x = self.xwing_x
                self.blaster_y = 100
                pyxel.play(2, 2, loop=False)
        else:
            self.blaster_y -= 25
            if self.blaster_y < 0:
                self.blaster_x = None
                self.blaster_y = None
    
    def update_core(self):
        if self.cleared != False:
            return
        if pyxel.frame_count >= self.THIRD_STAGE + 50:
            if self.core_x == None:
                self.core_x = 40 - 16
                self.core_y = 0
                # ボス音
                pyxel.playm(1, loop=True)
            else:
                if self.blaster_x != None:
                    if self.blaster_x >= self.core_x and self.blaster_x + 16 <= self.core_x + 32 and self.blaster_y <= self.core_y:
                        self.cleared = True
                if self.core_y <= 50:
                    self.core_y += 5
        
    def draw(self):
        pyxel.cls(0)
        
        # pipes
        for pipe in self.pipe_list:
            if pipe != None:
                pyxel.blt(
                    pipe.x,
                    pipe.y,
                    0,
                    0,
                    32,
                    self.PIPE_WIDTH,
                    self.PIPE_HEIGHT,
                    0,
                )

        # xwing
        pyxel.blt(
            self.xwing_x,
            self.xwing_y,
            0,
            0 if self.player_is_alive else 16,
            0,
            16,
            16,
            0,
        )

        # blaster
        if self.blaster_x != None:
            pyxel.blt(
                self.blaster_x,
                self.blaster_y,
                0,
                48,
                0,
                16,
                16,
                0,
            )

        if self.core_x != None:
            pyxel.blt(
                self.core_x,
                self.core_y,
                0,
                32 if self.cleared else 0,
                64,
                32,
                32,
                0,
            )

        # score
        pyxel.blt(
            5,
            5,
            0,
            32,
            0,
            11,
            7,
            0,
        )
        pyxel.blt(
            7,
            12,
            0,
            self.SCORE_WIDTH * self.life,
            16,
            5,
            8,
            0,
        )

        # crear
        if self.cleared:
            pyxel.blt(
                40 - 16,
                25,
                0,
                0,
                96,
                32,
                16,
                0,
            )


App()