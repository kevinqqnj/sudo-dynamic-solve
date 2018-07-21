from flask import Flask, render_template, request, current_app, jsonify
from flask_compress import Compress
from sudo_recur import Sudo
import logging, os, time
import requests, re

app = Flask(__name__)
compress = Compress()
compress.init_app(app)

# DEBUG INFO WARNING ERROR CRITICAL
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
# format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('sudoku.html')

@app.route('/solve', methods=['GET', 'POST'])
def solve_sudo():
    # {'puzzle': '8,0,0,0,0,0,0,0,0,0,0,3...'}
    # jsondata = request.get_json()
    # app = current_app._get_current_object()
    data = request.get_json().get('puzzle', '')
    app.logger.debug(f'puzzle: {data}')
    sudo = None
    try:
        data = [int(x) for x in data.split(',')]
        sudo = Sudo(data)
        sudo.sudo_solve_iter()
        return jsonify({
            'code': 'success',
            'result': sudo.value.tolist(),
            'guess_times': sudo.guess_times,
            'time_cost': sudo.time_cost,
            'guess_record': sudo.guess_record,
        })
    except:
        app.logger.error('cannot solve!', exc_info=1)
        return jsonify({
            'code': 'fail',
            'result': 'Not valid sudoku!',
            'guess_times': sudo.guess_times if sudo else 0,
            'time_cost': sudo.time_cost if sudo else 0
        })

@app.route('/fetch_tmda', methods=['GET', 'POST'])
def fetch_tmda():
    # http://cn.sudokupuzzle.org/online2.php
    # tm:题目 da:答案 nd：难度 tmxh：序号
    print(request, request.headers, 'args:', request.args, 'data', request.data)
    import random
    nd = request.args.get('level', -1)
    nd =  random.randint(0,4) if nd == -1 else nd
    tmda = [[],[],[],[],[],[],[],[],[]]
    try:
        # tmurl = '/online2.php?nd=' + tmnd 0-4 + '&y=' + yy + '&m=' + mm + '&d=' + dd
        url = f'http://cn.sudokupuzzle.org/online2.php?nd={nd}'
        app.logger.debug(f'Fetch on-line Sudo: {url}')
        rsp = requests.get(url)
        tmda_str = re.search(r"tmda='([\d]{81,})'", rsp.text)
        if tmda_str:
            tmda_str = tmda_str.group(1)[:81]
            [tmda[i//9].append(tmda_str[i]) for i in range(81)]
            rsp = jsonify({
                'code': 'success',
                'result': 'fetch OK',
                'tmda': tmda,
                'nd' : nd,
            })
        else:
            tmda_str = '008610930070000000000027050080940201709162005132805469204038006000056743307491500'
            [tmda[i//9].append(tmda_str[i]) for i in range(81)]
            rsp = jsonify({
                'code': 'fail',
                'result': 'Cannot fetch sudo puzzle, use default',
                'tmda': tmda,
                'nd': 1,
            })
    except:
        tmda_str = '008610930070000000000027050080940201709162005132805469204038006000056743307491500'
        tmda = [[],[],[],[],[],[],[],[],[]]
        [tmda[i//9].append(tmda_str[i]) for i in range(81)]
        app.logger.error('cannot fetch sodu!', exc_info=1)
        rsp = jsonify({
            'code': '500',
            'result': 'cannot fetch sodu！',
            'tmda': tmda,
            'nd': 1,
        })
    return rsp

if __name__ == '__main__':
    app.run()
