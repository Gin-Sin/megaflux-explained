"""Check rendered media and typography records, not merely source declarations."""
from pathlib import Path
import json,subprocess,re

root=Path(__file__).resolve().parents[1]
assets=root/'site/assets'
data=json.loads((assets/'animation-audit.json').read_text())
slugs={'RoutingSkew':'routing-skew','ForwardPipeline':'forward-pipeline','BackwardReduction':'backward-reduction'}
assert {s['scene'] for s in data}==set(slugs)
for scene in data:
    file=assets/(slugs[scene['scene']]+'.mp4')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'],video['r_frame_rate'])==(1920,1080,'30/1')
    assert abs(float(probe['format']['duration'])-scene['duration'])<.15
    assert all(not p['overflow'] for p in scene['checkpoints'])
    assert len(scene['checkpoints'])>=4
    roles={item['role'] for item in scene['typography']}
    assert {'prose','title','math'}<=roles
    if scene['scene']=='ForwardPipeline':assert 'code' in roles
    expected={'prose':'CMU Serif','title':'CMU Serif','code':'JetBrains Mono','math':'LaTeX / Computer Modern'}
    for item in scene['typography']:
        assert item['font']==expected[item['role']]
        if item['role']=='prose':assert not re.search(r'\b(?:W[12]|E\d|dW\d)\b',item['source']),item
    print(f"PASS {scene['scene']}: 1080p/30 fps, {scene['duration']} s, roles {sorted(roles)}, no text outside reading frames")
