"""Extract reading holds and transition samples for visual review."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
import argparse
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--draft',action='store_true');args=parser.parse_args()
folder=root/('media/preview' if args.draft else 'site/assets')
out=root/'test-results/animation-review';out.mkdir(parents=True,exist_ok=True)
scenes={'RoutingSkew':'routing-skew','ForwardPipeline':'forward-pipeline','BackwardReduction':'backward-reduction'}
for scene,slug in scenes.items():
 data=json.loads((root/'media/audit'/f'{scene}.json').read_text())
 holds=[p['time']-.15 for p in data['checkpoints']]
 # Include transition interiors, not only final frames.
 times=sorted(set([1.2,*holds,*[(a+b)/2 for a,b in zip(holds,holds[1:])]]))
 images=[]
 for i,t in enumerate(times):
  file=out/f'{slug}-{i:02}.png'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(folder/f'{slug}.mp4'),'-frames:v','1',str(file)],check=True)
  im=Image.open(file).convert('RGB').resize((640,360),Image.Resampling.LANCZOS);tile=Image.new('RGB',(640,389),'#eff2ed');tile.paste(im,(0,29));ImageDraw.Draw(tile).text((12,8),f'{scene} / {t:.1f} s',fill='#16252f');images.append(tile)
 sheet=Image.new('RGB',(1280,389*((len(images)+1)//2)),'white')
 for i,tile in enumerate(images):sheet.paste(tile,((i%2)*640,(i//2)*389))
 sheet.save(out/f'{slug}-contact.png')
 print(scene, data['duration'],'seconds;',len(times),'frames reviewed')
