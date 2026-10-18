import os,subprocess
from playwright.sync_api import sync_playwright
FPS=30
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080})
    pg.goto('file://'+os.path.abspath('promo_x.html')); pg.wait_for_function('window.ready===true')
    T=pg.evaluate('window.TOTAL'); n=int(T*FPS)
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-',
        '-i','audio_x.wav','-map','0:v','-map','1:a',
        '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-profile:v','high',
        '-af','loudnorm=I=-14:TP=-1.5:LRA=11','-c:a','aac','-b:a','192k','-ar','48000',
        '-shortest','-movflags','+faststart','masari_x.mp4'],stdin=subprocess.PIPE)
    for i in range(n):
        pg.evaluate(f'render({i/FPS})'); ff.stdin.write(pg.screenshot(type='jpeg',quality=95))
    ff.stdin.close(); ff.wait(); b.close()
print('frames',n)
