import json
from Bot4z import Bot4P

class Adapter3P:
    def __init__(self):
        self.seat = 0
        self.old_oya = 0
        self.new_actor = [0, 0, 0, 0]
        self.N_obtaining = 0
        self.bot = None

    def self_install(self):
        self.install(Bot4P())
    
    def install(self, bot):
        self.bot = bot

    def react(self, event):
        if self.bot == None:
            raise Exception('No available bot installed in adapter')
        def patch_score(score3p, self_seat_idx, oya, tehais=['', '', '', '']):
            _tmp = sorted(score3p)
            _tmp = int((_tmp[-1] + _tmp[-2]) * 0.5)
            
            new_tehais = [['?'] * 13] * 4
            new_actor = [0, 0, 0, 0]
            score4p = [_tmp, _tmp, _tmp, _tmp]
            
            winds_3p = ['东', '南', '西']
            winds = '东南西北'
            winds_4p = ['东', '南', '西', '北']
            
            seat_to_wind = {}
            seat_to_wind_idx = {}
            for i in range(3):
                seat_idx = (oya + i) % 3
                seat_to_wind[seat_idx] = winds_3p[i]
                seat_to_wind_idx[seat_idx] = i
                
            self_wind_idx = seat_to_wind_idx[self_seat_idx]
            winds_4p[self_seat_idx] = winds[self_wind_idx]
            winds_4p[(self_seat_idx + 1) % 4] = winds[(self_wind_idx + 1) % 4]
            winds_4p[(self_seat_idx + 2) % 4] = winds[(self_wind_idx + 2) % 4]
            winds_4p[(self_seat_idx + 3) % 4] = winds[(self_wind_idx + 3) % 4]
            
            wind_to_4p_seat = {}
            for i in range(4):
                wind_to_4p_seat[winds_4p[i]] = i
            
            for i in range(3):
                wind = seat_to_wind[i]
                seat_4p = wind_to_4p_seat[wind]
                score4p[seat_4p] = score3p[i]
                new_tehais[seat_4p] = tehais[i]
                new_actor[i] = seat_4p
            
            new_oya_idx = wind_to_4p_seat['东']            
            return score4p, new_oya_idx, new_tehais, new_actor
        
        events = json.loads(event)
        if type(events) != list:
            events = [events]
        result_events = []
        for e in events:
            if len(events) > 100:
                break
            if 'actor' in e:
                e['actor'] = self.new_actor[e['actor']]
            if 'target' in e:
                e['target'] = self.new_actor[e['target']]
            
            # Memorize self seat
            if e['type'] == 'start_game':
                self.seat = e['id']
            
            elif e['type'] == 'start_kyoku':
                # E2 -> E3, E3 -> E4
                if e['kyoku'] != 1:
                    e['kyoku'] += 1                    
                self.old_oya = e['oya']
                
                patched = patch_score([x - 10000 for x in e['scores']], self.seat, self.old_oya, e['tehais'])
                e['scores'] = patched[0]
                e['oya'] = patched[1]
                e['tehais'] = patched[2]
                self.new_actor = patched[3]
                
                self.N_obtaining = 0
                for tile in e['tehais'][self.seat]:
                    self.N_obtaining += 1 if tile == 'N' else 0

                if e['dora_marker'] == '1m':
                    e['dora_marker'] = '8m'
                    
                north_seat = (e['oya'] + 3) % 4
                # Make dahai list to remove 2m~7m
                # Keep 8m for potential 1m dora markers
                result_events.append(e)
                print('\033[92m' + json.dumps(e) + '\033[0m')
                for _t in range(2, 8):
                    tile = str(_t) + 'm'
                    count = 4
                    for _ in range(count):
                        # 5mr
                        if _t == 5 and _ == 3:
                            tile += 'r'
                        who = north_seat
                        result_events.append({
                            'type': 'dahai',
                            'actor': who,
                            'pai': tile,
                            'tsumogiri': True
                        })
                continue

            elif e['type'] == 'dora':
                if e['dora_marker'] == '1m':
                    e['dora_marker'] = '8m'

            elif e['type'] == 'reach_accepted':
                if 'deltas' in e:
                    e['deltas'] = patch_score(e['deltas'], self.seat, self.old_oya)[0]
                if 'scores' in e:
                    e['scores'] = patch_score([x - 10000 for x in e['scores']], self.seat, self.old_oya)[0]

            # Simply set nukidora event to dahai
            elif e['type'] == 'nukidora':
                e['type'] = 'dahai'
                e['tsumogiri'] = False
                if e['pai'] == 'N' and e['actor'] == self.seat:
                    self.N_obtaining -= 1

            elif e['type'] == 'tsumo':
                if e['pai'] == 'N' and e['actor'] == self.seat:
                    self.N_obtaining += 1
                
            result_events.append(e)
            print('\033[93m模型决策：' + json.dumps(e) + '\033[0m')
            
        reaction = self.bot.react(json.dumps(result_events))
        
        if reaction == None:
            return None
        reaction = json.loads(reaction)
        if reaction['type'] == 'dahai' and self.N_obtaining > 0:
            return json.dumps({"type": "nukidora", "actor": 0, "pai": "N",
                               "meta": { "q_values": [-3, 4], "mask_bits": 1100585369600 } })

        if reaction['type'] == 'chi':
            reaction['type'] = 'none'
        reaction = json.dumps(reaction)
        return reaction

false = False
true = True
if __name__ == '__main__':
    bot = Adapter3P()
    bot.install(Bot4P())
    print(bot)

    events = {
  "is3p": false,
  "model": "v2-a",
  "events": [
    {
      "id": 2,
      "type": "start_game"
    },
    {"type":"start_kyoku","bakaze":"E","kyoku":2,"honba":0,"kyotaku":0,"oya":1,"dora_marker":"W","scores":[17000,18000,118000,0],
     "tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],
               ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
               ["6s","5p","1p","C","9p","6p","7p","1p","N","8s","6p","1m","E"],
               ["?","?","?","?","?","?","?","?","?","?","?","?","?"]]
     }, {'type':'nukidora','actor':0,'pai':'N'}
    
  ],
  "timestamp": "2025-09-22T15:03:13.873Z"
}

    res = bot.react(json.dumps(events['events']))
    print(res)
