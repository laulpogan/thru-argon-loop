"""Render the saved scene without rebuilding imported assets or scatter."""
ROOT='/workspace/fullscene'
exec(compile(open(ROOT+'/src/ue_backend.py').read(),ROOT+'/src/ue_backend.py','exec'))
try:
    LES.load_level('/Game/Maps/Creek')
    for name in RUN.get('shots',[]):QUEUE.append(('Seq_'+name,RUN['out']+'/'+name,RUN.get('res',[1280,720]),RUN.get('temporal',4),CV))
    if RUN.get('walk'):QUEUE.append(('SeqWalk',RUN['out']+'/walk',RUN.get('walk_res',[1280,720]),1,CV))
    mark('saved_scene_loaded');nxt()
except Exception:
    open(ROOT+'/ue_error.txt','w').write(traceback.format_exc());unreal.SystemLibrary.quit_editor()
