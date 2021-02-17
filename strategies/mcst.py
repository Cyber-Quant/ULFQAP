from conf.conf import strategies_config_path
from strategies.common import get_latest_batch_data, get_liqa_share


class MCSTInfo:
    def __init__(self):
        self.name = '市场平均成本'
        self.desc = '''
        成交量(手)/当前流通股本(手)为权重成交额(元)/(100*成交量(手))的动态移动平均
        '''
        self.choose_flag = False
        self.watch_flag = False


class MCST:
    def __init__(self):
        pass

    def calc_batch_mcst(self, volumes, amount, code):
        mcst = []
        # FIXME get different liqa_share by date.
        liqa_share = get_liqa_share(code)
        for i, _ in enumerate(volumes):
            _mcst = (volumes[i] / liqa_share) * (amount[i] / volumes[i] / 100)
            mcst.append(_mcst)
        return mcst
