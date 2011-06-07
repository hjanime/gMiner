# Other modules #
from bbcflib.track import Track

################################################################################### 
def run_one(case, t):
    # Input tracks #
    for k,v in t['tracks'].items():
        if type(v) == list:
            t['tracks'][k] = iter(v)
        else:
            if t.get('fields') and t['fields'].get(k):
                with Track(v) as x:
                    t['tracks'][k] = iter(list(x.read('chr1', fields=t['fields'][k])))
            else:                                      
                with Track(v) as x:
                    t['tracks'][k] = iter(list(x.read('chr1')))
    # Input variables #
    kwargs = t.get('input', {})
    kwargs.update(t['tracks'])
    # Run it #
    case.assertEqual(list(t['fn'](**kwargs)), t['expected'])
