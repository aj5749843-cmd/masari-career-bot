import os,subprocess,sys
from playwright.sync_api import sync_playwright
SUB=3; FPS=30; R=FPS*SUB
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080})
    pg.goto('file://'+os.path.abspath('film.html')); pg.wait_for_function('window.ready===true')
    T=pg.evaluate('window.TOTAL'); n=int(T*R)
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(R),'-c:v','mjpeg','-i','-',
        '-vf',f'tmix=frames={SUB},framestep={SUB},format=yuv420p','-r',str(FPS),
        '-c:v','libx264','-crf','17','-preset','medium','-profile:v','high','film_noaudio.mp4'],stdin=subprocess.PIPE)
    for i in range(n):
        pg.evaluate(f'render({i/R})'); ff.stdin.write(pg.screenshot(type='jpeg',quality=93))
        if i%480==0: print(i,n,flush=True)
    ff.stdin.close(); ff.wait(); b.close()
print('done')
